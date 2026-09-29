import json
import os
import faiss
import numpy as np
from pathlib import Path
from typing import List, Dict

from app.config import settings
from .embeddings import embed_texts


def _chunk_text(text: str, chunk_size: int = 400, overlap: int = 60) -> List[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


def load_documents(docs_dir: Path) -> List[Dict]:
    """Load all .md files → chunk → return list of {text, source, tenant_id}."""
    docs = []
    for md_file in sorted(docs_dir.glob("*.md")):
        raw = md_file.read_text(encoding="utf-8")
        # Convention: filename prefix "tenantA__" scopes to a tenant; otherwise "public"
        tenant_id = "public"
        name = md_file.stem
        if "__" in name:
            tenant_id = name.split("__", 1)[0]
        for chunk in _chunk_text(raw):
            docs.append({
                "text": chunk,
                "source": md_file.name,
                "tenant_id": tenant_id,
            })
    return docs


def build_index(docs_dir: Path = None) -> None:
    if docs_dir is None:
        docs_dir = Path(__file__).resolve().parent.parent.parent / "knowledge_base" / "docs"

    docs = load_documents(docs_dir)
    if not docs:
        raise RuntimeError(f"No .md documents found in {docs_dir}")

    texts = [d["text"] for d in docs]
    vectors = embed_texts(texts)
    mat = np.array(vectors, dtype=np.float32)

    index = faiss.IndexFlatIP(mat.shape[1])  # cosine sim because vectors are L2-normalized
    index.add(mat)

    os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH), exist_ok=True)
    faiss.write_index(index, settings.FAISS_INDEX_PATH)

    with open(settings.FAISS_METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)

    print(f"[indexer] Built FAISS index with {len(docs)} chunks, dim={mat.shape[1]}")


def load_index():
    if not os.path.exists(settings.FAISS_INDEX_PATH):
        raise FileNotFoundError(
            f"FAISS index not found at {settings.FAISS_INDEX_PATH}. "
            f"Run: python scripts/rebuild_index.py"
        )
    index = faiss.read_index(settings.FAISS_INDEX_PATH)
    with open(settings.FAISS_METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return index, metadata