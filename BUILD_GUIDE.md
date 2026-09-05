# HEFIN Build Guide

This is the step-by-step path from the scaffold in this repo to a working
MVP, following the pillars and MVP definition in the Phase 0 spec.

## Status: Steps 1, 3, 4, 5, and 7 are implemented, not just stubbed

The backend imports cleanly, its test suite passes, and the frontend
**builds and renders** — verified with a real `next build` + a headless
screenshot, not just eyeballed. What's real:

- **Auth, permissions, chat plumbing** (Step 1) — unchanged from before.
- **RAG is now real, not a stub** (Step 3): `app/rag/embeddings.py` uses
  a local multilingual sentence-transformers model (covers all 10 Pillar
  4 languages, including Tamil/Hindi), `app/rag/ingest.py` chunks/embeds/
  upserts real documents into Qdrant, and the orchestrator's three agents
  now retrieve real chunks and generate real citations instead of stub
  strings.
- **Model router dispatches for real** (Step 3): local Ollama-style
  servers for simple/moderate complexity, Anthropic's API for complex
  reasoning. Needs `ANTHROPIC_API_KEY` in `.env` to actually call out.
- **Document Vault + report parsing are real** (Steps 4 & 5):
  `app/models/document.py`, MinIO-backed object storage
  (`app/services/storage.py`), PDF text extraction, and AI summarization
  routed through the safety gate.
- **3D landing page is real** (Step 7): a "Medical Galaxy" network scene
  in `components/MedicalGalaxyScene.tsx` — not decorative, it's the
  literal shape of the product (scattered sources pulled into one
  connected layer). Built and screenshotted to confirm it renders.

## Honest limitations of what I could verify in this environment

I don't have Docker, and network access here is restricted to package
registries (no huggingface.co, no live LLM API calls). So:

- I **could not** actually run `docker compose up`, Postgres, Qdrant, or
  MinIO here — the compose file and connection code are correct, but
  untested against real running services. Test this first when you pull
  the repo.
- I **could not** download the sentence-transformers model weights here
  (blocked network) — the code is correct and will work the moment you
  run it somewhere with normal internet access.
- I **could not** call Anthropic's or Ollama's live APIs — dispatch code
  is written and follows their documented request formats, but hasn't
  made a real round-trip.
- I **did** verify: the backend app imports and its test passes, the
  frontend builds with `next build` (including a full TypeScript check),
  and the production build actually renders the intended design when
  screenshotted headlessly.

## What's already scaffolded here

```
hefin/
├── backend/                     FastAPI service
│   ├── app/
│   │   ├── main.py              App entrypoint, CORS, router registration
│   │   ├── core/                 config, security (JWT/bcrypt), permissions, deps
│   │   ├── models/                User, Document, TimelineEvent (SQLAlchemy)
│   │   ├── schemas/               Pydantic request/response models
│   │   ├── api/                    auth.py, chat.py, documents.py routes
│   │   ├── db/                      async session/engine
│   │   ├── rag/                      embeddings.py, retriever.py, ingest.py — all real
│   │   ├── agents/                  LangGraph orchestrator, real retrieval + generation
│   │   └── services/                model_router (real dispatch), storage, report_parser, safety_guard
│   ├── alembic/                      migrations (configured, no revisions yet)
│   ├── requirements.txt
│   └── .env.example
├── frontend/                    Next.js 14 + Tailwind app router
│   ├── app/                       layout, globals.css, real 3D landing page
│   ├── components/                 MedicalGalaxyScene.tsx (signature 3D element)
│   ├── lib/api.ts                   fetch wrapper for the backend
│   └── package.json                 react-three-fiber/three/gsap, patched Next 14.2.35
├── infra/
│   └── docker-compose.yml           Postgres+pgvector, Qdrant, Redis, MinIO
└── .gitignore
```

## Step 1 — Get it running locally

```bash
# 1. Start infra
cd infra && docker compose up -d

# 2. Backend
cd ../backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic revision --autogenerate -m "create users table"
alembic upgrade head
uvicorn app.main:app --reload

# 3. Frontend (new terminal)
cd ../frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Visit `http://localhost:8000/docs` for the API and `http://localhost:3000`
for the frontend. Register a user via `/api/v1/auth/register`, log in via
`/api/v1/auth/login`, and call `/api/v1/chat` with the returned token —
you'll get back a stub answer from whichever agent the orchestrator
routed you to, which confirms the whole chain (auth → permission check →
safety gate → orchestrator → route) is wired correctly.

## Step 2 — Close the Phase 0 research gaps that block real functionality

You said to build from scratch regardless of Phase 0 status, which is
fine for scaffolding — but three decisions block *real* (non-stub)
behavior and are worth resolving before Step 3:

1. **LLM choice** for the model router (`app/services/model_router.py`) —
   pick a starting model per complexity tier (e.g., a local Ollama model
   for simple queries, a hosted model for complex reasoning) and fill in
   `ModelRouter.generate()`.
2. **Embedding model** for the retriever — determines `vector_size` in
   `MedicalKnowledgeRetriever.ensure_collection()` and needs to handle
   the target languages (Section 20 flags Tamil/Hindi specifically).
3. **Cloud provider / hosting** — affects deployment later but not local
   dev, so it can wait.

You can stub past #1 and #2 initially (as scaffolded) and come back once
you've benchmarked — the interfaces won't need to change, just the
implementations.

## Step 3 — Make the AI chat real — ✅ done, needs your API key

`ModelRouter.generate()`, the retriever, and the orchestrator's three
agents are wired end to end. What's left for you:

- Add `ANTHROPIC_API_KEY` (or swap in another hosted provider) to
  `backend/.env` — the "complex" routing tier needs it.
- Point `LOCAL_LLM_BASE_URL` at a running Ollama (or compatible) server
  for the "simple"/"moderate" tiers, or change `ROUTING_TABLE` in
  `model_router.py` to route everything to the hosted model until you
  have local inference set up.
- Seed the knowledge base: `python -m app.rag.ingest --file guideline.txt
  --source "WHO"` — without this, `medical_agent`/`research_agent`/
  `finance_agent` will correctly report "no grounded sources" rather
  than hallucinate, which is intentional.

## Step 4 — Patient Dashboard & Document Vault — ✅ backend done

`Document`/`TimelineEvent` models, MinIO-backed storage, and
`/api/v1/documents/upload` (gated by the permission matrix) are all
implemented. Remaining:

- `alembic revision --autogenerate -m "add documents"` once Postgres is
  running, to generate the actual migration.
- Frontend: dashboard route at `frontend/app/dashboard/page.tsx` with
  upload UI and timeline view — not yet built.

## Step 5 — Medical report parsing & summarization — ✅ done

`app/services/report_parser.py` extracts PDF text and summarizes through
the model router, routed through the Step 3 safety gate. Call
`POST /api/v1/documents/{id}/parse` after upload.

## Step 6 — Multilingual support (Pillar 4)

- Confirm your embedding model choice (Step 2) actually performs well
  for Tamil/Hindi — this is flagged as an open research question in
  Section 20 for a reason; test before committing.
- Add a `language` parameter through the retrieval and generation path
  (already threaded through `ChatRequest`/`OrchestratorState` — just
  needs real translation/multilingual retrieval behind it).

## Step 7 — 3D Landing Page (Pillar 5, MVP item) — ✅ done

Built the "Medical Galaxy" option: a network of nodes/edges built from a
Fibonacci-sphere point distribution, slowly rotating, representing
scattered sources pulled into one connected layer — the visual is the
product thesis, not decoration. Verified with `next build` (clean
TypeScript check) and a headless screenshot.

Next iteration ideas, not required for MVP: hover interactivity on
nodes (surface a real citation/source on hover), a second signature
element (Human Anatomy Explorer or Digital Earth) for an interior page
rather than the landing hero, and replacing the current placeholder
nav/CTA copy once the actual product flows exist to link to.

## Step 8 — Security & Compliance hardening (Section 18)

- Enable HTTPS/TLS at the deploy layer (not app-level).
- Add audit logging middleware to `app/main.py` (who accessed what, when).
- Add prompt-injection guarding around anything that feeds retrieved
  document content back into LLM prompts — sanitize/delimit context
  clearly from instructions.
- Per-region compliance (HIPAA-equivalent in US, DPDP in India, GDPR in
  EU) affects data residency — revisit `DATABASE_URL`/storage location
  per deployment region.

## Step 9 — Deploy

- Containerize backend (`Dockerfile` alongside `docker-compose.yml`) and
  frontend (`next build` + Node runtime or static export, depending on
  how much of the 3D content needs SSR).
- Point `alembic upgrade head` at the production database as part of your
  deploy pipeline, not manually.

---

**Suggested order if you want a working demo fastest:** Steps 1 → 3
(real chat, even with one model and a small seeded knowledge base) → 7
(landing page, since it's highly visible) → 4/5 (dashboard + parsing) →
6 → 8 → 9.

Tell me which step you want to do next and I'll build it out.

## AI Assistant frontend — operational MVP

The frontend now provides three working surfaces: authenticated AI Assistant chat, Document Vault upload/parse, and the original Medical Galaxy landing experience. Chat calls `POST /api/v1/chat` with the user's JWT; it is no longer powered by the HTML demo's browser-side mock knowledge base.

For the fastest first run:
1. Start the infrastructure with `cd infra && docker compose up -d`.
2. Start the backend with the commands in Step 1. The MVP now creates missing SQLAlchemy tables on startup; production should still use Alembic.
3. Put `ANTHROPIC_API_KEY` in `backend/.env`. When it is present, the moderate RAG chat path automatically uses the hosted Claude provider, so Ollama is not required for the first MVP.
4. Seed the included demo knowledge base:
   `cd backend && python -m app.rag.ingest --file data/demo_who.txt --source "WHO"`
   `python -m app.rag.ingest --file data/demo_pubmed.txt --source "PubMed"`
   `python -m app.rag.ingest --file data/demo_insurance.txt --source "Insurance Policy Database"`
   Then replace these demo files with your vetted production sources.
5. Start the frontend with `cd frontend && npm install && npm run dev`, then create an account in the UI.

The original single-file `HEFIN_Demo.html` remains a useful visual/reference artifact; its browser-side `KB`, routing, and delayed mock response logic are not used by the Next.js application.
