import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


IMAGE_RE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")
INLINE_CODE_RE = re.compile(r"`([^`]*)`")
EMPHASIS_RE = re.compile(r"\*\*(.*?)\*\*|__(.*?)__|\*(.*?)\*|_(.*?)_")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*[-:]+(?:\s*\|\s*[-:]+)+\s*\|?\s*$")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _strip_inline_markdown(text: str) -> str:
    text = IMAGE_RE.sub(r"\1", text)
    text = LINK_RE.sub(r"\1", text)
    text = INLINE_CODE_RE.sub(r"\1", text)
    text = EMPHASIS_RE.sub(lambda m: next(g for g in m.groups() if g is not None), text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _clean_markdown_text(text: str) -> str:
    cleaned_lines: List[str] = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        if not line.strip():
            cleaned_lines.append("")
            continue

        if re.match(r"^\s*([-*_]\s*){3,}$", line):
            continue

        # Convert two-column markdown tables to "key: value" lines.
        if "|" in line:
            if TABLE_SEPARATOR_RE.match(line):
                continue

            parts = [
                _strip_inline_markdown(part.strip())
                for part in line.strip().strip("|").split("|")
            ]
            parts = [part for part in parts if part]
            if len(parts) >= 2:
                line = f"{parts[0]}: {parts[1]}"
            else:
                line = " ".join(parts)

        line = re.sub(r"^\s{0,3}#{1,6}\s+", "", line)
        line = re.sub(r"^\s{0,3}>\s?", "", line)
        line = re.sub(r"^\s*[-*+]\s+", "", line)
        line = re.sub(r"^\s*\d+\.\s+", "", line)
        line = _strip_inline_markdown(line)
        cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text).strip()
    return cleaned_text


def _clean_title(title: str) -> str:
    match = re.search(r"[A-Za-z0-9\u0600-\u06FF]", title)
    cleaned = title[match.start():] if match else ""
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"^[^A-Za-z0-9\u0600-\u06FF]+", "", cleaned)
    return cleaned.strip()


def _title_parts(title: str, file_name: str) -> Tuple[str, str, str]:
    cleaned_title = _clean_title(title) if title else file_name
    split_parts = re.split(r"\s+[\u2013\u2014-]\s+", cleaned_title, maxsplit=1)

    if len(split_parts) == 2:
        disease_base = split_parts[0].strip()
        plant = split_parts[1].strip()
    else:
        disease_base = cleaned_title.strip()
        plant = ""

    disease_name = f"{disease_base} - {plant}" if plant else disease_base
    return disease_name, disease_base, plant


def _extract_metadata_line(lines: List[str]) -> Dict[str, str]:
    info = {"pathogen": "", "type": "", "host": ""}

    for line in lines:
        if "Pathogen:" not in line and "Type:" not in line and "Host:" not in line:
            continue

        clean_line = _strip_inline_markdown(line)
        segments = [seg.strip() for seg in clean_line.split("|") if seg.strip()]

        for seg in segments:
            if ":" not in seg:
                continue
            key, value = [part.strip() for part in seg.split(":", 1)]
            key_l = key.lower()

            if key_l == "pathogen":
                info["pathogen"] = value
            elif key_l == "type":
                # Keep primary disease type for clean metadata (e.g. "Fungal" from "Fungal (Rust)").
                info["type"] = value.split("(", 1)[0].strip()
            elif key_l == "host":
                info["host"] = value

        if info["pathogen"] or info["type"] or info["host"]:
            break

    return info


def _normalize_plant(host_value: str, fallback_plant: str) -> str:
    if fallback_plant.strip():
        return fallback_plant.strip()

    if host_value:
        plant = host_value.split(",", 1)[0]
        plant = plant.split("/", 1)[0]
        plant = plant.split("(", 1)[0]
        plant = plant.strip()
        if plant:
            return plant
    return fallback_plant


def _section_key(section_title: str) -> str:
    normalized = _clean_title(section_title)
    normalized = re.sub(r"[^A-Za-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", "_", normalized).strip("_").lower()
    if not normalized:
        return "general"

    section_aliases = {
        "simple_explanation": "definition",
        "definition": "definition",
        "severity_danger_level": "severity",
        "severity_and_danger_level": "severity",
        "time_to_spread": "spread_time",
        "how_does_it_spread": "spread",
        "how_it_spreads": "spread",
        "pathogen_biology": "pathogen_biology",
        "symptoms": "symptoms",
        "favorable_conditions": "favorable_conditions",
        "disease_cycle": "disease_cycle",
        "treatment_management": "treatment",
        "treatment_and_management": "treatment",
        "quick_actions_what_to_do_right_now": "quick_actions",
        "quick_actions": "quick_actions",
        "scouting_monitoring_guide": "monitoring",
        "scouting_and_monitoring": "monitoring",
        "geographic_distribution": "distribution",
        "frequently_asked_questions": "faq",
        "faq": "faq",
    }

    return section_aliases.get(normalized, normalized)


def _clean_synonym_term(value: str) -> str:
    cleaned = _strip_inline_markdown(value)
    cleaned = cleaned.lower()
    cleaned = re.sub(
        r"^(also\s+)?(formerly\s+)?(known|referred)\s+as\s+",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s+in\s+some\s+literature$", "", cleaned)
    cleaned = cleaned.strip(" .,:;()[]{}\"'\n\t")

    # Keep short disease/pathogen terms; drop noisy phrase-like text.
    word_count = len([w for w in cleaned.split() if w])
    if word_count > 5:
        return ""
    if any(token in cleaned for token in (" known as ", " referred to ")):
        return ""

    return cleaned


def _extract_synonyms(md_text: str, disease_base: str, pathogen: str) -> List[str]:
    synonyms: List[str] = []

    def add_syn(term: str) -> None:
        cleaned = _clean_synonym_term(term)
        if cleaned and cleaned not in synonyms:
            synonyms.append(cleaned)

    add_syn(disease_base)
    add_syn(pathogen)

    # Capture patterns like "formerly known as X", "also known as Y" and "referred to as Z".
    aka_patterns = [
        r"formerly known as\s+([^.,;\n]+)",
        r"also known as\s+([^.,;\n]+)",
        r"referred to as\s+([^.,;\n]+)",
        r"known under the synonyms\s+([^\n]+)",
        r"synonyms?\s*[:\-]\s*([^\n]+)",
    ]

    for pattern in aka_patterns:
        for match in re.finditer(pattern, md_text, flags=re.IGNORECASE):
            raw = match.group(1)
            pieces = re.split(r",| and | or ", raw, flags=re.IGNORECASE)
            for piece in pieces:
                add_syn(piece)

    return synonyms


def _chunk_text(text: str, max_chars: int, min_chars: int) -> List[str]:
    if len(text) <= max_chars:
        return [text]

    sentences = [s.strip() for s in SENTENCE_SPLIT_RE.split(text) if s.strip()]
    if not sentences:
        return [text]

    chunks: List[str] = []
    current: List[str] = []
    current_len = 0

    def flush_current() -> None:
        nonlocal current, current_len
        if current:
            chunks.append(" ".join(current).strip())
            current = []
            current_len = 0

    for sentence in sentences:
        sentence_len = len(sentence)
        if sentence_len >= max_chars:
            flush_current()
            # Hard split very long sentences.
            for i in range(0, sentence_len, max_chars):
                chunk = sentence[i:i + max_chars].strip()
                if chunk:
                    chunks.append(chunk)
            continue

        if current_len + sentence_len + (1 if current else 0) > max_chars:
            flush_current()

        current.append(sentence)
        current_len += sentence_len + (1 if current_len else 0)

    flush_current()

    # Merge tiny tail chunk if needed.
    if len(chunks) >= 2 and len(chunks[-1]) < min_chars:
        chunks[-2] = (chunks[-2] + " " + chunks[-1]).strip()
        chunks.pop()

    return chunks


def parse_markdown(md_text: str, file_name: str, chunk_size: int, chunk_min: int) -> List[Dict[str, object]]:
    lines = md_text.splitlines()
    doc_title = ""

    for line in lines:
        if line.startswith("# "):
            doc_title = line[2:].strip()
            break

    disease_name, disease_base, fallback_plant = _title_parts(doc_title, file_name)
    info = _extract_metadata_line(lines)
    plant = _normalize_plant(info["host"], fallback_plant)
    pathogen = info["pathogen"]
    disease_type = info["type"].lower()
    synonyms = _extract_synonyms(md_text, disease_base, pathogen)

    records: List[Dict[str, object]] = []
    current_section: Optional[str] = None
    buffer: List[str] = []

    def flush_record() -> None:
        nonlocal buffer
        if current_section is None:
            buffer = []
            return

        text_block = _clean_markdown_text("\n".join(buffer))
        if not text_block:
            buffer = []
            return

        chunks = _chunk_text(text_block, chunk_size, chunk_min)
        total_chunks = len(chunks)
        for idx, chunk in enumerate(chunks, start=1):
            records.append(
                {
                    "text": chunk,
                    "metadata": {
                        "disease_name": disease_name,
                        "disease_base": disease_base,
                        "plant": plant,
                        "section": _section_key(current_section),
                        "pathogen": pathogen,
                        "type": disease_type,
                        "synonyms": synonyms,
                        "chunk_index": idx,
                        "chunk_total": total_chunks,
                    },
                }
            )
        buffer = []

    for line in lines:
        if line.startswith("## "):
            flush_record()
            current_section = _clean_title(line[3:].strip())
            continue

        # Skip the metadata line because it is represented as structured metadata.
        if "Pathogen:" in line and "Host:" in line and "Type:" in line:
            continue

        buffer.append(line)

    flush_record()
    return records


def convert_markdown_folder(input_dir: Path, chunk_size: int, chunk_min: int) -> List[Dict[str, object]]:
    all_records: List[Dict[str, object]] = []

    for md_file in sorted(input_dir.glob("*.md")):
        if md_file.name.lower() == "readme.md":
            continue

        md_text = md_file.read_text(encoding="utf-8")
        fallback_name = md_file.stem.replace("_", " ").title()
        records = parse_markdown(md_text, fallback_name, chunk_size, chunk_min)
        all_records.extend(records)

    return all_records


def main() -> None:
    script_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(
        description="Convert disease markdown files to JSON with text + disease metadata"
    )
    parser.add_argument(
        "--input-dir",
        default="Knowledge_base",
        help="Folder that contains disease markdown files (default: Knowledge_base)",
    )
    parser.add_argument(
        "--output",
        default="diseases_from_md.json",
        help="Output JSON file path (default: diseases_from_md.json)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=900,
        help="Maximum characters per chunk (default: 900)",
    )
    parser.add_argument(
        "--chunk-min",
        type=int,
        default=200,
        help="Minimum characters for last chunk before merge (default: 200)",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.is_absolute():
        input_dir = script_dir / input_dir
    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"Input folder not found: {input_dir}")

    all_records = convert_markdown_folder(input_dir, args.chunk_size, args.chunk_min)

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = script_dir / output_path
    output_path.write_text(
        json.dumps(all_records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Converted {len(all_records)} records from {input_dir} -> {output_path}")


if __name__ == "__main__":
    main()
