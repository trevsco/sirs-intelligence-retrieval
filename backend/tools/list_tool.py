import uuid
import time
from mcp.protocol import MCPResponse
from mcp.tool_registry import tool_registry
from retrieval.vector_store import vector_store

@tool_registry.register(
    tool_name="list_documents",
    action="list",
    description="Fetch a collection of all registered documents in the vector index including metadata and chunk counts.",
    schema={}
)
async def list_documents() -> MCPResponse:
    """Registered MCP tool to list all documents with their computed chunk totals."""
    start_time = time.perf_counter()
    msg_id = str(uuid.uuid4())
    
    try:
        documents_list = vector_store.get_documents()
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        return MCPResponse.make_success(
            message_id=msg_id,
            tool_name="list_documents",
            action="list",
            data=documents_list,
            execution_time_ms=elapsed_ms
        )
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return MCPResponse.make_error(
            message_id=msg_id,
            tool_name="list_documents",
            action="list",
            error_detail=f"List tool error: {str(e)}",
            execution_time_ms=elapsed_ms
        )
