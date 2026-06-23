"""
retrieval/vector_store.py
--------------------------
Optimized FAISS vector store for SIRS.

Key optimizations:
1. Batch embedding during ingestion — encodes all chunks at once
   instead of one-by-one (much faster for large documents)
2. Validation only on startup and after mutations, not on every search
3. Normalized vectors for cosine-style similarity (more accurate)
4. Better scoring — converts L2 distance to a 0-1 similarity score
"""

import json
import numpy as np
import faiss
from pathlib import Path
from loguru import logger
from config import settings
from retrieval.embeddings import embedding_model

# ── Paths ─────────────────────────────────────────────────────────────────────
INDEX_DIR      = Path(settings.LOGS_DIR).parent / "data" / "faiss_index"
INDEX_FILE     = INDEX_DIR / "faiss_index.index"
METADATA_FILE  = INDEX_DIR / "metadata.json"


class VectorStore:
    """
    Optimized FAISS vector store with batch ingestion and accurate scoring.
    """

    def __init__(self):
        self._index:    faiss.IndexFlatIP = None   # Inner Product (cosine sim)
        self._metadata: list              = []
        self._synced:   bool              = False  # validated flag

    # ── Initialization ────────────────────────────────────────────────────────

    def _init_index(self):
        """Create a fresh FAISS IndexFlatIP (inner product = cosine similarity)."""
        self._index = faiss.IndexFlatIP(settings.EMBEDDING_DIM)

    def _load_index(self):
        """Load existing index from disk, or create fresh if not found."""
        INDEX_DIR.mkdir(parents=True, exist_ok=True)

        if INDEX_FILE.exists() and METADATA_FILE.exists():
            try:
                self._index    = faiss.read_index(str(INDEX_FILE))
                self._metadata = json.loads(METADATA_FILE.read_text(encoding="utf-8"))
                self._validate_sync()
                logger.info(f"FAISS index loaded: {self._index.ntotal} vectors, "
                            f"{len(self._metadata)} metadata entries.")
            except Exception as e:
                logger.warning(f"Index load failed ({e}). Creating fresh index.")
                self._init_index()
                self._metadata = []
        else:
            logger.info("No existing index found. Creating fresh FAISS index.")
            self._init_index()
            self._metadata = []

        self._synced = True

    def _save_index(self):
        """Persist index and metadata to disk."""
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(INDEX_FILE))
        METADATA_FILE.write_text(
            json.dumps(self._metadata, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def _validate_sync(self):
        """
        Ensure FAISS index vector count matches metadata list length.
        Called only on startup and after mutations (not on every search).
        """
        if self._index is None:
            return
        idx_count  = self._index.ntotal
        meta_count = len(self._metadata)
        if idx_count != meta_count:
            logger.warning(
                f"FAISS sync mismatch: {idx_count} vectors vs "
                f"{meta_count} metadata entries. Rebuilding..."
            )
            self._rebuild_from_metadata()

    def _ensure_loaded(self):
        """Lazy-load index on first access."""
        if self._index is None:
            self._load_index()

    # ── Core operations ───────────────────────────────────────────────────────

    def add_chunks(self, chunks: list, doc_id: str, filename: str):
        """
        Index all chunks for a document.

        Optimization: uses encode_batch() to embed all chunks at once
        instead of encoding one-by-one — much faster for large documents.
        """
        self._ensure_loaded()

        if not chunks:
            logger.warning(f"No chunks to index for {filename}")
            return

        logger.info(f"Batch encoding {len(chunks)} chunks for {filename}...")

        # ── Batch encode all chunks at once ───────────────────────────────────
        vectors = embedding_model.encode_batch(chunks)   # shape: (N, 384)

        # Add all vectors to FAISS in one call
        self._index.add(vectors)

        # Append metadata for each chunk
        for i, chunk in enumerate(chunks):
            self._metadata.append({
                "chunk_id":    f"{doc_id}_chunk_{i}",
                "doc_id":      doc_id,
                "filename":    filename,
                "content":     chunk,
                "chunk_index": i,
            })

        self._save_index()
        logger.info(f"Indexed {len(chunks)} chunks for '{filename}'. "
                    f"Total vectors: {self._index.ntotal}")

    def search(self, query_vector: np.ndarray, top_k: int,
               threshold: float = 0.0, doc_id: str = None) -> list:
        """
        Search FAISS index for top-K most similar chunks.

        Optimization: validation skipped here (done only on startup/mutations).
        Returns similarity score as 0-1 float (not raw L2 distance).
        """
        self._ensure_loaded()

        if self._index.ntotal == 0:
            logger.warning("FAISS index is empty — no documents indexed.")
            return []

        # Reshape to (1, dim) for FAISS
        query = query_vector.reshape(1, -1).astype(np.float32)

        # Search returns (distances, indices). When a document filter is active,
        # search the whole index first so other documents cannot hide matches.
        actual_k       = self._index.ntotal if doc_id else min(top_k, self._index.ntotal)
        scores, indices = self._index.search(query, actual_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue

            # Inner product of normalized vectors = cosine similarity (0 to 1)
            # Clamp to [0, 1] to handle floating point edge cases
            similarity = float(np.clip(score, 0.0, 1.0))

            metadata = self._metadata[idx]

            if doc_id and metadata.get("doc_id") != doc_id:
                continue

            if similarity < threshold:
                continue

            results.append({
                **metadata,
                "score": round(similarity, 4),
            })

            if len(results) >= top_k:
                break

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def delete_document(self, doc_id: str):
        """
        Remove all chunks for a document and rebuild the index.
        """
        self._ensure_loaded()

        before = len(self._metadata)
        self._metadata = [m for m in self._metadata if m["doc_id"] != doc_id]
        after  = len(self._metadata)

        if before == after:
            logger.warning(f"No chunks found for doc_id: {doc_id}")
            return

        logger.info(f"Removed {before - after} chunks for doc_id: {doc_id}. Rebuilding index...")
        self._rebuild_from_metadata()
        logger.info(f"Index rebuilt. Total vectors: {self._index.ntotal}")

    def _rebuild_from_metadata(self):
        """Rebuild FAISS index from scratch using current metadata."""
        self._init_index()

        if not self._metadata:
            self._save_index()
            return

        texts   = [m["content"] for m in self._metadata]
        vectors = embedding_model.encode_batch(texts)
        self._index.add(vectors)
        self._save_index()

    # ── Utility ───────────────────────────────────────────────────────────────

    def get_chunk_count(self) -> int:
        self._ensure_loaded()
        return self._index.ntotal if self._index else 0

    def get_documents(self) -> list:
        """Return list of unique documents currently indexed."""
        self._ensure_loaded()
        seen, docs = set(), []
        for m in self._metadata:
            if m["doc_id"] not in seen:
                seen.add(m["doc_id"])
                docs.append({
                    "doc_id":   m["doc_id"],
                    "filename": m["filename"],
                })
        return docs


# Module-level singleton
vector_store = VectorStore()
