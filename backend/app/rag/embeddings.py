"""Lightweight, production-safe embedding service for HEFIN RAG.

The Render free tier has a 512 MiB memory limit, so importing PyTorch and a
sentence-transformers model is not suitable for the API process. When an
OpenAI key is configured we use a 384-dimensional text-embedding-3-small
vector. Without a key, a deterministic multilingual character-ngram vector
keeps ingestion/retrieval operational and dependency-free; it can be replaced
by a managed embedding provider without changing the RAG interface.
"""
from __future__ import annotations

import hashlib
import math
import re
from functools import lru_cache

import httpx

from app.core.config import get_settings

EMBEDDING_DIM = 384
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"


def _hashed_embedding(text: str) -> list[float]:
    """Create a deterministic multilingual character-ngram embedding."""
    vector = [0.0] * EMBEDDING_DIM
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    padded = f"  {normalized}  "
    ngrams = [padded[i : i + 3] for i in range(max(0, len(padded) - 2))]
    if not ngrams:
        return vector

    for gram in ngrams:
        digest = hashlib.blake2b(gram.encode("utf-8"), digest_size=8).digest()
        index = int.from_bytes(digest[:4], "big") % EMBEDDING_DIM
        sign = 1.0 if digest[4] & 1 else -1.0
        vector[index] += sign

    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def _openai_embeddings(texts: list[str], api_key: str) -> list[list[float]]:
    response = httpx.post(
        "https://api.openai.com/v1/embeddings",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": OPENAI_EMBEDDING_MODEL,
            "input": texts,
            "dimensions": EMBEDDING_DIM,
        },
        timeout=30.0,
    )
    response.raise_for_status()
    data = response.json()["data"]
    return [item["embedding"] for item in sorted(data, key=lambda item: item["index"])]


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    api_key = get_settings().openai_api_key
    if api_key:
        try:
            return _openai_embeddings(texts, api_key)
        except (httpx.HTTPError, KeyError, TypeError, ValueError):
            # Keep the API usable if the optional provider is unavailable.
            pass

    return [_hashed_embedding(text) for text in texts]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
