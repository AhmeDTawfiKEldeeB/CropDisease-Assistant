import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
from uuid import NAMESPACE_URL, uuid5

from sentence_transformers import SentenceTransformer

from src.config import settings
from src.infrastructure.qdrant.vectorstore import QdrantDBProvider


def _resolve_data_path(data_path: str | None) -> Path:
    if data_path:
        return Path(data_path)
    return Path(settings.qdrant.data_json_path)


def _load_records(path: Path) -> List[Dict[str, Any]]:
    resolved = path if path.is_absolute() else Path.cwd() / path
    if not resolved.exists():
        raise FileNotFoundError(f"Data file not found: {resolved}")

    raw = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Input JSON must be a list of records")
    return raw


def _prepare_records(records: List[Dict[str, Any]]) -> Tuple[List[str], List[Dict[str, Any]], List[str]]:
    texts: List[str] = []
    payloads: List[Dict[str, Any]] = []
    ids: List[str] = []

    for idx, record in enumerate(records):
        if not isinstance(record, dict):
            continue

        text = str(record.get("text", "")).strip()
        if not text:
            continue

        metadata = record.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}

        texts.append(text)
        payloads.append({"text": text, "metadata": metadata})
        ids.append(str(uuid5(NAMESPACE_URL, f"disease-record:{idx}")))

    return texts, payloads, ids


def build_index(data_path: str | None = None, recreate_collection: bool = True) -> int:
    if not settings.qdrant.url:
        raise ValueError("QDRANT__URL is required")
    if not settings.qdrant.api_key:
        raise ValueError("QDRANT__API_KEY is required")

    provider = QdrantDBProvider(url=settings.qdrant.url, api_key=settings.qdrant.api_key)
    provider.connect()

    try:
        input_path = _resolve_data_path(data_path)
        records = _load_records(input_path)

        embedder = SentenceTransformer(settings.huggingface.model_name)
        embedding_size = int(embedder.get_sentence_embedding_dimension())

        provider.create_collection(
            collection_name=settings.qdrant.collection_name,
            embedding_size=embedding_size,
            do_reset=recreate_collection,
        )

        texts, payloads, ids = _prepare_records(records)
        if not texts:
            return 0

        vectors = embedder.encode(
            texts,
            batch_size=settings.qdrant.upload_batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).tolist()

        provider.client.upload_collection(
            collection_name=settings.qdrant.collection_name,
            vectors=vectors,
            payload=payloads,
            ids=ids,
            batch_size=settings.qdrant.upload_batch_size,
            wait=True,
        )
        return len(vectors)
    finally:
        provider.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Qdrant index from cleaned disease JSON")
    parser.add_argument(
        "--data-path",
        default=None,
        help="Path to input JSON file (defaults to QDRANT__DATA_JSON_PATH)",
    )
    parser.add_argument(
        "--no-recreate",
        action="store_true",
        help="Do not recreate collection if it already exists",
    )
    args = parser.parse_args()

    inserted = build_index(data_path=args.data_path, recreate_collection=not args.no_recreate)
    print(
        f"Indexed {inserted} records into collection '{settings.qdrant.collection_name}' "
        f"using multilingual model '{settings.huggingface.model_name}'"
    )


if __name__ == "__main__":
    main()