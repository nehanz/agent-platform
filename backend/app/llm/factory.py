from .base import LLMProvider
from .gemini_provider import GeminiProvider
from app.config import settings


def get_llm_provider() -> LLMProvider:
    if settings.LLM_PROVIDER == "gemini":
        return GeminiProvider()
    # BedrockProvider
    raise ValueError(f"Unknown LLM_PROVIDER: {settings.LLM_PROVIDER}")