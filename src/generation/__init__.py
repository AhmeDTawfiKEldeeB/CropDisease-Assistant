def ask_rag(*args, **kwargs):
	from .rag_chain import ask_rag as _ask_rag

	return _ask_rag(*args, **kwargs)


def ask_llm(*args, **kwargs):
	from .rag_chain import ask_llm as _ask_llm

	return _ask_llm(*args, **kwargs)


def main(*args, **kwargs):
	from .rag_chain import main as _main

	return _main(*args, **kwargs)


__all__ = ["ask_rag", "ask_llm", "main"]

