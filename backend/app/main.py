from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, chat, documents
from app.core.config import get_settings
from app.db.session import Base, engine
from app.models import document, user  # noqa: F401

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Healthcare Financial Intelligence Network — API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(documents.router)


@app.on_event("startup")
async def create_tables_for_mvp() -> None:
    # Keeps the local MVP runnable on a fresh Postgres database. For production,
    # use Alembic migrations as described in BUILD_GUIDE.md.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def close_database() -> None:
    await engine.dispose()


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}
