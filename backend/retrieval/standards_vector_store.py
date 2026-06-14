# ==============================================================================
# SIRS — Standards Vector Store
# File: backend/retrieval/standards_vector_store.py
#
# PURPOSE: Query interface for the IEEE standards FAISS index built by
#          standards_indexer.py. Used by ieee_compliance_tool.py to retrieve
#          relevant clauses from IEEE 830, 829, 1016 for a given text chunk.
# ==============================================================================

import os
import json
import numpy as np
from loguru import logger

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_DIR      = os.path.join(BASE_DIR, "data", "standards_index")
FAISS_PATH     = os.path.join(INDEX_DIR, "standards.index")
METADATA_PATH  = os.path.join(INDEX_DIR, "standards_metadata.json")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class StandardsVectorStore:
    def __init__(self):
        self._index    = None
        self._metadata = []
        self._model    = None
        self._loaded   = False
        self._load()

    def _load(self):
        if not os.path.exists(FAISS_PATH):
            logger.warning(f"[StandardsVectorStore] standards.index not found at {FAISS_PATH}. Run standards_indexer.py first.")
            return
        if not os.path.exists(METADATA_PATH):
            logger.warning(f"[StandardsVectorStore] standards_metadata.json not found at {METADATA_PATH}.")
            return
        try:
            import faiss
            from sentence_transformers import SentenceTransformer
            logger.info("[StandardsVectorStore] Loading standards FAISS index ...")
            self._index = faiss.read_index(FAISS_PATH)
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                self._metadata = json.load(f)
            logger.info("[StandardsVectorStore] Loading embedding model ...")
            self._model = SentenceTransformer(EMBEDDING_MODEL)
            self._loaded = True
            logger.info(
                f"[StandardsVectorStore] Ready — "
                f"{self._index.ntotal} clause vectors loaded "
                f"({len(set(c['standard_id'] for c in self._metadata))} standards)"
            )
        except Exception as e:
            logger.error(f"[StandardsVectorStore] Load failed: {e}")
            self._loaded = False

    @property
    def is_ready(self) -> bool:
        return self._loaded

    def query(self, text: str, top_k: int = 4, standard_filter: str | None = None) -> list[dict]:
        if not self._loaded:
            logger.warning("[StandardsVectorStore] Not loaded — returning empty results.")
            return []
        if not text or not text.strip():
            return []
        try:
            query_vec = self._model.encode([text.strip()], convert_to_numpy=True).astype(np.float32)

            # FIX: fetch large pool when filtering so we always find the target standard
            if standard_filter:
                fetch_k = min(top_k * 50, self._index.ntotal)
            else:
                fetch_k = min(top_k, self._index.ntotal)

            distances, indices = self._index.search(query_vec, fetch_k)
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx == -1:
                    continue
                chunk = self._metadata[idx]
                if standard_filter and chunk["standard_id"] != standard_filter:
                    continue
                results.append({
                    "text":        chunk["text"],
                    "standard_id": chunk["standard_id"],
                    "page":        chunk["page"],
                    "source":      chunk["source"],
                    "score":       float(dist),
                })
                if len(results) >= top_k:
                    break
            return results
        except Exception as e:
            logger.error(f"[StandardsVectorStore] Query failed: {e}")
            return []

    def query_per_standard(self, text: str, top_k_per_standard: int = 2) -> dict[str, list[dict]]:
        if not self._loaded:
            return {}
        RAG_STANDARDS = ["IEEE 830", "IEEE 829", "IEEE 1016"]
        results = {}
        for standard_id in RAG_STANDARDS:
            clauses = self.query(text, top_k=top_k_per_standard, standard_filter=standard_id)
            if clauses:
                results[standard_id] = clauses
        return results

    def available_standards(self) -> list[str]:
        if not self._metadata:
            return []
        return list(set(c["standard_id"] for c in self._metadata))

    def stats(self) -> dict:
        if not self._loaded:
            return {"loaded": False}
        per_standard = {}
        for chunk in self._metadata:
            sid = chunk["standard_id"]
            per_standard[sid] = per_standard.get(sid, 0) + 1
        return {"loaded": True, "total_vectors": self._index.ntotal, "standards": per_standard}


_store_instance: StandardsVectorStore | None = None


def get_standards_store() -> StandardsVectorStore:
    global _store_instance
    if _store_instance is None:
        _store_instance = StandardsVectorStore()
    return _store_instance