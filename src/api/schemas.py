"""Pydantic schemas for API."""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    disease_name: Optional[str] = None
    plant: Optional[str] = None


class ContextItem(BaseModel):
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    score: float = 0.0




class ChatResponse(BaseModel):
    answer: str
    model: str
    contexts: List[ContextItem] = Field(default_factory=list)
    retrieval_error: str = ""


class HealthResponse(BaseModel):
    status: str = "ok"