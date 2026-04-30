from typing import Any, Dict, List
from src.config import settings
from src.services.prompt import build_prompt
from src.services.retrival import retrieve


def ask_rag(question: str, top_k: int = 5) -> Dict[str, Any]:
    try:
        contexts = retrieve(query=question, top_k=top_k)
    except Exception as e:
        return {
            "answer": "",
            "model": "",
            "contexts": [],
            "retrieval_error": str(e),
        }

    if not contexts:
        return {
            "answer": "No relevant information found.",
            "model": settings.groq.model,
            "contexts": [],
            "retrieval_error": "",
        }

    context_texts = [c["text"] for c in contexts]
    prompt = build_prompt(question=question, contexts=context_texts)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.groq.api_key, base_url=settings.groq.base_url)
        response = client.chat.completions.create(
            model=settings.groq.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=settings.groq.temperature,
            max_tokens=settings.groq.max_tokens,
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Error generating response: {e}"

    return {
        "answer": answer,
        "model": settings.groq.model,
        "contexts": [{"text": c, "metadata": {}, "score": 0.0} for c in context_texts],
        "retrieval_error": "",
    }


def ask_llm(question: str) -> Dict[str, Any]:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.groq.api_key, base_url=settings.groq.base_url)
        response = client.chat.completions.create(
            model=settings.groq.model,
            messages=[{"role": "user", "content": question}],
            temperature=settings.groq.temperature,
            max_tokens=settings.groq.max_tokens,
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Error: {e}"

    return {
        "answer": answer,
        "model": settings.groq.model,
    }