import re
from typing import List, Dict, Any
from config import settings

class DocumentChunker:
    @staticmethod
    def chunk_text(
        text: str, 
        chunk_size: int = 512, 
        chunk_overlap: int = 64
    ) -> List[Dict[str, Any]]:
        """
        Splits text into chunks of maximum 'chunk_size' characters with 'chunk_overlap' characters overlap.
        Returns a list of dicts: {"text": str, "char_start": int, "char_end": int}
        """
        if not text:
            return []
            
        # Clean consecutive whitespace but preserve single newlines
        text = re.sub(r'[ \t]+', ' ', text)
        
        chunks = []
        text_len = len(text)
        start = 0
        
        # If the text is shorter than chunk size, return it as a single chunk
        if text_len <= chunk_size:
            return [{
                "text": text,
                "char_start": 0,
                "char_end": text_len
            }]
            
        while start < text_len:
            end = start + chunk_size
            
            # If we're not at the end of the text, try to find a natural boundary (like a space or newline)
            if end < text_len:
                # Look back up to 'chunk_overlap' characters for a space or newline
                lookback_range = text[end - chunk_overlap:end]
                boundary_idx = -1
                for marker in ['\n', ' ', '.', ',', ';']:
                    idx = lookback_range.rfind(marker)
                    if idx != -1:
                        boundary_idx = end - chunk_overlap + idx + 1
                        break
                
                if boundary_idx != -1:
                    end = boundary_idx
            
            # Slice and clean chunk
            chunk_content = text[start:end].strip()
            if chunk_content:
                chunks.append({
                    "text": chunk_content,
                    "char_start": start,
                    "char_end": min(end, text_len)
                })
                
            # Advance start pointer
            start = end - chunk_overlap
            
            # Safeguard to prevent infinite loops if overlap is configured poorly
            if start >= end:
                start = end
                
        return chunks
