from abc import ABC, abstractmethod
from typing import List, Dict, Any


class LLMProvider(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], system: str = "") -> str:
        """Return plain text response."""
        ...

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Return L2-normalized embeddings for a batch of texts."""
        ...