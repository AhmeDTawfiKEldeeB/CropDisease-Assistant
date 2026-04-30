from functools import lru_cache
from typing import Any, Dict, List
from sentence_transformers import SentenceTransformer
from src.config import settings
from src.infrastructure.qdrant.vectorstore import QdrantDBProvider

@lru_cache(maxsize=1)
def _embedder() -> SentenceTransformer:
    return SentenceTransformer(settings.huggingface.model_name)


def retrieve(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    if not query or not query.strip():
        raise ValueError("query is required")

    provider = QdrantDBProvider(url=settings.qdrant.url, api_key=settings.qdrant.api_key)
    provider.connect()

    try:
        dense_vector = _embedder().encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )[0].tolist()

        points = provider.hybrid_search(
            collection_name=settings.qdrant.collection_name,
            query_text=query,
            dense_vector=dense_vector,
            limit=top_k,
        )

        results = []
        seen_texts = set()
        for point in points:
            payload = getattr(point, "payload", {}) or {}
            text = str(payload.get("text", "")).strip()
            if not text or text in seen_texts:
                continue
            seen_texts.add(text)
            metadata = payload.get("metadata", {}) or {}
            score = float(getattr(point, "score", 0.0) or 0.0)
            results.append({
                "text": text,
                "metadata": metadata,
                "score": score,
            })

        return results[:top_k]
    finally:
        provider.disconnect()