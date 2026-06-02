import os
import uuid
import time
from typing import Dict, Any
import PyPDF2
import docx
from loguru import logger

from mcp.protocol import MCPResponse
from mcp.tool_registry import tool_registry
from retrieval.chunking import DocumentChunker
from retrieval.vector_store import vector_store
from config import settings

def extract_text(file_path: str) -> str:
    """Parse text based on document extension types (.pdf, .docx, .txt, .md)."""
    _, ext = os.path.splitext(file_path.lower())
    
    if ext in [".txt", ".md"]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
            
    elif ext == ".pdf":
        text = []
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return "\n\n".join(text)
        
    elif ext == ".docx":
        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs]
        return "\n".join(paragraphs)
        
    else:
        raise ValueError(f"Format '{ext}' is not supported for extraction.")

@tool_registry.register(
    tool_name="upload_document",
    action="ingest",
    description="Ingest a local document, extract text content, split into overlapping chunks, embed, and index in FAISS.",
    schema={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string", 
                "description": "Absolute path of the saved file to parse and ingest"
            },
            "filename": {
                "type": "string", 
                "description": "The name of the file"
            },
            "doc_id": {
                "type": "string", 
                "description": "Unique identifier for this document"
            }
        },
        "required": ["file_path", "filename", "doc_id"]
    }
)
async def ingest_document(file_path: str, filename: str, doc_id: str) -> MCPResponse:
    """Registered MCP action to ingest and parse a document into the system index."""
    start_time = time.perf_counter()
    msg_id = str(uuid.uuid4())
    
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File to ingest not found at path: {file_path}")
            
        logger.info(f"Ingesting file: {filename} from {file_path} for doc_id: {doc_id}")
        
        # 1. Extract Text
        text = extract_text(file_path)
        if not text.strip():
            raise ValueError("No text content could be extracted from the document.")
            
        # 2. Chunk Text
        chunks = DocumentChunker.chunk_text(
            text=text, 
            chunk_size=settings.CHUNK_SIZE, 
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        # 3. Add to FAISS and embed
        vector_store.add_chunks(chunks=chunks, doc_id=doc_id, filename=filename)
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        result_data = {
            "doc_id": doc_id,
            "filename": filename,
            "chunk_count": len(chunks),
            "total_characters": len(text),
            "status": "fully_indexed"
        }
        
        return MCPResponse.make_success(
            message_id=msg_id,
            tool_name="upload_document",
            action="ingest",
            data=result_data,
            execution_time_ms=elapsed_ms
        )
        
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        logger.exception(f"Ingest failed for document: {filename}")
        return MCPResponse.make_error(
            message_id=msg_id,
            tool_name="upload_document",
            action="ingest",
            error_detail=f"Ingestion failed: {str(e)}",
            execution_time_ms=elapsed_ms
        )

@tool_registry.register(
    tool_name="upload_document",
    action="delete",
    description="Remove all vector chunks corresponding to a document and rebuild the FAISS index.",
    schema={
        "type": "object",
        "properties": {
            "doc_id": {
                "type": "string", 
                "description": "Unique identifier of the document to purge"
            }
        },
        "required": ["doc_id"]
    }
)
async def delete_document_tool(doc_id: str) -> MCPResponse:
    """Registered MCP action to delete a document and rebuild index."""
    start_time = time.perf_counter()
    msg_id = str(uuid.uuid4())
    
    try:
        # Rebuilds the FAISS store without the specified doc_id
        vector_store.delete_document(doc_id)
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        return MCPResponse.make_success(
            message_id=msg_id,
            tool_name="upload_document",
            action="delete",
            data={"doc_id": doc_id, "status": "deleted"},
            execution_time_ms=elapsed_ms
        )
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        logger.exception(f"Delete failed for document: {doc_id}")
        return MCPResponse.make_error(
            message_id=msg_id,
            tool_name="upload_document",
            action="delete",
            error_detail=f"Deletion failed: {str(e)}",
            execution_time_ms=elapsed_ms
        )
