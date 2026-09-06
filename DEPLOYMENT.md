# HEFIN Deployment Guide

This guide covers the production-shaped Docker setup added to the repository. It is intended for a first deploy of the operational AI assistant MVP.

## 1. Prerequisites

- Docker Engine with Docker Compose v2
- A public hostname for the frontend and API (or an ingress/reverse proxy)
- A model-provider API key such as Anthropic
- TLS/HTTPS termination at the edge

## 2. Configure production secrets

From `infra/`, copy `.env.prod.example` to `.env` and replace all placeholders. Never commit the production `.env` file.

The important values are:

- `SECRET_KEY`: long random application signing key
- `POSTGRES_PASSWORD`: database password
- `MINIO_ROOT_PASSWORD`: object-storage password
- `NEXT_PUBLIC_API_URL`: browser-reachable backend URL
- `ALLOWED_ORIGINS`: exact frontend origin(s), comma-separated
- one of the supported model-provider keys for AI generation

## 3. Build and start

```bash
cd infra
docker compose -f docker-compose.prod.yml --env-file .env up -d --build
```

The frontend listens on port 3000 and the API on port 8000 by default. Put both behind HTTPS in production rather than exposing the application ports directly to the internet.

## 4. Seed the knowledge base

The AI assistant is RAG-grounded. After the backend is running, seed the included demo sources from inside the backend container:

```bash
docker compose -f docker-compose.prod.yml exec backend python -m app.rag.ingest demo_who.txt
docker compose -f docker-compose.prod.yml exec backend python -m app.rag.ingest demo_pubmed.txt
docker compose -f docker-compose.prod.yml exec backend python -m app.rag.ingest demo_insurance.txt
```

If the ingest module expects a different invocation in a later revision, follow the current `BUILD_GUIDE.md` instructions.

## 5. Health check

```bash
curl http://localhost:8000/health
```

Expected response includes `"status":"ok"`.

## 6. Database migrations

The MVP startup path creates missing SQLAlchemy tables automatically. For production schema evolution, run Alembic migrations and then remove that compatibility behavior when the deployment process is fully migration-driven.

## 7. CI

`.github/workflows/ci.yml` runs backend compilation/tests and a frontend production build on pushes and pull requests targeting `main`.

The repository currently does not contain a committed frontend `package-lock.json`, so CI uses `npm install`. Once a lockfile is committed, change the frontend CI step to `npm ci` for reproducible installs.

## 8. Security checklist

- Use HTTPS everywhere.
- Set a unique, high-entropy `SECRET_KEY`.
- Restrict `ALLOWED_ORIGINS` to trusted frontend origins.
- Keep Postgres, Qdrant, Redis, and MinIO on the private Docker network.
- Do not commit `.env` files or API keys.
- Replace demo knowledge with reviewed, authoritative sources before real clinical use.
- Keep the safety gate and educational/non-diagnostic positioning enabled.
- Back up Postgres, Qdrant, and MinIO volumes.
