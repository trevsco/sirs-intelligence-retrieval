from typing import List, Dict, Any
from loguru import logger
from mcp.protocol import MCPMessage, MCPResponse, ToolStatus
from mcp.communication import mcp_bus

class ToolRouter:
    async def execute_plan(
        self, 
        plan: List[str], 
        query: str, 
        top_k: int = 5, 
        threshold: float = 0.0
    ) -> Dict[str, Any]:
        """
        Sequentially execute a list of tool names, carrying context over between them.
        Accumulates results in a context dictionary and returns a complete tool trace audit.
        """
        context: Dict[str, Any] = {}
        tool_trace: List[Dict[str, Any]] = []
        
        logger.info(f"ToolRouter: Starting execution of plan: {plan}")
        
        for tool_name in plan:
            action = ""
            payload: Dict[str, Any] = {}
            
            # Setup tool parameters based on dynamic context matching
            if tool_name == "retrieve_documents":
                action = "search"
                payload = {
                    "query": query,
                    "top_k": top_k,
                    "threshold": threshold
                }
            elif tool_name == "summarize_results":
                action = "summarize"
                payload = {
                    "text": context.get("context", "")
                }
            elif tool_name == "generate_report":
                action = "generate"
                payload = {
                    "query": query,
                    "chunks": context.get("chunks", [])
                }
            elif tool_name == "list_documents":
                action = "list"
                payload = {}
            elif tool_name == "upload_document":
                # Fallback action; uploads are normally executed via dedicated API routes
                action = "ingest"
                payload = {}
                
            logger.info(f"ToolRouter: Dispatching tool '{tool_name}' ({action}) with payload keys: {list(payload.keys())}")
            
            # Build and route MCP message
            message = MCPMessage(
                tool_name=tool_name,
                action=action,
                payload=payload
            )
            
            # Run using the MCP communication bus
            response: MCPResponse = await mcp_bus.send(message)
            
            # Record execution trace
            trace_entry = {
                "tool": tool_name,
                "action": action,
                "status": response.status.value,
                "execution_time_ms": response.execution_time_ms
            }
            tool_trace.append(trace_entry)
            
            # Verify if execution failed
            if response.status == ToolStatus.ERROR:
                # CRITICAL: Read the error using .error_detail per Pydantic v2 naming rules
                err_msg = response.error_detail or "Unknown tool execution failure."
                logger.error(f"ToolRouter failed on '{tool_name}': {err_msg}")
                context["error_detail"] = err_msg
                break
                
            # Process success response data
            if response.data is not None:
                if isinstance(response.data, dict):
                    context.update(response.data)
                else:
                    context["last_result"] = response.data
                    
                # Explicitly normalize outputs of retrieve_documents to feed subsequent steps
                if tool_name == "retrieve_documents":
                    context["chunks"] = response.data.get("chunks", [])
                    context["context"] = response.data.get("context", "")
                    context["confidence"] = response.data.get("confidence", 0.0)
                    context["sources"] = response.data.get("sources", [])
                    
        return {
            "context": context,
            "tool_trace": tool_trace
        }

tool_router = ToolRouter()
