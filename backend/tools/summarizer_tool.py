import uuid
import time
from mcp.protocol import MCPResponse
from mcp.tool_registry import tool_registry
from llm.ollama_client import ollama_client
from llm.prompt_templates import SUMMARIZATION_SYSTEM_PROMPT, SUMMARIZATION_PROMPT_TEMPLATE

@tool_registry.register(
    tool_name="summarize_results",
    action="summarize",
    description="Synthesize a dense, technical, objective summary of the retrieved document snippets.",
    schema={
        "type": "object",
        "properties": {
            "text": {
                "type": "string", 
                "description": "Context snippets or unstructured text to summarize"
            },
            "max_length": {
                "type": "integer", 
                "description": "Maximum length constraints", 
                "default": 250
            }
        },
        "required": ["text"]
    }
)
async def summarize_results(text: str, max_length: int = 250) -> MCPResponse:
    """Registered MCP tool to generate summaries of context text."""
    start_time = time.perf_counter()
    msg_id = str(uuid.uuid4())
    
    if not text or not text.strip():
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return MCPResponse.make_success(
            message_id=msg_id,
            tool_name="summarize_results",
            action="summarize",
            data="No text content was available to summarize.",
            execution_time_ms=elapsed_ms
        )
        
    try:
        prompt = SUMMARIZATION_PROMPT_TEMPLATE.format(text=text)
        summary = await ollama_client.generate(
            prompt=prompt, 
            system_prompt=SUMMARIZATION_SYSTEM_PROMPT
        )
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return MCPResponse.make_success(
            message_id=msg_id,
            tool_name="summarize_results",
            action="summarize",
            data=summary,
            execution_time_ms=elapsed_ms
        )
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return MCPResponse.make_error(
            message_id=msg_id,
            tool_name="summarize_results",
            action="summarize",
            error_detail=f"Summarizer tool error: {str(e)}",
            execution_time_ms=elapsed_ms
        )
