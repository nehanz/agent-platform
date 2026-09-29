import numpy as np
from typing import List, Dict
from .indexer import load_index
from .embeddings import embed_texts

_index_cache = None
_meta_cache = None


def _get_index():
    global _index_cache, _meta_cache
    if _index_cache is None:
        _index_cache, _meta_cache = load_index()
    return _index_cache, _meta_cache


def retrieve(query: str, tenant_id: str, top_k: int = 3) -> List[Dict]:
    index, metadata = _get_index()
    qvec = np.array(embed_texts([query]), dtype=np.float32)

    # Search more than top_k, then filter by tenant
    scores, indices = index.search(qvec, min(top_k * 4, index.ntotal))

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        doc = metadata[idx]
        # Tenant isolation: allow own tenant OR public docs
        if doc["tenant_id"] not in (tenant_id, "public"):
            continue
        results.append({
            "text": doc["text"],
            "source": doc["source"],
            "tenant_id": doc["tenant_id"],
            "score": float(score),
        })
        if len(results) >= top_k:
            break
    return results