# HEFIN Infrastructure

Local development infrastructure for HEFIN.

## Services

- PostgreSQL 16 with pgvector
- Qdrant vector database
- Redis cache
- MinIO object storage

## Start

```bash
docker compose up -d
```

Stop with:

```bash
docker compose down
```

Persistent data is stored in Docker volumes defined by the compose file.
