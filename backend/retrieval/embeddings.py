from typing import List, Optional
from sentence_transformers import SentenceTransformer
from config import settings
from loguru import logger

class EmbeddingModel:
    def __init__(self) -> None:
        self._model: Optional[SentenceTransformer] = None

    def load(self) -> None:
        """Pre-loads the sentence-transformer model if it has not been loaded yet."""
        if self._model is None:
            logger.info(f"Loading sentence-transformer model: {settings.EMBEDDING_MODEL}...")
            # sentence-transformers loads internally; will download if not cached
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("Sentence-transformer model loaded successfully.")

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Encode multiple texts and return normalized float embeddings."""
        self.load()
        if not texts:
            return []
        assert self._model is not None
        # We set normalize_embeddings=True to allow direct Cosine Similarity calculations with IndexFlatIP
        embeddings = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return [emb.tolist() for emb in embeddings]

    def get_embedding(self, text: str) -> List[float]:
        """Encode a single string and return its normalized embedding."""
        return self.get_embeddings([text])[0]

embedding_model = EmbeddingModel()
