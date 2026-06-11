"""
retrieval/embeddings.py
------------------------
Optimized embedding model wrapper for SIRS.

Key optimizations:
1. Query cache — same query text is not re-embedded on repeated calls
   (saves 100-200ms per cached hit)
2. Cache size limit — auto-clears when it grows too large
3. Batch encoding for multiple chunks at once (faster than one-by-one)
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from loguru import logger
from config import settings

# ── Cache settings ────────────────────────────────────────────────────────────
MAX_CACHE_SIZE = 200   # clear cache after 200 unique queries


class EmbeddingModel:
    """
    SentenceTransformers wrapper with query-level caching.

    The cache maps query_text -> np.ndarray (embedding vector).
    This means if the same query is asked twice, the second call
    returns instantly without running the transformer model.
    """

    def __init__(self):
        self._model:  SentenceTransformer = None
        self._loaded: bool                = False
        self._cache:  dict                = {}   # text -> np.ndarray

    def load(self):
        """Load the SentenceTransformer model into memory."""
        if self._loaded:
            return
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self._model  = SentenceTransformer(settings.EMBEDDING_MODEL)
        self._loaded = True
        logger.info("Embedding model loaded successfully.")

    def encode(self, text: str) -> np.ndarray:
        """
        Encode a single text string into a 384-dimensional vector.

        Optimization: checks cache first — avoids re-encoding
        the same query text on repeated calls.
        """
        if not self._loaded:
            self.load()

        # ── Cache hit ─────────────────────────────────────────────────────────
        if text in self._cache:
            return self._cache[text]

        # ── Cache miss — encode and store ─────────────────────────────────────
        vector = self._model.encode(
            text,
            normalize_embeddings=True,   # normalize for better cosine similarity
            show_progress_bar=False,
        ).astype(np.float32)

        # Auto-clear cache if it grows too large
        if len(self._cache) >= MAX_CACHE_SIZE:
            self._cache.clear()
            logger.debug("Embedding cache cleared (size limit reached)")

        self._cache[text] = vector
        return vector

    def encode_batch(self, texts: list) -> np.ndarray:
        """
        Encode multiple texts at once.

        Optimization: batch encoding is significantly faster than
        calling encode() in a loop for large document ingestion.
        """
        if not self._loaded:
            self.load()

        vectors = self._model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=32,            # process 32 chunks at a time
        ).astype(np.float32)

        # Store each in cache
        for text, vector in zip(texts, vectors):
            if len(self._cache) < MAX_CACHE_SIZE:
                self._cache[text] = vector

        return vectors

    def clear_cache(self):
        """Manually clear the embedding cache."""
        self._cache.clear()
        logger.info("Embedding cache manually cleared.")

    @property
    def cache_size(self) -> int:
        return len(self._cache)


# Module-level singleton
embedding_model = EmbeddingModel()