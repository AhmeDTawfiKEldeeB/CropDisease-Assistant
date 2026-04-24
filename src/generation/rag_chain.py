import argparse
import os
import re
import sys
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from openai import OpenAI
from openai import AuthenticationError
from sentence_transformers import SentenceTransformer
from src.config import settings
from src.infrastructure.qdrant.vectorstore import QdrantDBProvider

load_dotenv(".env")

traceable = lambda **kwargs: lambda f: f

if os.getenv("LANGSMITH_TRACING") == "true":
    try:
        from langsmith import traceable
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
        os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
        os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "CropDisease")
    except ImportError:
        pass

SYSTEM_PROMPT = (
    "You are an agricultural expert. "
    "Answer only from the provided context. "
    "Be concise. "
    "If context is insufficient, say so."
)

DEFAULT_ANSWER = "I'm not certain about that. You can ask about crop diseases, symptoms, causes, or treatments."

_embedder_cache: Optional[SentenceTransformer] = None


def _get_embedder() -> SentenceTransformer:
    global _embedder_cache
    if _embedder_cache is None:
        _embedder_cache = SentenceTransformer(settings.huggingface.model_name)
    return _embedder_cache


def _validate_groq_key(api_key: str) -> None:
    if not api_key:
        raise ValueError("GROQ__API_KEY is required")
    lower_key = api_key.lower()
    if "replace-with" in lower_key or lower_key in {"changeme", "placeholder"}:
        raise ValueError("GROQ__API_KEY is a placeholder. Set a valid key.")


def _extract_context(points: List[Any]) -> List[Dict[str, Any]]:
    contexts = []
    for point in points:
        payload = getattr(point, "payload", {}) or {}
        text = payload.get("text", "")
        metadata = payload.get("metadata", {}) or {}
        contexts.append({
            "text": str(text),
            "metadata": metadata,
            "score": float(getattr(point, "score", 0.0) or 0.0),
        })
    return contexts


def _build_prompt(question: str, contexts: List[Dict[str, Any]]) -> str:
    context_lines = []
    for idx, item in enumerate(contexts, start=1):
        disease = item["metadata"].get("disease_name", "unknown")
        section = item["metadata"].get("section_title", "unknown")
        context_lines.append(f"[{idx}] {disease} - {section}: {item['text'][:500]}")

    return f"Context:\n{chr(10).join(context_lines)}\n\nQuestion: {question}"


def _clean_answer(text: str) -> str:
    if not text:
        return DEFAULT_ANSWER
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    cleaned = re.sub(r"```", "", cleaned)
    return cleaned.strip() or DEFAULT_ANSWER


@traceable(run_type="tool", project_name="CropDisease")
def ask_llm(question: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    api_key = settings.groq.api_key.strip()
    base_url = settings.groq.base_url.strip()
    _validate_groq_key(api_key)

    client = OpenAI(base_url=base_url, api_key=api_key)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    try:
        response = client.chat.completions.create(
            model=settings.groq.model,
            temperature=settings.groq.temperature,
            messages=messages,
        )
    except AuthenticationError:
        raise RuntimeError("Groq authentication failed. Check GROQ__API_KEY.")

    answer = _clean_answer(response.choices[0].message.content if response.choices else "")
    return {"answer": answer, "model": settings.groq.model, "contexts": [], "retrieval_error": ""}


@traceable(run_type="chain", project_name="CropDisease")
def ask_rag(question: str, top_k: int = 5, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    api_key = settings.groq.api_key.strip()
    base_url = settings.groq.base_url.strip()
    _validate_groq_key(api_key)

    if not settings.qdrant.url or not settings.qdrant.api_key:
        raise ValueError("QDRANT__URL and QDRANT__API_KEY are required")

    embedder = _get_embedder()
    query_vector = embedder.encode(question, convert_to_numpy=True, normalize_embeddings=True).tolist()

    provider = QdrantDBProvider(url=settings.qdrant.url, api_key=settings.qdrant.api_key)
    points = []
    retrieval_error = ""
    try:
        provider.connect()
        points = provider.search_by_vector(
            collection_name=settings.qdrant.collection_name,
            vector=query_vector,
            limit=top_k,
        )
    except Exception as exc:
        retrieval_error = str(exc)
    finally:
        provider.disconnect()

    contexts = _extract_context(points)
    valid_contexts = [c for c in contexts if c.get("score", 0) > 0.5]

    if not valid_contexts:
        return {"answer": DEFAULT_ANSWER, "model": settings.groq.model, "contexts": [], "retrieval_error": retrieval_error}

    client = OpenAI(base_url=base_url, api_key=api_key)
    prompt = _build_prompt(question, valid_contexts)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    try:
        response = client.chat.completions.create(
            model=settings.groq.model,
            temperature=settings.groq.temperature,
            max_tokens=settings.groq.max_tokens,
            messages=messages,
        )
    except AuthenticationError:
        raise RuntimeError("Groq authentication failed. Check GROQ__API_KEY.")

    answer = _clean_answer(response.choices[0].message.content if response.choices else "")
    return {
        "answer": answer,
        "model": settings.groq.model,
        "contexts": valid_contexts,
        "retrieval_error": retrieval_error,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the RAG chain using Groq LLM")
    parser.add_argument("question", type=str, help="User question")
    parser.add_argument("--top-k", type=int, default=5, help="Number of retrieved chunks")
    parser.add_argument("--llm-only", action="store_true", help="Skip Qdrant retrieval")
    args = parser.parse_args()

    result = ask_llm(question=args.question) if args.llm_only else ask_rag(question=args.question, top_k=args.top_k)

    if result.get("retrieval_error"):
        print(result["retrieval_error"], file=sys.stderr)
    print(result["answer"])


if __name__ == "__main__":
    main()