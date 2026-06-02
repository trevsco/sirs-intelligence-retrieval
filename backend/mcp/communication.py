import time
import inspect
from typing import List, Dict, Any, Optional
from loguru import logger
from mcp.protocol import MCPMessage, MCPResponse, ToolStatus
from mcp.tool_registry import tool_registry

class MCPBus:
    def __init__(self) -> None:
        self._audit_log: List[Dict[str, Any]] = []

    async def send(self, message: MCPMessage) -> MCPResponse:
        """Route an MCPMessage to its registered handler and return MCPResponse."""
        start_time = time.perf_counter()
        tool_name = message.tool_name
        action = message.action
        
        logger.info(f"MCP Dispatch -> Tool: {tool_name}, Action: {action}, MsgID: {message.message_id}")
        handler = tool_registry.get_handler(tool_name, action)
        
        if not handler:
            execution_time_ms = (time.perf_counter() - start_time) * 1000.0
            error_msg = f"No handler registered for tool '{tool_name}' and action '{action}'"
            response = MCPResponse.make_error(
                message_id=message.message_id,
                tool_name=tool_name,
                action=action,
                error_detail=error_msg,
                execution_time_ms=execution_time_ms
            )
            self._log_audit(message, response)
            logger.error(error_msg)
            return response
            
        try:
            # Inspect handler to see how to call it
            sig = inspect.signature(handler)
            has_kwargs = any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())
            
            # Filter parameters to only what the handler expects unless it takes **kwargs
            if has_kwargs:
                kwargs = message.payload
            else:
                kwargs = {
                    k: v for k, v in message.payload.items()
                    if k in sig.parameters
                }
            
            # Execute handler (async or sync)
            if inspect.iscoroutinefunction(handler):
                result = await handler(**kwargs)
            else:
                result = handler(**kwargs)
            
            execution_time_ms = (time.perf_counter() - start_time) * 1000.0
            
            if isinstance(result, MCPResponse):
                response = result
                # Update execution time if not set
                if response.execution_time_ms == 0.0:
                    response.execution_time_ms = execution_time_ms
            else:
                response = MCPResponse.make_success(
                    message_id=message.message_id,
                    tool_name=tool_name,
                    action=action,
                    data=result,
                    execution_time_ms=execution_time_ms
                )
                
            logger.info(f"MCP Resolve -> Tool: {tool_name}, Status: {response.status.value}, Time: {execution_time_ms:.2f}ms")
            
        except Exception as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000.0
            error_msg = f"Error executing tool '{tool_name}': {str(e)}"
            logger.exception(error_msg)
            response = MCPResponse.make_error(
                message_id=message.message_id,
                tool_name=tool_name,
                action=action,
                error_detail=error_msg,
                execution_time_ms=execution_time_ms
            )
            
        self._log_audit(message, response)
        return response

    def _log_audit(self, message: MCPMessage, response: MCPResponse) -> None:
        """Record the tool execution in the audit log list."""
        log_entry = {
            "message_id": message.message_id,
            "timestamp": message.timestamp,
            "tool_name": message.tool_name,
            "action": message.action,
            "status": response.status.value,
            "execution_time_ms": response.execution_time_ms,
            "payload": message.payload,
            "error_detail": response.error_detail
        }
        self._audit_log.append(log_entry)
        # Cap audit log to avoid memory blowup
        if len(self._audit_log) > 1000:
            self._audit_log.pop(0)

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Return the complete audit logs list."""
        return self._audit_log

mcp_bus = MCPBus()
