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

LANGSMITH_AVAILABLE = False
traceable = lambda **kwargs: lambda f: f

if os.getenv("LANGSMITH_TRACING") == "true":
    print("LangSmith tracing enabled, importing...", file=sys.stderr)
    try:
        from langsmith import traceable
        print("LangSmith imported successfully!", file=sys.stderr)
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
        os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
        os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "CropDisease")
        LANGSMITH_AVAILABLE = True
    except ImportError as e:
        print(f"LangSmith import failed: {e}", file=sys.stderr)


CONCISE_RULES = (
    "You are an agricultural expert. "
    "Provide direct, factual answers based only on the context given. "
    "Do NOT repeat information. "
    "Do NOT infer or soften statements. "
    "Answer concisely in the same language as the user's question."
)

GREETINGS = {
    "hi", "hello", "hey", "hi there", "hello!", "hey!", "greetings",
    "hi!", "مرحبا", "السلام عليكم", "السلام عليكم", "مرحبا"
}

NEED_MORE_INFO = {
    "what is this", "what is that", "what disease", "identify this", "what's wrong",
    " diagnose", "my plant", "my crop", "this plant", "that disease", "help me",
    "help identify", "what's this", "disease?", " diagnose?", "identify"
}

DEFAULT_ANSWER = "I’m not certain about that. You can ask about symptoms, causes, or treatment and I’ll try to help."
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
    if (
        "replace-with" in lower_key
        or "your-groq-api-key" in lower_key
        or lower_key in {"changeme", "placeholder"}
    ):
        raise ValueError(
            "GROQ__API_KEY in .env is a placeholder. "
            "Set a real Groq key from dashboard before running."
        )


def _extract_context(points: List[Any]) -> List[Dict[str, Any]]:
    contexts: List[Dict[str, Any]] = []
    for point in points:
        payload = getattr(point, "payload", {}) or {}
        text = payload.get("text", "")
        metadata = payload.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}

        contexts.append(
            {
                "text": str(text),
                "metadata": metadata,
                "score": float(getattr(point, "score", 0.0) or 0.0),
            }
        )
    return contexts


def _detect_language(text: str) -> str:
    text_lower = text.lower()
    arabic_chars = set('ايةبتثجحخدذرزسشصضطظعغفقكلمنهوي')
    if any(c in arabic_chars for c in text_lower):
        return "ar"
    return "en"


def _build_prompt(question: str, contexts: List[Dict[str, Any]], history: Optional[List[Dict[str, str]]] = None) -> str:
    lang = _detect_language(question)
    lang_instruction = "Respond in Arabic." if lang == "ar" else "Respond in English."

    parts: List[str] = [
        f"Language: {lang}",
        lang_instruction,
    ]

    if history:
        history_text = []
        for msg in history[-4:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")[:100]
            history_text.append(f"{role}: {content}")
        if history_text:
            parts.append("Conversation:\n" + "\n".join(history_text))

    if not contexts:
        return DEFAULT_ANSWER
    else:
        context_lines: List[str] = []
        for idx, item in enumerate(contexts, start=1):
            disease = item["metadata"].get("disease_name", "unknown")
            section = item["metadata"].get("section_title", "unknown")
            context_lines.append(
                f"[{idx}] {disease} - {section}: {item['text'][:600]}"
            )
        parts.append("Knowledge base:\n" + "\n\n".join(context_lines))

    parts.append(f"Question: {question}")
    parts.append("Answer helpfully in the same language as the question.")

    return "\n\n".join(parts)


def _sanitize_answer(text: str) -> str:
    if not text:
        return DEFAULT_ANSWER

    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    cleaned = cleaned.strip()

    lines = [line.rstrip() for line in cleaned.splitlines() if line.strip()]
    if lines:
        return "\n".join(lines[:6]).strip()

    return cleaned or DEFAULT_ANSWER


def _check_special_cases(question: str) -> Optional[Dict[str, Any]]:
    q = question.lower().strip()

    if q in GREETINGS or q.startswith(("hi ", "hello ", "hey ")):
        return {
            "answer": DEFAULT_ANSWER,
            "model": settings.groq.model,
            "contexts": [],
            "retrieval_error": "",
        }

    if any(pattern in q for pattern in NEED_MORE_INFO):
        return {
            "answer": DEFAULT_ANSWER,
            "model": settings.groq.model,
            "contexts": [],
            "retrieval_error": "",
        }

    return None


@traceable(run_type="tool", project_name="CropDisease")
def ask_llm(question: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    api_key = settings.groq.api_key.strip()
    base_url = settings.groq.base_url.strip()

    _validate_groq_key(api_key)

    client = OpenAI(base_url=base_url, api_key=api_key)

    messages: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": "You are a helpful agricultural disease expert. " + CONCISE_RULES,
        }
    ]

    if history:
        for msg in history[-6:]:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

    messages.append({"role": "user", "content": question})

    try:
        response = client.chat.completions.create(
            model=settings.groq.model,
            temperature=settings.groq.temperature,
            messages=messages,
        )
    except AuthenticationError as exc:
        raise RuntimeError(
            "Groq authentication failed (401). "
            "Update GROQ__API_KEY in .env with a valid key."
        ) from exc

    answer = _sanitize_answer(response.choices[0].message.content if response.choices else "")
    return {
        "answer": answer,
        "model": settings.groq.model,
        "contexts": [],
        "retrieval_error": "",
    }


@traceable(run_type="chain", project_name="CropDisease")
def ask_rag(question: str, top_k: int = 5, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    special = _check_special_cases(question)
    if special:
        return special

    api_key = settings.groq.api_key.strip()
    base_url = settings.groq.base_url.strip()

    _validate_groq_key(api_key)
    if not settings.qdrant.url or not settings.qdrant.api_key:
        raise ValueError("QDRANT__URL and QDRANT__API_KEY are required")

    embedder = _get_embedder()
    query_vector = embedder.encode(
        question,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).tolist()

    points: List[Any] = []
    retrieval_error = ""
    provider = QdrantDBProvider(url=settings.qdrant.url, api_key=settings.qdrant.api_key)
    try:
        provider.connect()
        points = provider.search_by_vector(
            collection_name=settings.qdrant.collection_name,
            vector=query_vector,
            limit=top_k,
        )
    except Exception as exc:
        retrieval_error = f"Qdrant error: {exc}"
    finally:
        provider.disconnect()

    contexts = _extract_context(points)
    valid_contexts = [c for c in contexts if c.get("score", 0) > 0.5]

    if not valid_contexts:
        return {
            "answer": DEFAULT_ANSWER,
            "model": settings.groq.model,
            "contexts": [],
            "retrieval_error": retrieval_error,
        }

    contexts = valid_contexts
    messages: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": "You are an agricultural disease expert. " + CONCISE_RULES,
        }
    ]

    if history:
        for msg in history[-6:]:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

    prompt = _build_prompt(question, contexts)
    messages.append({"role": "user", "content": prompt})

    client = OpenAI(base_url=base_url, api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=settings.groq.model,
            temperature=settings.groq.temperature,
            max_tokens=settings.groq.max_tokens,
            messages=messages,
        )
    except AuthenticationError as exc:
        raise RuntimeError(
            "Groq authentication failed (401). "
            "Update GROQ__API_KEY in .env with a valid key."
        ) from exc

    answer = _sanitize_answer(response.choices[0].message.content if response.choices else "")
    return {
        "answer": answer,
        "model": settings.groq.model,
        "contexts": contexts,
        "retrieval_error": retrieval_error,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the RAG chain using Groq LLM")
    parser.add_argument("question", type=str, help="User question")
    parser.add_argument("--top-k", type=int, default=5, help="Number of retrieved chunks")
    parser.add_argument(
        "--llm-only",
        action="store_true",
        help="Skip Qdrant retrieval and call Groq LLM directly",
    )
    args = parser.parse_args()

    if args.llm_only:
        result = ask_llm(question=args.question)
    else:
        result = ask_rag(question=args.question, top_k=args.top_k)

    if result.get("retrieval_error"):
        print(result["retrieval_error"], file=sys.stderr)
    print(result["answer"])


if __name__ == "__main__":
    main()