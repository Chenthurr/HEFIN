from dataclasses import dataclass
from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

from app.core.config import get_settings


@dataclass(frozen=True)
class RetrievedChunk:
    text: str
    source: str
    score: float


class QdrantRetriever:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = AsyncQdrantClient(url=settings.qdrant_url)
        self.collection = settings.qdrant_collection

    async def ensure_collection(self, vector_size: int = 384) -> None:
        """Create the configured collection when the knowledge base is first seeded."""
        try:
            collections = await self.client.get_collections()
            names = {item.name for item in collections.collections}
            if self.collection not in names:
                await self.client.create_collection(
                    collection_name=self.collection,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE,
                    ),
                )
        except Exception:
            # Startup must not depend on Qdrant being available; ingestion will
            # surface a real configuration/connectivity error when requested.
            return

    async def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        source_filter: str | None = None,
    ) -> list[RetrievedChunk]:
        query_filter = None
        if source_filter:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="source",
                        match=models.MatchValue(value=source_filter),
                    )
                ]
            )

        try:
            results = await self.client.search(
                collection_name=self.collection,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=top_k,
                with_payload=True,
            )
        except Exception:
            # A missing/unavailable vector store should not crash the API.
            return []

        chunks: list[RetrievedChunk] = []
        for result in results:
            payload: dict[str, Any] = result.payload or {}
            text = str(payload.get("text") or payload.get("content") or "").strip()
            source = str(payload.get("source") or "Unknown source").strip()
            if text:
                chunks.append(
                    RetrievedChunk(text=text, source=source, score=float(result.score))
                )
        return chunks


retriever = QdrantRetriever()
