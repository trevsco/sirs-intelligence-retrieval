import re
import json
from typing import List
from loguru import logger
from config import settings
from llm.ollama_client import ollama_client
from llm.prompt_templates import PLANNER_SYSTEM_PROMPT, PLANNER_PROMPT_TEMPLATE
from mcp.tool_registry import tool_registry

class AgentPlanner:
    def __init__(self) -> None:
        # All valid tools currently in registry
        self.allowed_tools = {
            "retrieve_documents", 
            "summarize_results", 
            "generate_report", 
            "upload_document", 
            "list_documents"
        }

    async def plan(self, query: str) -> List[str]:
        logger.info(f"Generating execution plan for inquiry: '{query}'")

        query_lower = query.lower()

        if any(
            k in query_lower
            for k in [
                "analyze",
                "analysis",
                "summary",
                "summarize",
                "summarise",
                "key takeaways",
                "overview",
                "brief"
            ]
        ):
            plan = ["retrieve_documents", "summarize_results"]
            logger.info(f"Forced Agent Plan: {plan}")
            return plan

        try:
            prompt = PLANNER_PROMPT_TEMPLATE.format(query=query)

            llm_output = await ollama_client.generate(
                prompt=prompt,
                system_prompt=PLANNER_SYSTEM_PROMPT,
                format_type="json"
            )

            logger.info(f"Raw Planner LLM Output: {llm_output}")

            match = re.search(
                r'(\[\s*".*?"\s*(?:,\s*".*?"\s*)*\])',
                llm_output,
                re.DOTALL
            )

            if match:
                array_str = match.group(1)
                plan = json.loads(array_str)
            else:
                plan = json.loads(llm_output)

            if isinstance(plan, list) and len(plan) > 0:

                validated_plan = [
                    tool
                    for tool in plan
                    if tool in self.allowed_tools
                ]

                validated_plan = [
                    tool
                    for tool in validated_plan
                    if tool != "generate_report"
                ]

                if validated_plan:
                    logger.info(
                        f"Accepted LLM Agent Plan: {validated_plan}"
                    )
                    return validated_plan

        except Exception as e:
            logger.warning(
                f"LLM planner failed: {e}. Executing rule-based fallback strategy."
            )

        if any(
            k in query_lower
            for k in [
                "upload",
                "ingest",
                "add file",
                "index file",
                "insert"
            ]
        ):
            plan = ["upload_document"]

        elif any(
            k in query_lower
            for k in [
                "list",
                "show documents",
                "all documents",
                "all files",
                "show files"
            ]
        ):
            plan = ["list_documents"]

        elif any(
            k in query_lower
            for k in [
                "report",
                "analysis",
                "assessment",
                "write-up",
                "detailed brief"
            ]
        ):
            plan = ["retrieve_documents", "summarize_results"]

        elif any(
            k in query_lower
            for k in [
                "summarise",
                "summarize",
                "brief",
                "summary",
                "gist"
            ]
        ):
            plan = ["retrieve_documents", "summarize_results"]

        else:
            plan = ["retrieve_documents", "summarize_results"]

        logger.info(f"Fallback Agent Plan: {plan}")
        return plan

agent_planner = AgentPlanner()
