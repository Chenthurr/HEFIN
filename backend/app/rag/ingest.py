"""
Ingestion pipeline for the medical knowledge layer.

Usage:
    python -m app.rag.ingest --file path/to/who_guideline.txt --source "WHO"
"""
import argparse
import asyncio
import uuid
from qdrant_client.http import models as qmodels
from app.rag.embeddings import EMBEDDING_DIM, embed_texts
from app.rag.retriever import retriever

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start = end - overlap
    return [c for c in chunks if c.strip()]

async def ingest_file(path: str, source: str, language: str = "en") -> int:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    chunks = chunk_text(text)
    if not chunks:
        return 0
    vectors = embed_texts(chunks)
    await retriever.ensure_collection(vector_size=EMBEDDING_DIM)
    points = [qmodels.PointStruct(id=str(uuid.uuid4()), vector=vector, payload={"text": chunk, "source": source, "language": language}) for chunk, vector in zip(chunks, vectors)]
    await retriever.client.upsert(collection_name=retriever.collection, points=points)
    return len(points)

def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest a document into the HEFIN knowledge base")
    parser.add_argument("--file", required=True, help="Path to a plain-text source file")
    parser.add_argument("--source", required=True, help="Source label, e.g. 'WHO', 'PubMed'")
    parser.add_argument("--language", default="en")
    args = parser.parse_args()
    count = asyncio.run(ingest_file(args.file, args.source, args.language))
    print(f"Ingested {count} chunks from {args.file} (source={args.source})")

if __name__ == "__main__":
    main()
