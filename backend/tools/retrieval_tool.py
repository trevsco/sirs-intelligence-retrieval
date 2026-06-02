import uuid
import time
from mcp.protocol import MCPResponse
from mcp.tool_registry import tool_registry
from retrieval.rag_pipeline import rag_pipeline
from config import settings

@tool_registry.register(
    tool_name="retrieve_documents",
    action="search",
    description="Search the local FAISS vector database to retrieve intelligence segments matching a query.",
    schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string", 
                "description": "Natural language query to search documents"
            },
            "top_k": {
                "type": "integer", 
                "description": "Number of snippets to retrieve", 
                "default": 5
            },
            "threshold": {
                "type": "number", 
                "description": "Cosine similarity cutoff (default is 0.0)", 
                "default": 0.0
            }
        },
        "required": ["query"]
    }
)
async def retrieve_documents(
    query: str, 
    top_k: int = None, 
    threshold: float = None
) -> MCPResponse:
    """Registered MCP tool to execute document segment searches."""
    start_time = time.perf_counter()
    msg_id = str(uuid.uuid4())
    
    # Use fallback configuration values if args are missing
    k = top_k if top_k is not None else settings.TOP_K
    t = threshold if threshold is not None else settings.SIMILARITY_THRESHOLD
    
    try:
        result = rag_pipeline.run(query=query, top_k=k, threshold=t)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return MCPResponse.make_success(
            message_id=msg_id,
            tool_name="retrieve_documents",
            action="search",
            data=result,
            execution_time_ms=elapsed_ms
        )
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return MCPResponse.make_error(
            message_id=msg_id,
            tool_name="retrieve_documents",
            action="search",
            error_detail=f"Retrieval tool error: {str(e)}",
            execution_time_ms=elapsed_ms
        )
