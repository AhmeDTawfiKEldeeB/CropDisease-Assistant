"""Utilities for RAG pipeline."""

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

from src.config import settings

logger = logging.getLogger(__name__)

ARABIC_BLACK_ROT = ("العفن الاسود", "العفن الأسود", "عفن اسود", "عفن أسود")

MAX_CONTEXT_CHARS = 6000
MAX_HISTORY = 10

INTENT_SECTIONS: Dict[str, Tuple[str, ...]] = {
    "treatment": ("treatment", "management", "control", "prevention"),
    "symptoms": ("symptoms", "signs", "simple explanation", "overview"),
    "cause": ("cause", "pathogen", "spread", "disease cycle", "overview"),
    "definition": ("simple explanation", "overview", "pathogen"),
    "general": ("overview", "simple explanation", "symptoms"),
}


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


def text(value: Any, limit: int = 4000) -> str:
    """Clean and truncate text value."""
    return str(value or "").replace("\x00", " ").strip()[:limit].strip()


def normalize(value: Any) -> str:
    """Normalize text for matching."""
    text = str(value or "").lower().strip()
    text = re.sub(r"[\s_\-–—]+", " ", text)
    text = re.sub(r"[^\w\u0621-\u064a ]+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def name_keys(name: str) -> List[str]:
    """Generate all possible keys from a disease name."""
    keys = {normalize(name)}
    for sep in (" - ", "-", " – ", " — "):
        if sep in name:
            left, right = [part.strip() for part in name.split(sep, 1)]
            if left and right:
                keys.add(normalize(f"{left} {right}"))
                keys.add(normalize(f"{right} {left}"))
                keys.add(normalize(left))
    return [key for key in keys if key]


def has_arabic(text: str) -> bool:
    """Check if text contains Arabic characters."""
    return bool(re.search(r"[\u0600-\u06ff]", text))


def load_json(path: str) -> List[Dict[str, Any]]:
    """Load JSON file, returning empty list on failure."""
    file_path = Path(path)
    if not file_path.is_absolute():
        file_path = Path.cwd() / file_path
    if not file_path.exists():
        logger.warning("JSON file not found: %s", file_path)
        return []
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        logger.exception("Failed to load JSON file: %s", file_path)
        return []


@lru_cache(maxsize=1)
def kb() -> List[Dict[str, Any]]:
    """Load knowledge base from JSON."""
    return load_json(settings.qdrant.data_json_path)


@lru_cache(maxsize=1)
def name_map() -> Dict[str, Dict[str, str]]:
    """Build normalized disease name mapping."""
    mapping: Dict[str, Dict[str, str]] = {}
    for record in [*kb(), *load_json("chatbot/diseases.json")]:
        meta = record.get("metadata") or {}
        if not isinstance(meta, dict):
            continue
        en = text(meta.get("disease_name"), 200)
        ar = text(meta.get("disease_name_ar"), 200)
        if not en:
            continue
        names = {"en": en, "ar": ar}
        for name in (en, ar):
            for key in name_keys(name):
                mapping[key] = names
    for alias in ARABIC_BLACK_ROT:
        mapping[normalize(alias)] = {"en": "Black Rot", "ar": alias}
    return mapping


def matches_name(key: str, text: str) -> bool:
    """Check if key matches in text with loose token matching."""
    if key in text:
        return True
    stop = {"in", "on", "of", "the", "في", "على", "من", "ال"}
    key_tokens = [part for part in key.split() if part not in stop]
    text_tokens = {part for part in text.split() if part not in stop}
    return bool(key_tokens) and all(part in text_tokens for part in key_tokens)


def mapped_names(text: str) -> List[str]:
    """Map text to known disease names."""
    normalized = normalize(text)
    found: List[str] = []
    for key, names in name_map().items():
        if matches_name(key, normalized):
            found.extend(name for name in names.values() if name)
    if "black rot" in normalized or any(
        normalize(alias) in normalized for alias in ARABIC_BLACK_ROT
    ):
        found.extend(["Black Rot", "Black Rot - Apple", "Black Rot - Grape", *ARABIC_BLACK_ROT])
    return list(dict.fromkeys(found))


def augment_meta(meta: Any) -> Dict[str, Any]:
    """Augment metadata with missing translations."""
    meta = meta if isinstance(meta, dict) else {}
    disease = text(meta.get("disease_name"), 200)
    if not disease or meta.get("disease_name_ar"):
        return dict(meta)

    for key in name_keys(disease):
        names = name_map().get(key)
        if names:
            updated = dict(meta)
            updated.setdefault("disease_name", names["en"])
            if names.get("ar"):
                updated.setdefault("disease_name_ar", names["ar"])
            return updated
    return dict(meta)


def clean_history(
    history: Optional[Sequence[Dict[str, str]]]
) -> List[Dict[str, str]]:
    """Clean and truncate conversation history."""
    role_map = {"ai": "assistant", "bot": "assistant", "human": "user"}
    clean: List[Dict[str, str]] = []
    for item in history or []:
        if not isinstance(item, dict):
            continue
        role = role_map.get(
            str(item.get("role", "")).lower(), str(item.get("role", "")).lower()
        )
        content = text(item.get("content"), 1200)
        if role in {"user", "assistant"} and content:
            clean.append({"role": role, "content": content})
    return clean[-MAX_HISTORY:]


def detect_intent(question: str) -> str:
    """Detect user intent from question."""
    q = normalize(question)
    if any(
        word in q
        for word in (
            "treatment",
            "treat",
            "control",
            "manage",
            "cure",
            "علاج",
            "مكافحة",
        )
    ):
        return "treatment"
    if any(
        word in q
        for word in (
            "symptom",
            "sign",
            "look like",
            "اعراض",
            "أعراض",
            "علامات",
            "شكل",
        )
    ):
        return "symptoms"
    if any(word in q for word in ("cause", "pathogen", "caused by", "سبب", "المسبب")):
        return "cause"
    if any(
        word in q for word in ("what is", "define", "ما هو", "ايه هو", "ماهي")
    ):
        return "definition"
    return "general"


def detect_language(text: str) -> str:
    """Detect primary language of text."""
    if not text:
        return "English"
    arabic_count = len(re.findall(r"[\u0600-\u06ff]", text))
    total_chars = len(re.findall(r"[\w\u0600-\u06ff]", text))
    if total_chars > 0 and arabic_count / total_chars > 0.3:
        return "Arabic"
    return "English"


def intent_sections(question: str) -> Sequence[str]:
    """Get preferred section titles for detected intent."""
    return INTENT_SECTIONS.get(detect_intent(question), INTENT_SECTIONS["general"])


def truncate_context(contexts: Sequence[Dict[str, Any]]) -> str:
    """Truncate contexts to fit within max characters."""
    result = []
    total = 0
    for ctx in contexts:
        chunk = f"[{len(result)}] metadata={json.dumps(ctx.get('metadata', {}), ensure_ascii=False)}\n{ctx.get('text', '')}"
        if total + len(chunk) > MAX_CONTEXT_CHARS:
            remaining = MAX_CONTEXT_CHARS - total
            if remaining > 100:
                result.append(chunk[:remaining])
            break
        result.append(chunk)
        total += len(chunk)
    return "\n\n".join(result) or "No relevant context available."