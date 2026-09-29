from typing import List
from app.llm import get_llm_provider

_provider = None


def _get_provider():
    global _provider
    if _provider is None:
        _provider = get_llm_provider()
    return _provider


def embed_texts(texts: List[str]) -> List[List[float]]:
    return _get_provider().embed(texts)