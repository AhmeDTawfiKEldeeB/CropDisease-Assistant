import argparse
import json
import re
from pathlib import Path
from typing import Any


HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+")
BLOCKQUOTE_RE = re.compile(r"^\s{0,3}>\s?")
UNORDERED_LIST_RE = re.compile(r"^\s*[-*+]\s+")
ORDERED_LIST_RE = re.compile(r"^\s*\d+\.\s+")
HORIZONTAL_RULE_RE = re.compile(r"^\s*([-*_]\s*){3,}$")

IMAGE_RE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")

BOLD_RE = re.compile(r"\*\*(.*?)\*\*")
BOLD_UNDERSCORE_RE = re.compile(r"__(.*?)__")
ITALIC_STAR_RE = re.compile(r"\*(.*?)\*")
ITALIC_UNDERSCORE_RE = re.compile(r"_(.*?)_")
INLINE_CODE_RE = re.compile(r"`([^`]*)`")


def clean_markdown_text(text: str) -> str:
    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        if HORIZONTAL_RULE_RE.match(line):
            continue

        line = HEADING_RE.sub("", line)
        line = BLOCKQUOTE_RE.sub("", line)
        line = UNORDERED_LIST_RE.sub("", line)
        line = ORDERED_LIST_RE.sub("", line)

        cleaned_lines.append(line)

    cleaned = "\n".join(cleaned_lines)

    cleaned = IMAGE_RE.sub(r"\1", cleaned)
    cleaned = LINK_RE.sub(r"\1", cleaned)
    cleaned = BOLD_RE.sub(r"\1", cleaned)
    cleaned = BOLD_UNDERSCORE_RE.sub(r"\1", cleaned)
    cleaned = ITALIC_STAR_RE.sub(r"\1", cleaned)
    cleaned = ITALIC_UNDERSCORE_RE.sub(r"\1", cleaned)
    cleaned = INLINE_CODE_RE.sub(r"\1", cleaned)

    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)
    return cleaned.strip()


def clean_value(value: Any) -> Any:
    if isinstance(value, str):
        return clean_markdown_text(value)

    if isinstance(value, list):
        return [clean_value(item) for item in value]

    if isinstance(value, dict):
        return {key: clean_value(item) for key, item in value.items()}

    return value


def main() -> None:
    script_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(
        description="Clean markdown symbols from all string values in a JSON file."
    )
    parser.add_argument(
        "--input",
        default="diseases_from_md.json",
        help="Input JSON path (default: diseases_from_md.json)",
    )
    parser.add_argument(
        "--output",
        default="diseases_from_md_clean.json",
        help="Output JSON path when not using --inplace",
    )
    parser.add_argument(
        "--inplace",
        action="store_true",
        help="Overwrite the input file instead of writing a separate file",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = script_dir / input_path

    output_path = input_path if args.inplace else Path(args.output)
    if not output_path.is_absolute():
        output_path = script_dir / output_path

    data = json.loads(input_path.read_text(encoding="utf-8"))
    cleaned_data = clean_value(data)

    output_path.write_text(
        json.dumps(cleaned_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Cleaned markdown JSON saved to: {output_path}")


if __name__ == "__main__":
    main()
