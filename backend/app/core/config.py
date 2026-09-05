from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "HEFIN"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "change_me"

    # Database
    database_url: str = "postgresql+asyncpg://hefin:hefin_dev_password@localhost:5432/hefin"

    # Vector DB
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "hefin_medical_knowledge"

    # Cache
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # LLM providers
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    openrouter_api_key: str | None = None
    local_llm_base_url: str = "http://localhost:11434"

    # Object storage (MinIO locally / S3-compatible in prod)
    minio_endpoint: str = "http://localhost:9000"
    minio_access_key: str = "hefin"
    minio_secret_key: str = "hefin_dev_secret"

    # CORS
    allowed_origins: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
