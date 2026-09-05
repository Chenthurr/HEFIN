# HEFIN Backend

FastAPI backend for the Healthcare Financial Intelligence Network (HEFIN).

## Responsibilities

- JWT authentication and permission checks
- Safety-gated AI chat
- LangGraph intent routing
- Grounded RAG retrieval with Qdrant
- Model routing to hosted/local LLM providers
- Document upload, storage, parsing and educational summarization
- PostgreSQL persistence

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Start PostgreSQL, Qdrant, Redis and MinIO from `../infra/docker-compose.yml` first.

API docs: `http://localhost:8000/docs`
