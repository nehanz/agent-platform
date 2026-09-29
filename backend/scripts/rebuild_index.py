"""Rebuild the FAISS index from knowledge_base/docs.

Run this whenever:
  - You add/change knowledge base documents.
  - You switch embedding providers (Gemini ↔ Bedrock).
"""
import sys
from pathlib import Path

# Add backend/ to path so `app.*` imports resolve
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.indexer import build_index

if __name__ == "__main__":
    build_index()
    print("Index rebuilt successfully.")