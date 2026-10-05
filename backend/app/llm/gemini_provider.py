import numpy as np
from typing import List, Dict
from google import genai
from google.genai import types

from .base import LLMProvider
from app.config import settings


class GeminiProvider(LLMProvider):
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set")
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.chat_model = settings.GEMINI_CHAT_MODEL
        self.embed_model = settings.GEMINI_EMBEDDING_MODEL
        self.embed_dim = settings.EMBEDDING_DIM

    def chat(self, messages: List[Dict[str, str]], system: str = "") -> str:
        import time
        from google.genai.errors import APIError

        contents = []
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            contents.append(
                types.Content(role=role, parts=[types.Part(text=m["content"])])
            )

        config = types.GenerateContentConfig(
            system_instruction=system if system else None,
            temperature=0.2,
        )

        primary = self.chat_model if self.chat_model in ("gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash") else "gemini-3.8-flash"
        candidates = [primary, "gemini-3.7-flash", "gemini-3.5-flash", "gemini-flash-latest"]
        if self.chat_model and self.chat_model not in candidates:
            candidates.append(self.chat_model)

        last_error = None
        for model_name in candidates:
            for attempt in range(2):
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=config,
                    )
                    return (response.text or "").strip()
                except APIError as e:
                    last_error = e
                    if getattr(e, "code", None) in (503, 429) or "UNAVAILABLE" in str(e):
                        time.sleep(1.0)
                        continue
                    break
                except Exception as e:
                    last_error = e
                    break

        if last_error:
            raise last_error
        return ""


    def embed(self, texts: List[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        for text in texts:
            kwargs = {"model": self.embed_model, "contents": text}
            if self.embed_dim and "text-embedding" in self.embed_model:
                kwargs["config"] = {"output_dimensionality": self.embed_dim}
            result = self.client.models.embed_content(**kwargs)
            vec = np.array(result.embeddings[0].values, dtype=np.float32)
            # Gemini-embedding-001 returns unnormalized vectors → normalize for cosine sim
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            vectors.append(vec.tolist())
        return vectors