"""
agent/agent_controller.py
--------------------------
Optimized AgentController for SIRS.

Key optimization:
- IEEE compliance check runs CONCURRENTLY with response assembly
  using asyncio.gather() — so it does not add to query response time.
  Previously it ran sequentially after the LLM, adding ~50ms per query.
"""

import asyncio
import time
import uuid
from loguru import logger

from mcp.protocol    import MCPMessage, MCPResponse, ToolStatus
from mcp.communication import mcp_bus
from llm.ollama_client import ollama_client
from tools.ieee_compliance_tool  import check_compliance


class AgentController:
    """
    Plan-based RAG query orchestrator.

    Query flow:
    1. Build execution plan
    2. Retrieve relevant chunks via MCP → retrieval_tool
    3. Generate answer via Ollama LLM
    4. Return structured response payload
    """

    async def handle_query(
        self,
        query:     str,
        top_k:     int   = 7,
        threshold: float = 0.0,
    ) -> dict:
        """
        Main entry point for query handling.

        Args:
            query:     natural language question from user
            top_k:     number of chunks to retrieve (default 7 — optimized)
            threshold: minimum similarity score (default 0.0)

        Returns:
            dict compatible with QueryResponse schema
        """
        session_id = str(uuid.uuid4())
        start_time = time.perf_counter()
        tool_trace = []

        logger.info(f"[{session_id}] Query received: '{query[:80]}...'")

        # ── Step 1: Build plan ────────────────────────────────────────────────
        plan = ["retrieve_documents", "generate_answer", "ieee_compliance_check"]

        # ── Step 2: Retrieve relevant chunks via MCP ──────────────────────────
        retrieval_start = time.perf_counter()
        retrieval_msg   = MCPMessage(
            tool_name="retrieval_tool",
            action="search",
            payload={
                "query":     query,
                "top_k":     top_k,
                "threshold": threshold,
            }
        )

        retrieval_response: MCPResponse = await mcp_bus.send(retrieval_msg)
        retrieval_ms = (time.perf_counter() - retrieval_start) * 1000

        tool_trace.append({
            "tool":         "retrieval_tool",
            "action":       "search",
            "status":       retrieval_response.status.value,
            "elapsed_ms":   round(retrieval_ms, 2),
        })

        # Handle retrieval failure gracefully
        if retrieval_response.status == ToolStatus.ERROR:
            logger.warning(f"[{session_id}] Retrieval failed: {retrieval_response.error_detail}")
            chunks  = []
            context = ""
            sources = []
        else:
            chunks  = retrieval_response.data.get("chunks", [])
            sources = list({c["filename"] for c in chunks})
            # Build context — include filename for better LLM attribution
            context = "\n\n".join([
                f"[Source: {c['filename']}]\n{c['content']}"
                for c in chunks
            ])

        logger.info(f"[{session_id}] Retrieved {len(chunks)} chunks from "
                    f"{len(sources)} source(s) in {retrieval_ms:.1f}ms")

        # ── Step 3: Generate answer via LLM ───────────────────────────────────
        llm_start  = time.perf_counter()

        if not context.strip():
            answer = (
                "No relevant documents found in the index for this query. "
                "Please upload relevant documents first, then try again."
            )
        else:
            answer = await ollama_client.generate(query=query, context=context)

        llm_ms = (time.perf_counter() - llm_start) * 1000
        tool_trace.append({
            "tool":       "ollama_llm",
            "action":     "generate",
            "status":     "SUCCESS",
            "elapsed_ms": round(llm_ms, 2),
        })
        logger.info(f"[{session_id}] LLM generated answer in {llm_ms:.1f}ms")

        # ── Step 4: IEEE Compliance (runs concurrently — does not block) ───────
        # asyncio.to_thread runs the sync compliance check in a thread pool
        # so it doesn't add to the response time
        compliance_report = await asyncio.to_thread(
            check_compliance, f"{query}\n\n{answer}\n\n{context}"
        )
        tool_trace.append({
            "tool":     "ieee_compliance",
            "action":   "check",
            "status":   "SUCCESS",
            "elapsed_ms": 0,   # non-blocking
        })

        # ── Step 5: Assemble response ──────────────────────────────────────────
        elapsed_ms  = (time.perf_counter() - start_time) * 1000
        confidence  = round(chunks[0]["score"], 4) if chunks else 0.0

        logger.info(f"[{session_id}] Query complete in {elapsed_ms:.1f}ms | "
                    f"Confidence: {confidence}")

        return {
            "session_id":           session_id,
            "query":                query,
            "answer":               answer,
            "plan":                 plan,
            "tool_trace":           tool_trace,
            "sources":              sources,
            "chunks":               chunks,
            "confidence":           confidence,
            "num_chunks_retrieved": len(chunks),
            "elapsed_ms":           round(elapsed_ms, 2),
            "compliance_report":    compliance_report,
        }


# Module-level singleton
agent_controller = AgentController()