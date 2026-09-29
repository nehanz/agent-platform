import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


class Settings:
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "gemini")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_CHAT_MODEL: str = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash")
    GEMINI_EMBEDDING_MODEL: str = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
    EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM", "768"))

    FAISS_INDEX_PATH: str = str(BASE_DIR / os.getenv("FAISS_INDEX_PATH", "data/faiss_index"))
    FAISS_METADATA_PATH: str = str(BASE_DIR / os.getenv("FAISS_METADATA_PATH", "data/faiss_metadata.json"))
    SQLITE_AUDIT_DB: str = str(BASE_DIR / os.getenv("SQLITE_AUDIT_DB", "data/audit.db"))

    AUTH_MODE: str = os.getenv("AUTH_MODE", "local")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-me")


settings = Settings()