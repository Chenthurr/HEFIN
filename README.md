# HEFIN — Healthcare Financial Intelligence Network

HEFIN is an evidence-grounded AI assistant for healthcare, research, and insurance workflows. It combines specialist routing, retrieval-augmented generation (RAG), citations, a safety gate, and a Document Vault in one application.

## Features

- **AI Assistant** — authenticated chat with medical, research, and finance routing
- **Grounded RAG** — retrieves evidence before generation and returns source citations
- **Safety Gate** — keeps the assistant educational and prevents autonomous diagnosis/prescription behavior
- **Document Vault** — upload PDF/TXT documents, extract text, and generate educational summaries
- **Multilingual foundation** — multilingual embedding model and requested-language responses
- **Model routing** — hosted Anthropic inference when configured, with local Ollama fallback
- **Infrastructure** — PostgreSQL/pgvector, Qdrant, Redis, and MinIO via Docker Compose

## Repository layout

```text
HEFIN/
├── backend/      # FastAPI API, auth, agents, RAG, model router, documents
├── frontend/     # Next.js 14 + TypeScript + Tailwind UI
├── infra/        # Docker Compose infrastructure
├── LICENSE       # MIT License
└── README.md
```

## Quick start

### 1. Start infrastructure

```bash
cd infra
docker compose up -d
```

### 2. Configure the backend

```bash
cd ../backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env` and configure at least:

```env
SECRET_KEY=change-this-in-production
ANTHROPIC_API_KEY=your-key
```

The backend defaults to the local Docker services defined in `infra/docker-compose.yml`.

### 3. Seed the demo knowledge base

```bash
python -m app.rag.ingest --file data/demo_who.txt --source "WHO"
python -m app.rag.ingest --file data/demo_pubmed.txt --source "PubMed"
python -m app.rag.ingest --file data/demo_insurance.txt --source "Insurance Policy Database"
```

### 4. Start the API

```bash
uvicorn app.main:app --reload
```

API health check: `http://localhost:8000/health`

### 5. Start the frontend

```bash
cd ../frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## AI architecture

```text
User
  ↓
Next.js AI Assistant
  ↓
FastAPI /api/v1/chat
  ↓
Authentication + permissions
  ↓
Safety gate
  ↓
LangGraph intent router
  ├── Medical agent
  ├── Research agent
  └── Finance agent
          ↓
      Qdrant RAG
          ↓
      Model Router
      ├── Anthropic
      └── Ollama fallback
          ↓
   Grounded answer + citations
```

## Safety

HEFIN is designed as an educational information assistant, not a clinician or autonomous medical decision-maker. Do not use it as a substitute for professional medical, legal, financial, or insurance advice. Production deployments require appropriate security, privacy, clinical governance, monitoring, and regulatory review.

## Security

Never commit API keys, JWT secrets, database passwords, or production credentials. Use environment variables or a managed secret store.

## License

MIT License. See `LICENSE`.
