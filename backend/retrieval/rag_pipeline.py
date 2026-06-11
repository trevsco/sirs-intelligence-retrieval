from typing import List, Dict, Any
from loguru import logger
from config import settings
from retrieval.vector_store import vector_store

# ── FIX 1: Import the embedding model so we can vectorize the query ──
from retrieval.embeddings import embedding_model
# ─────────────────────────────────────────────────────────────────────

class RAGPipeline:
    @staticmethod
    def run(
        query: str, 
        top_k: int = 5, 
        threshold: float = 0.0
    ) -> Dict[str, Any]:
        """
        Execute the retrieval pipeline:
        1. Query the vector store using the embedding representation.
        2. Format retrieved chunks as a combined context string.
        3. Compute confidence score based on the retrieval similarity scores.
        4. Deduplicate source filenames.
        """
        logger.info(f"Running RAG pipeline for query: '{query}', top_k: {top_k}, threshold: {threshold}")
        
        # ── FIX 1: Convert the text query into a mathematical vector ──
        # We use encode_batch here because we know from vector_store.py that this method exists
        query_vector = embedding_model.encode_batch([query])[0]
        
        # Now we pass the vector to FAISS, not the string!
        results = vector_store.search(query_vector, top_k=top_k, threshold=threshold)
        # ─────────────────────────────────────────────────────────────
        
        if not results:
            logger.info("No matching chunks found in FAISS vector store.")
            return {
                "chunks": [],
                "context": "",
                "confidence": 0.0,
                "sources": []
            }
            
        chunks = []
        sources = set()
        context_elements = []
        scores = []
        
        for res in results:
            chunks.append(res)
            sources.add(res["filename"])
            
            # ── FIX 2: Use "content" to match the vector_store metadata ──
            # We use .get() just to be absolutely safe
            chunk_text = res.get("content") or res.get("text") or ""
            context_elements.append(chunk_text)
            # ─────────────────────────────────────────────────────────────
            
            scores.append(res["score"])
            
        # Join chunks together with high visual separation for LLM context reading
        context = "\n\n=== SOURCE SEGMENT ===\n" + "\n\n=== SOURCE SEGMENT ===\n".join(context_elements)
        
        # Compute confidence based on the average cosine similarity of retrieved chunks
        avg_score = sum(scores) / len(scores) if scores else 0.0
        # Clip to positive ranges
        confidence = max(0.0, min(1.0, avg_score))
        
        logger.info(
            f"RAG pipeline retrieved {len(chunks)} chunks from {len(sources)} sources. "
            f"Confidence: {confidence:.4f}"
        )
        
        return {
            "chunks": chunks,
            "context": context,
            "confidence": round(confidence, 4),
            "sources": sorted(list(sources))
        }

rag_pipeline = RAGPipeline()