import uuid
import time
from typing import Dict, Any
from loguru import logger
from agent.planner import agent_planner
from agent.tool_router import tool_router

class AgentController:
    async def handle_query(
        self, 
        query: str, 
        top_k: int = 5, 
        threshold: float = 0.0
    ) -> Dict[str, Any]:
        """
        Main query entrypoint for the SIRS agent:
        1. Invokes the AgentPlanner to generate a sequential tool plan.
        2. Routes the plan to the ToolRouter to execute the actions and collect trace.
        3. Parses execution context to construct a structured query response.
        """
        start_time = time.perf_counter()
        session_id = str(uuid.uuid4())
        
        logger.info(f"Received query session: {session_id} - Query: '{query}'")
        
        # 1. Generate execution plan (LLM or rule-based)
        plan = await agent_planner.plan(query)
        
        # 2. Execute plan using the tool router
        execution_results = await tool_router.execute_plan(
            plan=plan,
            query=query,
            top_k=top_k,
            threshold=threshold
        )
        
        context = execution_results["context"]
        tool_trace = execution_results["tool_trace"]
        
        # 3. Formulate the final user-facing answer
        if "error_detail" in context:
            answer = f"An execution error occurred in the toolchain: {context['error_detail']}"
        elif "report" in context:
            answer = context["report"]
        elif "last_result" in context and isinstance(context["last_result"], str):
            answer = context["last_result"]
        elif "context" in context and context["context"]:
            # If retrieve only ran
            answer = f"The following relevant document snippets were retrieved from the offline archive:\n\n{context['context']}"
        else:
            answer = "No relevant intelligence segments were found in the offline repository."
            
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        response_payload = {
            "session_id": session_id,
            "query": query,
            "answer": answer,
            "plan": plan,
            "tool_trace": tool_trace,
            "sources": context.get("sources", []),
            "chunks": context.get("chunks", []),
            "confidence": context.get("confidence", 0.0),
            "num_chunks_retrieved": len(context.get("chunks", [])),
            "elapsed_ms": round(elapsed_ms, 2)
        }
        
        logger.info(f"Query session {session_id} completed successfully in {elapsed_ms:.2f}ms.")
        return response_payload

agent_controller = AgentController()
