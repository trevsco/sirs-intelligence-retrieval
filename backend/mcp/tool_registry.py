from typing import Callable, Dict, Any, List, Optional, Tuple
from loguru import logger
from mcp.protocol import MCPMessage, MCPResponse

class ToolRegistry:
    def __init__(self) -> None:
        # Maps (tool_name, action) -> callable handler
        self._handlers: Dict[Tuple[str, str], Callable] = {}
        # Simple tool schemas/metadata for display/LLM
        self._tools_metadata: Dict[str, Dict[str, Any]] = {}

    def register(
        self, 
        tool_name: str, 
        action: str, 
        description: str, 
        schema: Optional[Dict[str, Any]] = None
    ) -> Callable:
        """Decorator to register a tool handler function."""
        def decorator(func: Callable) -> Callable:
            self._handlers[(tool_name, action)] = func
            if tool_name not in self._tools_metadata:
                self._tools_metadata[tool_name] = {
                    "name": tool_name,
                    "description": description,
                    "actions": {},
                }
            self._tools_metadata[tool_name]["actions"][action] = {
                "description": description,
                "schema": schema or {}
            }
            logger.info(f"Registered MCP tool: {tool_name} (action: {action})")
            return func
        return decorator

    def get_handler(self, tool_name: str, action: str) -> Optional[Callable]:
        """Retrieve the handler for a given tool name and action."""
        return self._handlers.get((tool_name, action))

    def get_registered_tools(self) -> List[Dict[str, Any]]:
        """List all tools metadata currently in the registry."""
        return list(self._tools_metadata.values())

tool_registry = ToolRegistry()
