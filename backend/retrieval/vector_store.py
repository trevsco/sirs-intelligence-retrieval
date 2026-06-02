import os
import pickle
import numpy as np
import faiss
from typing import List, Dict, Any, Tuple, Optional
from loguru import logger
from config import settings
from retrieval.embeddings import embedding_model

class VectorStore:
    def __init__(self) -> None:
        self._index_path = settings.MODELS_DIR / "faiss_index" / "index.faiss"
        self._metadata_path = settings.MODELS_DIR / "faiss_index" / "metadata.pkl"
        self._index: Optional[faiss.IndexFlatIP] = None
        self._metadata: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        """Load index and metadata from disk, or initialize empty if not found."""
        os.makedirs(self._index_path.parent, exist_ok=True)
        if os.path.exists(self._index_path) and os.path.exists(self._metadata_path):
            try:
                self._index = faiss.read_index(str(self._index_path))
                with open(self._metadata_path, "rb") as f:
                    self._metadata = pickle.load(f)
                logger.info(f"Loaded FAISS index with {self._index.ntotal} vectors.")
                self._validate_sync()
            except Exception as e:
                logger.error(f"Error loading vector store: {e}. Reinitializing empty store.")
                self._init_empty()
        else:
            self._init_empty()

    def _init_empty(self) -> None:
        """Initialize an empty FAISS IndexFlatIP (Cosine Similarity)."""
        self._index = faiss.IndexFlatIP(settings.EMBEDDING_DIM)
        self._metadata = []
        logger.info("Initialized new empty FAISS index (IndexFlatIP).")

    def _validate_sync(self) -> None:
        """
        CRITICAL SYNC CHECK:
        Compares self._index.ntotal with len(self._metadata).
        If mismatched, truncates self._metadata to match index size and saves.
        """
        if self._index is None:
            return
        ntotal = self._index.ntotal
        meta_len = len(self._metadata)
        if ntotal != meta_len:
            logger.warning(
                f"Sync mismatch detected: FAISS index count ({ntotal}) does not match "
                f"metadata length ({meta_len}). Truncating metadata to match index size."
            )
            self._metadata = self._metadata[:ntotal]
            self._save()

    def _save(self) -> None:
        """Serialize index and metadata to disk."""
        if self._index is None:
            return
        os.makedirs(self._index_path.parent, exist_ok=True)
        faiss.write_index(self._index, str(self._index_path))
        with open(self._metadata_path, "wb") as f:
            pickle.dump(self._metadata, f)
        logger.info(f"Saved FAISS index and metadata. Count: {self._index.ntotal}")

    def add_chunks(self, chunks: List[Dict[str, Any]], doc_id: str, filename: str) -> None:
        """Add chunks to vector store, compute embeddings, validate sync and save."""
        if self._index is None:
            self._init_empty()
            
        assert self._index is not None
        if not chunks:
            return
            
        texts = [chunk["text"] for chunk in chunks]
        embeddings = embedding_model.get_embeddings(texts)
        embeddings_np = np.array(embeddings).astype("float32")
        
        # Add to FAISS index
        self._index.add(embeddings_np)
        
        # Add parallel records to metadata
        for chunk in chunks:
            self._metadata.append({
                "doc_id": doc_id,
                "filename": filename,
                "text": chunk["text"],
                "char_start": chunk["char_start"],
                "char_end": chunk["char_end"]
            })
            
        self._validate_sync()
        self._save()

    def search(
        self, 
        query: str, 
        top_k: int = 5, 
        threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Search the FAISS index and return metadata matches above similarity threshold."""
        if self._index is None or self._index.ntotal == 0:
            return []
            
        # Get query embedding
        query_emb = embedding_model.get_embedding(query)
        query_np = np.array([query_emb]).astype("float32")
        
        # Search index
        scores, indices = self._index.search(query_np, top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
                
            # CRITICAL BOUNDS CHECK: prevent IndexError if metadata and index are out of sync
            if idx >= len(self._metadata):
                logger.warning(
                    f"FAISS index retrieved idx={idx} which is out of metadata bounds (len={len(self._metadata)}). Skipping."
                )
                continue
                
            score_val = float(score)
            if score_val >= threshold:
                meta = self._metadata[idx]
                results.append({
                    "text": meta["text"],
                    "doc_id": meta["doc_id"],
                    "filename": meta["filename"],
                    "score": score_val,
                    "char_start": meta["char_start"],
                    "char_end": meta["char_end"]
                })
        return results

    def delete_document(self, doc_id: str) -> None:
        """
        Delete document by rebuilding the entire index.
        IndexFlatIP does not support native element deletion.
        """
        logger.info(f"Deleting document {doc_id} and rebuilding vector index...")
        remaining_metadata = [meta for meta in self._metadata if meta["doc_id"] != doc_id]
        
        if not remaining_metadata:
            self._init_empty()
            self._save()
            logger.info("All documents deleted. Vector store is now empty.")
            return
            
        # Rebuild
        texts = [meta["text"] for meta in remaining_metadata]
        embeddings = embedding_model.get_embeddings(texts)
        embeddings_np = np.array(embeddings).astype("float32")
        
        new_index = faiss.IndexFlatIP(settings.EMBEDDING_DIM)
        new_index.add(embeddings_np)
        
        self._index = new_index
        self._metadata = remaining_metadata
        
        self._validate_sync()
        self._save()
        logger.info(f"Rebuild completed successfully. New vector count: {self._index.ntotal}")

    def get_chunk_count(self) -> int:
        return self._index.ntotal if self._index else 0

    def get_documents(self) -> List[Dict[str, Any]]:
        """Return a summarized list of all unique documents and their chunk counts."""
        docs = {}
        for meta in self._metadata:
            doc_id = meta["doc_id"]
            if doc_id not in docs:
                docs[doc_id] = {
                    "doc_id": doc_id,
                    "filename": meta["filename"],
                    "chunk_count": 0
                }
            docs[doc_id]["chunk_count"] += 1
        return list(docs.values())

vector_store = VectorStore()
