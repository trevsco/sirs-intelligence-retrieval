import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field

class ToolStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    NOT_FOUND = "not_found"

class MCPMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tool_name: str
    action: str
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

class MCPResponse(BaseModel):
    message_id: str
    tool_name: str
    action: str
    status: ToolStatus
    data: Any = None
    error_detail: Optional[str] = None  # MUST be named error_detail to prevent Pydantic V2 conflicts
    execution_time_ms: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def make_success(
        cls, 
        message_id: str, 
        tool_name: str, 
        action: str, 
        data: Any = None, 
        execution_time_ms: float = 0.0, 
        metadata: Optional[dict[str, Any]] = None
    ) -> "MCPResponse":
        """Factory method for successful tool execution response."""
        return cls(
            message_id=message_id,
            tool_name=tool_name,
            action=action,
            status=ToolStatus.SUCCESS,
            data=data,
            execution_time_ms=execution_time_ms,
            metadata=metadata or {}
        )
    
    @classmethod
    def make_error(
        cls, 
        message_id: str, 
        tool_name: str, 
        action: str, 
        error_detail: str, 
        execution_time_ms: float = 0.0, 
        metadata: Optional[dict[str, Any]] = None
    ) -> "MCPResponse":
        """Factory method for failed tool execution response."""
        return cls(
            message_id=message_id,
            tool_name=tool_name,
            action=action,
            status=ToolStatus.ERROR,
            error_detail=error_detail,
            execution_time_ms=execution_time_ms,
            metadata=metadata or {}
        )
