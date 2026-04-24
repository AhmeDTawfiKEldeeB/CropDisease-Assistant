import logging
import re
from fastapi import APIRouter, HTTPException

from src.api.schemas import ChatRequest, ChatResponse
from src.generation import ask_rag, ask_llm

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])


def clean_text(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    cleaned = re.sub(r"##\s*", "", cleaned)
    cleaned = re.sub(r"#\s*", "", cleaned)
    cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
    cleaned = re.sub(r"```", "", cleaned)
    return cleaned.strip()


@router.post("/chat", response_model=ChatResponse)
async def chat_rag(body: ChatRequest):
    try:
        result = ask_rag(question=body.question, top_k=body.top_k, history=body.history)
        answer = clean_text(result.get("answer", ""))
        return ChatResponse(
            answer=answer,
            model=result.get("model", ""),
            contexts=result.get("contexts", []),
            retrieval_error=result.get("retrieval_error", ""),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error in /api/chat")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")


@router.post("/chat/llm", response_model=ChatResponse)
async def chat_llm(body: ChatRequest):
    try:
        result = ask_llm(question=body.question)
        answer = clean_text(result.get("answer", ""))
        return ChatResponse(
            answer=answer,
            model=result.get("model", ""),
            contexts=[],
            retrieval_error="",
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error in /api/chat/llm")
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")