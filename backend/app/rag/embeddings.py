"""
Embedding service backing the RAG retriever. Uses a local multilingual
sentence-transformers model so ingestion/retrieval work offline and free
of per-call API cost — appropriate given Pillar 4 (10 target languages,
including Tamil/Hindi flagged as an open research question in Section 20).

Swap `MODEL_NAME` if benchmarking turns up a better multilingual model.
"""
from functools import lru_cache
from sentence_transformers import SentenceTransformer

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIM = 384

@lru_cache
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)

def embed_texts(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return vectors.tolist()

def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
