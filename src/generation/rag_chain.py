import argparse
import re
import sys
from typing import Any, Dict, List
from openai import OpenAI
from openai import AuthenticationError
from sentence_transformers import SentenceTransformer
from src.config import settings
from src.infrastructure.qdrant.vectorstore import QdrantDBProvider


CONCISE_RULES = (
	"Answer in maximum 3 short bullet points or 2 short sentences. "
	"Do not include headings. Do not include chain-of-thought. "
	"Do not include tags like <think>."
)


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


def _build_prompt(question: str, contexts: List[Dict[str, Any]]) -> str:
	if not contexts:
		return (
			"No context was retrieved from the knowledge base. "
			"Answer with uncertainty and ask the user for more details.\n"
			f"{CONCISE_RULES}\n\n"
			f"Question: {question}"
		)

	context_lines: List[str] = []
	for idx, item in enumerate(contexts, start=1):
		disease = item["metadata"].get("disease_name", "unknown")
		section = item["metadata"].get("section_title", "unknown")
		context_lines.append(
			f"[{idx}] disease={disease} | section={section}\n{item['text']}"
		)

	return (
		"You are an agricultural disease assistant. "
		"Use only the provided context. If the answer is not present, say you are not sure.\n\n"
		f"{CONCISE_RULES}\n\n"
		"Context:\n"
		+ "\n\n".join(context_lines)
		+ f"\n\nQuestion: {question}\n"
		"Include only the minimal useful details and cite used context indices like [2], [3]."
	)


def _sanitize_answer(text: str) -> str:
	if not text:
		return ""

	# Remove any exposed reasoning blocks if the model emits them.
	cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
	cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()

	lines = [line.rstrip() for line in cleaned.splitlines() if line.strip()]
	unique_lines: List[str] = []
	seen = set()
	for line in lines:
		normalized = re.sub(r"\s+", " ", line.strip()).lower()
		if normalized in seen:
			continue
		seen.add(normalized)
		unique_lines.append(line)

	bullet_lines = [line for line in unique_lines if line.lstrip().startswith("-")]
	if bullet_lines:
		return "\n".join(bullet_lines[:3]).strip()

	return "\n".join(unique_lines[:2]).strip()


def ask_llm(question: str) -> Dict[str, Any]:
	api_key = settings.groq.api_key.strip()
	base_url = settings.groq.base_url.strip()

	_validate_groq_key(api_key)

	client = OpenAI(base_url=base_url, api_key=api_key)
	try:
		response = client.chat.completions.create(
			model=settings.groq.model,
			temperature=settings.groq.temperature,
			messages=[
				{
					"role": "system",
					"content": "You are a helpful agricultural assistant. " + CONCISE_RULES,
				},
				{"role": "user", "content": question},
			],
		)
	except AuthenticationError as exc:
		raise RuntimeError(
			"Groq authentication failed (401 invalid_api_key). "
			"Update GROQ__API_KEY in .env with a valid key from the Groq dashboard."
		) from exc
	answer = _sanitize_answer(response.choices[0].message.content if response.choices else "")
	return {
		"answer": answer,
		"model": settings.groq.model,
		"contexts": [],
		"retrieval_error": "",
	}


def ask_rag(question: str, top_k: int = 5) -> Dict[str, Any]:
	api_key = settings.groq.api_key.strip()
	base_url = settings.groq.base_url.strip()

	_validate_groq_key(api_key)
	if not settings.qdrant.url:
		raise ValueError("QDRANT__URL is required")
	if not settings.qdrant.api_key:
		raise ValueError("QDRANT__API_KEY is required")

	embedder = SentenceTransformer(settings.huggingface.model_name)
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
		retrieval_error = f"Qdrant retrieval failed: {exc}"
	finally:
		provider.disconnect()

	contexts = _extract_context(points)
	prompt = _build_prompt(question, contexts)

	client = OpenAI(base_url=base_url, api_key=api_key)
	try:
		response = client.chat.completions.create(
			model=settings.groq.model,
			temperature=settings.groq.temperature,
			max_tokens=settings.groq.max_tokens,
			messages=[
				{
					"role": "system",
					"content": "You answer using the provided context only. " + CONCISE_RULES,
				},
				{"role": "user", "content": prompt},
			],
		)
	except AuthenticationError as exc:
		raise RuntimeError(
			"Groq authentication failed (401 invalid_api_key). "
			"Update GROQ__API_KEY in .env with a valid key from the Groq dashboard."
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

