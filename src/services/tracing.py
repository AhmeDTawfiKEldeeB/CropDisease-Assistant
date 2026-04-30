import logging
import os
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any, Dict, Optional
from uuid import uuid4

from openai import OpenAI

from src.config import settings
from src.services.prompt import build_prompt
from src.services.retrival import retrieve

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _read_dotenv() -> Dict[str, str]:
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
    if not os.path.exists(env_path):
        return {}
    values: Dict[str, str] = {}
    try:
        with open(env_path, "r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                if key:
                    values[key] = value.strip().strip('"').strip("'")
        return values
    except Exception:
        logger.exception("Failed to read .env for LangSmith tracing.")
        return {}


def _env(name: str, default: str = "") -> str:
    return os.getenv(name) or _read_dotenv().get(name, default)


def _is_true(value: str) -> bool:
    return value.lower() in {"1", "true", "yes", "on"}


def _setup_tracing() -> bool:
    enabled = bool(settings.langsmith.tracing) or _is_true(_env("LANGSMITH_TRACING")) or _is_true(_env("LANGSMITH_TRACING_V2"))
    api_key = settings.langsmith.api_key or _env("LANGSMITH_API_KEY") or _env("LANGSMITH__API_KEY")
    if not enabled or not api_key:
        return False

    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_TRACING_V2"] = "true"
    os.environ["LANGSMITH_API_KEY"] = api_key
    os.environ.setdefault("LANGSMITH_PROJECT", settings.langsmith.project or _env("LANGSMITH_PROJECT", "CropDisease"))
    os.environ.setdefault("LANGSMITH_ENDPOINT", settings.langsmith.endpoint or _env("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"))
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
    ) -> None:
        self.id = str(uuid4())
        self.name = name
        self.run_type = run_type
        self.inputs = inputs
        self.parent_id = parent_id
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


def _clip(value: Any, limit: int = 4000) -> str:
    return str(value or "").replace("\x00", " ").strip()[:limit].strip()


def ask_rag(question: str, top_k: int = 5) -> Dict[str, Any]:
    with TraceSpan(
        name="Rag",
        run_type="chain",
        inputs={"question": question, "top_k": top_k},
    ) as chain_span:
        try:
            with TraceSpan(
                name="retrieve_context",
                run_type="retriever",
                inputs={"query": question, "top_k": top_k},
                parent_id=chain_span.id,
            ) as retriever_span:
                contexts = retrieve(query=question, top_k=top_k)
                documents = [
                    {
                        "page_content": c.get("text", ""),
                        "metadata": c.get("metadata", {}),
                        "score": c.get("score", 0.0),
                    }
                    for c in contexts
                ]
                retriever_span.outputs = {
                    "documents": documents,
                    "contexts": contexts,
                }
        except Exception as exc:
            chain_span.outputs = {"error": str(exc)}
            return {
                "answer": "",
                "model": settings.groq.model,
                "contexts": [],
                "retrieval_error": str(exc),
            }

        if not contexts:
            chain_span.outputs = {"answer": "No relevant information found.", "contexts": []}
            return {
                "answer": "No relevant information found.",
                "model": settings.groq.model,
                "contexts": [],
                "retrieval_error": "",
            }

        context_texts = [c.get("text", "") for c in contexts]
        prompt = build_prompt(question=question, contexts=context_texts)

        with TraceSpan(
            name="prompt",
            run_type="prompt",
            inputs={"question": question, "contexts": context_texts},
            parent_id=chain_span.id,
        ) as prompt_span:
            prompt_span.outputs = {"prompt": prompt}

        try:
            with TraceSpan(
                name="llm",
                run_type="llm",
                inputs={
                    "model": settings.groq.model,
                    "temperature": settings.groq.temperature,
                    "max_tokens": settings.groq.max_tokens,
                    "contexts": context_texts,
                    "messages": [{"role": "user", "content": _clip(prompt)}],
                },
                parent_id=chain_span.id,
            ) as llm_span:
                client = OpenAI(
                    api_key=settings.groq.api_key,
                    base_url=settings.groq.base_url,
                )
                response = client.chat.completions.create(
                    model=settings.groq.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=settings.groq.temperature,
                    max_tokens=settings.groq.max_tokens,
                )
                answer = response.choices[0].message.content
                llm_span.outputs = {"answer": answer}
        except Exception as exc:
            answer = f"Error generating response: {exc}"

        chain_span.outputs = {"answer": answer, "contexts": contexts}

        return {
            "answer": answer,
            "model": settings.groq.model,
            "contexts": contexts,
            "retrieval_error": "",
        }


def ask_llm(question: str) -> Dict[str, Any]:
    with TraceSpan(
        name="Rag",
        run_type="chain",
        inputs={"question": question},
    ) as chain_span:
        try:
            with TraceSpan(
                name="llm",
                run_type="llm",
                inputs={
                    "model": settings.groq.model,
                    "temperature": settings.groq.temperature,
                    "max_tokens": settings.groq.max_tokens,
                    "messages": [{"role": "user", "content": _clip(question)}],
                },
                parent_id=chain_span.id,
            ) as llm_span:
                client = OpenAI(
                    api_key=settings.groq.api_key,
                    base_url=settings.groq.base_url,
                )
                response = client.chat.completions.create(
                    model=settings.groq.model,
                    messages=[{"role": "user", "content": question}],
                    temperature=settings.groq.temperature,
                    max_tokens=settings.groq.max_tokens,
                )
                answer = response.choices[0].message.content
                llm_span.outputs = {"answer": answer}
        except Exception as exc:
            answer = f"Error: {exc}"

        chain_span.outputs = {"answer": answer}

        return {
            "answer": answer,
            "model": settings.groq.model,
        }
