from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
from uuid import uuid4

from openai import OpenAI
from sentence_transformers import SentenceTransformer

from src.config import settings
from src.infrastructure.qdrant.vectorstore import QdrantDBProvider

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a precise crop disease assistant.

Rules:
- Answer in the same language as the user's latest question.
- Answer only the latest question.
- Use only the supplied knowledge-base context for crop disease facts.
- Use history only to understand references like "it", "this disease", or "علاجه".
- Keep the answer short and direct.
- Do not add extra sections, tables, or steps unless the user asks for them.
- Do not invent diagnoses, pesticides, chemicals, dosages, or treatments.
- If the context is not enough, say you do not have enough information to answer confidently.
- If a disease name is broad and appears in more than one crop, give the shared meaning first, then mention that crop-specific details may differ.
"""

NO_CONTEXT = "No relevant context was retrieved. Do not answer from outside knowledge."
MAX_HISTORY = 10
MAX_CONTEXT_CHARS = 10000

INTENT_SECTIONS = {
    "treatment": ("treatment", "management", "control", "prevention"),
    "symptoms": ("symptoms", "signs", "simple explanation", "overview"),
    "cause": ("cause", "pathogen", "spread", "disease cycle", "overview"),
    "definition": ("simple explanation", "overview", "pathogen"),
}

ARABIC_BLACK_ROT = ("العفن الاسود", "العفن الأسود", "عفن اسود", "عفن أسود")


def _read_dotenv() -> Dict[str, str]:
    values: Dict[str, str] = {}
    env_path = Path.cwd() / ".env"
    if not env_path.exists():
        return values
    for raw_line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


@lru_cache(maxsize=1)
def _dotenv() -> Dict[str, str]:
    return _read_dotenv()


def _env(name: str, default: str = "") -> str:
    return os.getenv(name) or _dotenv().get(name, default)


def _setup_tracing() -> bool:
    enabled = (
        bool(settings.langsmith.tracing)
        or _env("LANGSMITH_TRACING").lower() in {"1", "true", "yes", "on"}
        or _env("LANGSMITH_TRACING_V2").lower() in {"1", "true", "yes", "on"}
    )
    api_key = settings.langsmith.api_key or _env("LANGSMITH_API_KEY") or _env("LANGSMITH__API_KEY")
    if not enabled or not api_key:
        return False

    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_TRACING_V2"] = "true"
    os.environ["LANGSMITH_API_KEY"] = api_key
    os.environ.setdefault("LANGSMITH_PROJECT", _env("LANGSMITH_PROJECT", "CropDisease"))
    os.environ.setdefault("LANGSMITH_ENDPOINT", _env("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"))
    return True


TRACING_ENABLED = _setup_tracing()


@lru_cache(maxsize=1)
def _trace_client():
    if not TRACING_ENABLED:
        return None
    try:
        from langsmith.client import Client

        return Client(
            api_key=os.environ["LANGSMITH_API_KEY"],
            api_url=os.environ["LANGSMITH_ENDPOINT"],
            auto_batch_tracing=False,
        )
    except Exception:
        logger.exception("LangSmith is configured but could not be initialized.")
        return None


class TraceSpan:
    def __init__(
        self,
        name: str,
        run_type: str,
        inputs: Dict[str, Any],
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.id = str(uuid4())
        self.name = name
        self.run_type = run_type
        self.inputs = inputs
        self.parent_id = parent_id
        self.metadata = metadata or {}
        self.outputs: Dict[str, Any] = {}
        self.client = _trace_client()

    def __enter__(self) -> "TraceSpan":
        if self.client:
            try:
                self.client.create_run(
                    id=self.id,
                    name=self.name,
                    run_type=self.run_type,
                    inputs=self.inputs,
                    project_name=os.environ.get("LANGSMITH_PROJECT", "CropDisease"),
                    parent_run_id=self.parent_id,
                    extra={"metadata": self.metadata},
                )
            except Exception:
                logger.exception("Failed to create LangSmith run: %s", self.name)
                self.client = None
        return self

    def __exit__(self, exc_type: Any, exc: Any, _tb: Any) -> None:
        if not self.client:
            return
        try:
            self.client.update_run(
                self.id,
                end_time=datetime.now(timezone.utc),
                outputs=self.outputs or None,
                error=str(exc) if exc else None,
            )
        except Exception:
            logger.exception("Failed to update LangSmith run: %s", self.name)


def _text(value: Any, limit: int = 4000) -> str:
    return str(value or "").replace("\x00", " ").strip()[:limit].strip()


def _norm(value: Any) -> str:
    text = str(value or "").lower().strip()
    text = re.sub(r"[\s_\-–—]+", " ", text)
    text = re.sub(r"[^\w\u0621-\u064a ]+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _name_keys(name: str) -> List[str]:
    keys = {_norm(name)}
    for sep in (" - ", "-", " – ", " — "):
        if sep in name:
            left, right = [part.strip() for part in name.split(sep, 1)]
            if left and right:
                keys.add(_norm(f"{left} {right}"))
                keys.add(_norm(f"{right} {left}"))
                keys.add(_norm(left))
    return [key for key in keys if key]


def _has_arabic(text: str) -> bool:
    return bool(re.search(r"[\u0600-\u06ff]", text))


@lru_cache(maxsize=1)
def _embedder() -> SentenceTransformer:
    return SentenceTransformer(settings.huggingface.model_name)


def _openai_client() -> OpenAI:
    if not settings.groq.api_key:
        raise ValueError("GROQ__API_KEY is required")
    return OpenAI(api_key=settings.groq.api_key, base_url=settings.groq.base_url)


def _qdrant() -> QdrantDBProvider:
    if not settings.qdrant.url or not settings.qdrant.api_key:
        raise ValueError("QDRANT__URL and QDRANT__API_KEY are required")
    return QdrantDBProvider(settings.qdrant.url, settings.qdrant.api_key)


def _load_json(path: str) -> List[Dict[str, Any]]:
    file_path = Path(path)
    if not file_path.is_absolute():
        file_path = Path.cwd() / file_path
    if not file_path.exists():
        return []
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        logger.exception("Failed to load JSON file: %s", file_path)
        return []


@lru_cache(maxsize=1)
def _kb() -> List[Dict[str, Any]]:
    return _load_json(settings.qdrant.data_json_path)


@lru_cache(maxsize=1)
def _name_map() -> Dict[str, Dict[str, str]]:
    mapping: Dict[str, Dict[str, str]] = {}
    for record in [*_kb(), *_load_json("chatbot/diseases.json")]:
        meta = record.get("metadata") or {}
        if not isinstance(meta, dict):
            continue
        en = _text(meta.get("disease_name"), 200)
        ar = _text(meta.get("disease_name_ar"), 200)
        if not en:
            continue
        names = {"en": en, "ar": ar}
        for name in (en, ar):
            for key in _name_keys(name):
                mapping[key] = names
    for alias in ARABIC_BLACK_ROT:
        mapping[_norm(alias)] = {"en": "Black Rot", "ar": alias}
    return mapping


def _augment_meta(meta: Any) -> Dict[str, Any]:
    meta = meta if isinstance(meta, dict) else {}
    disease = _text(meta.get("disease_name"), 200)
    if not disease or meta.get("disease_name_ar"):
        return dict(meta)

    for key in _name_keys(disease):
        names = _name_map().get(key)
        if names:
            updated = dict(meta)
            updated.setdefault("disease_name", names["en"])
            if names.get("ar"):
                updated.setdefault("disease_name_ar", names["ar"])
            return updated
    return dict(meta)


def _history(history: Optional[Sequence[Dict[str, str]]]) -> List[Dict[str, str]]:
    role_map = {"ai": "assistant", "bot": "assistant", "human": "user"}
    clean: List[Dict[str, str]] = []
    for item in history or []:
        if not isinstance(item, dict):
            continue
        role = role_map.get(str(item.get("role", "")).lower(), str(item.get("role", "")).lower())
        content = _text(item.get("content"), 1200)
        if role in {"user", "assistant"} and content:
            clean.append({"role": role, "content": content})
    return clean[-MAX_HISTORY:]


def _matches_name(key: str, text: str) -> bool:
    if key in text:
        return True
    stop = {"in", "on", "of", "the", "في", "على", "من", "ال"}
    key_tokens = [part for part in key.split() if part not in stop]
    text_tokens = {part for part in text.split() if part not in stop}
    return bool(key_tokens) and all(part in text_tokens for part in key_tokens)


def _mapped_names(text: str) -> List[str]:
    normalized = _norm(text)
    found: List[str] = []
    for key, names in _name_map().items():
        if _matches_name(key, normalized):
            found.extend(name for name in names.values() if name)
    if "black rot" in normalized or any(_norm(alias) in normalized for alias in ARABIC_BLACK_ROT):
        found.extend(["Black Rot", "Black Rot - Apple", "Black Rot - Grape", *ARABIC_BLACK_ROT])
    return list(dict.fromkeys(found))


def _intent(question: str) -> str:
    q = _norm(question)
    if any(word in q for word in ("treatment", "treat", "control", "manage", "cure", "علاج", "مكافحة")):
        return "treatment"
    if any(word in q for word in ("symptom", "sign", "look like", "اعراض", "أعراض", "علامات", "شكل")):
        return "symptoms"
    if any(word in q for word in ("cause", "pathogen", "caused by", "سبب", "المسبب")):
        return "cause"
    if any(word in q for word in ("what is", "define", "ما هو", "ايه هو", "ماهي")):
        return "definition"
    return "general"


def _query(question: str, history: Sequence[Dict[str, str]]) -> str:
    recent = [message["content"] for message in history[-4:]]
    names = _mapped_names("\n".join([*recent, question]))
    return "\n".join([*recent, *names, question])


def _point_context(point: Any) -> Optional[Dict[str, Any]]:
    payload = getattr(point, "payload", {}) or {}
    if not isinstance(payload, dict):
        return None
    text = _text(payload.get("text"))
    if not text:
        return None
    return {
        "text": text,
        "metadata": _augment_meta(payload.get("metadata")),
        "score": float(getattr(point, "score", 0.0) or 0.0),
    }


def _extra_contexts(contexts: Sequence[Dict[str, Any]], question: str, limit: int = 3) -> List[Dict[str, Any]]:
    if not contexts:
        return []
    disease = _norm((contexts[0].get("metadata") or {}).get("disease_name"))
    if not disease:
        return []

    wanted = INTENT_SECTIONS.get(_intent(question), ("overview", "simple explanation", "symptoms"))
    seen = {_norm(item.get("text")) for item in contexts}
    extras: List[Dict[str, Any]] = []

    for record in _kb():
        meta = _augment_meta(record.get("metadata"))
        if _norm(meta.get("disease_name")) != disease:
            continue
        section = _norm(meta.get("section_title"))
        text = _text(record.get("text"), 2200)
        if not text or _norm(text) in seen:
            continue
        if any(word in section for word in wanted) or len(extras) < 1:
            extras.append({"text": text, "metadata": meta, "score": 0.0})
        if len(extras) >= limit:
            break
    return extras


def _local_contexts(question: str, history: Sequence[Dict[str, str]], limit: int) -> List[Dict[str, Any]]:
    query = _norm(_query(question, history))
    names = [_norm(name) for name in _mapped_names(query)]
    wanted = INTENT_SECTIONS.get(_intent(question), ("overview", "simple explanation", "symptoms"))
    results: List[Tuple[int, Dict[str, Any]]] = []

    for record in _kb():
        meta = _augment_meta(record.get("metadata"))
        disease = _norm(meta.get("disease_name"))
        section = _norm(meta.get("section_title"))
        text = _text(record.get("text"), 2200)
        if not text:
            continue

        disease_names = _norm(" ".join([disease, _text(meta.get("disease_name_ar"), 200)]))
        haystack = _norm(" ".join([disease_names, section, text[:500]]))
        if names and not any(name and (name in disease_names or disease in name) for name in names):
            continue
        score = sum(3 for name in names if name and (name in haystack or haystack in name))
        score += sum(1 for token in query.split() if len(token) > 2 and token in haystack)
        score += 2 if any(word in section for word in wanted) else 0
        if score:
            results.append((score, {"text": text, "metadata": meta, "score": float(score)}))

    results.sort(key=lambda item: item[0], reverse=True)
    contexts: List[Dict[str, Any]] = []
    seen_sections = set()
    seen_diseases = set()

    for _, context in results:
        disease = _norm(context["metadata"].get("disease_name"))
        section = _norm(context["metadata"].get("section_title"))
        if disease in seen_diseases or (disease, section) in seen_sections:
            continue
        contexts.append(context)
        seen_diseases.add(disease)
        seen_sections.add((disease, section))
        if len(contexts) >= limit:
            return contexts

    for _, context in results:
        key = (_norm(context["metadata"].get("disease_name")), _norm(context["metadata"].get("section_title")))
        if key in seen_sections:
            continue
        contexts.append(context)
        seen_sections.add(key)
        if len(contexts) >= limit:
            break
    return contexts


def _merge_contexts(contexts: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    seen = set()
    for context in contexts:
        key = _norm(context.get("text"))
        if key and key not in seen:
            merged.append(context)
            seen.add(key)
    return merged


def _retrieve(question: str, history: Sequence[Dict[str, str]], top_k: int) -> Tuple[List[Dict[str, Any]], str]:
    provider = None
    try:
        provider = _qdrant()
        provider.connect()
        vector = _embedder().encode([_query(question, history)], normalize_embeddings=True, convert_to_numpy=True).tolist()[0]
        points = provider.search_by_vector(
            collection_name=settings.qdrant.collection_name,
            vector=vector,
            limit=min(top_k * 2, 20),
        )
        contexts = [ctx for point in points for ctx in [_point_context(point)] if ctx]
        local = _local_contexts(question, history, top_k)
        contexts = _merge_contexts([*local, *contexts])[:top_k]
        return contexts + _extra_contexts(contexts, question), ""
    except Exception as exc:
        logger.warning("Qdrant retrieval failed; using local KB fallback: %s", exc)
        contexts = _local_contexts(question, history, top_k)
        contexts = contexts + _extra_contexts(contexts, question)
        return contexts, "" if contexts else str(exc)
    finally:
        if provider:
            provider.disconnect()


def _messages(question: str, history: Sequence[Dict[str, str]], contexts: Sequence[Dict[str, Any]]) -> List[Dict[str, str]]:
    context = "\n\n".join(
        f"[{i}] metadata={json.dumps(c.get('metadata', {}), ensure_ascii=False)}\n{c.get('text', '')}"
        for i, c in enumerate(contexts, 1)
    )[:MAX_CONTEXT_CHARS] or NO_CONTEXT
    recent = "\n".join(f"{m['role']}: {m['content']}" for m in history[-4:]) or "(none)"
    language = "Arabic" if _has_arabic(question) else "English"

    user_prompt = (
        f"Required answer language: {language}\n\n"
        f"Recent conversation:\n{recent}\n\n"
        f"Knowledge-base context:\n{context}\n\n"
        f"Latest user question:\n{question}"
    )
    return [{"role": "system", "content": SYSTEM_PROMPT}, *history, {"role": "user", "content": user_prompt}]


def _generate(messages: Sequence[Dict[str, str]]) -> Tuple[str, str, Dict[str, Any]]:
    response = _openai_client().chat.completions.create(
        model=settings.groq.model,
        temperature=settings.groq.temperature,
        max_tokens=settings.groq.max_tokens,
        messages=list(messages),
    )
    answer = (response.choices[0].message.content or "").strip() if response.choices else ""
    usage = response.usage.model_dump() if getattr(response, "usage", None) else {}
    return answer, str(getattr(response, "model", settings.groq.model)), usage


def ask_llm(question: str) -> Dict[str, Any]:
    question = _text(question)
    if not question:
        raise ValueError("question is required")
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": question}]
    with TraceSpan("llm_only", "chain", {"question": question}) as root:
        with TraceSpan("llm_generate", "llm", {"model": settings.groq.model, "messages": messages}, root.id) as llm:
            answer, model, usage = _generate(messages)
            llm.outputs = {"answer": answer, "model": model, "usage": usage}
        root.outputs = {"answer": answer, "model": model}
    return {"answer": answer, "model": model}


def ask_rag(question: str, top_k: int = 5, history: Optional[Sequence[Dict[str, str]]] = None) -> Dict[str, Any]:
    question = _text(question)
    top_k = int(top_k)
    if not question:
        raise ValueError("question is required")
    if top_k < 1 or top_k > 20:
        raise ValueError("top_k must be between 1 and 20")

    clean_history = _history(history)
    with TraceSpan("rag_chain", "chain", {"question": question, "top_k": top_k, "history_count": len(clean_history)}) as root:
        with TraceSpan("retrieve_context", "retriever", {"question": question, "top_k": top_k}, root.id) as retriever:
            contexts, retrieval_error = _retrieve(question, clean_history, top_k)
            retriever.outputs = {"contexts_count": len(contexts), "retrieval_error": retrieval_error}

        with TraceSpan("build_prompt", "prompt", {"question": question, "contexts_count": len(contexts)}, root.id) as prompt:
            messages = _messages(question, clean_history, contexts)
            prompt.outputs = {"messages_count": len(messages)}

        with TraceSpan("llm_generate", "llm", {"model": settings.groq.model, "messages": messages}, root.id) as llm:
            answer, model, usage = _generate(messages)
            llm.outputs = {"answer": answer, "model": model, "usage": usage}

        result = {"answer": answer, "model": model, "contexts": contexts, "retrieval_error": retrieval_error}
        root.outputs = {**result, "contexts_count": len(contexts)}
        return result


def main() -> None:
    import sys

    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print("Usage: python -m src.generation.rag_chain <question>")
        raise SystemExit(2)
    print(ask_rag(question)["answer"])


if __name__ == "__main__":
    main()
