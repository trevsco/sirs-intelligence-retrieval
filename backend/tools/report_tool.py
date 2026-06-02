import uuid
import time
from typing import List, Optional, Dict, Any
from mcp.protocol import MCPResponse
from mcp.tool_registry import tool_registry
from llm.ollama_client import ollama_client
from llm.prompt_templates import REPORT_SYSTEM_PROMPT, REPORT_PROMPT_TEMPLATE
from retrieval.rag_pipeline import rag_pipeline

@tool_registry.register(
    tool_name="generate_report",
    action="generate",
    description="Compile a highly structured technical assessment report based on context or retrieved segments.",
    schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string", 
                "description": "Topic or core research inquiry to generate a report for"
            },
            "context": {
                "type": "string", 
                "description": "Optional context text. If blank, retrieved segments will be formatted."
            },
            "chunks": {
                "type": "array", 
                "description": "Optional retrieved chunk structures passed down from previous steps"
            }
        },
        "required": ["query"]
    }
)
async def generate_report(
    query: str, 
    context: Optional[str] = "", 
    chunks: Optional[List[Dict[str, Any]]] = None
) -> MCPResponse:
    """Registered MCP tool to generate defense-style intelligence analysis reports."""
    start_time = time.perf_counter()
    msg_id = str(uuid.uuid4())
    
    final_context = context or ""
    sources = set()
    
    # Unpack chunks if provided by previous pipeline steps
    if chunks:
        context_parts = []
        for c in chunks:
            text_val = c.get("text", "")
            if text_val:
                context_parts.append(text_val)
            filename = c.get("filename")
            if filename:
                sources.add(filename)
        final_context = "\n\n=== SOURCE SEGMENT ===\n" + "\n\n=== SOURCE SEGMENT ===\n".join(context_parts)
    
    # If context is still empty, perform fallback retrieval directly in tool
    if not final_context.strip():
        logger_name = "generate_report_tool"
        from loguru import logger
        logger.info("Report tool context was empty. Performing fallback retrieval.")
        rag_res = rag_pipeline.run(query=query)
        final_context = rag_res["context"]
        sources = set(rag_res["sources"])
        
    try:
        prompt = REPORT_PROMPT_TEMPLATE.format(query=query, context=final_context)
        report_text = await ollama_client.generate(
            prompt=prompt, 
            system_prompt=REPORT_SYSTEM_PROMPT
        )
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        response_data = {
            "report": report_text,
            "sources": sorted(list(sources))
        }
        
        return MCPResponse.make_success(
            message_id=msg_id,
            tool_name="generate_report",
            action="generate",
            data=response_data,
            execution_time_ms=elapsed_ms
        )
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return MCPResponse.make_error(
            message_id=msg_id,
            tool_name="generate_report",
            action="generate",
            error_detail=f"Report generation tool error: {str(e)}",
            execution_time_ms=elapsed_ms
        )
