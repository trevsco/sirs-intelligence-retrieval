"""
llm/ollama_client.py
---------------------
Optimized Ollama client for SIRS.

Key optimizations:
1. Structured, defense-context system prompt for better answer quality
2. Request timeout to prevent hanging queries
3. Graceful fallback if Ollama is slow or offline
4. Cleaner prompt formatting for more accurate retrieval-based answers
"""

import httpx
from loguru import logger
from config import settings

# ── Timeout settings ──────────────────────────────────────────────────────────
# 180 seconds for generation — phi4-mini on CPU can be slow
# 10 seconds for status checks
GENERATION_TIMEOUT = 180
STATUS_TIMEOUT     = 10

# ── System prompt ─────────────────────────────────────────────────────────────
# This is the most impactful optimization.
# A structured system prompt gives dramatically better, more focused answers.
SYSTEM_PROMPT = """
You are SIRS — a Secure Intelligence Retrieval System designed for defense and research operations.

Your role is to answer questions strictly based on the provided document context.

Rules you must follow:

1. Answer ONLY from the provided context.
2. If the context does not contain the answer, say:
"The indexed documents do not contain sufficient information to answer this query."

3. Be precise and factual.

4. Combine information from multiple document sections whenever necessary.

5. Structure answers clearly using paragraphs and bullet points.

6. Explain concepts completely instead of giving one-line answers.

7. Cite document names whenever possible.

8. Do not speculate or invent facts.

Classification:
UNCLASSIFIED // DEVELOPMENT
"""


class OllamaClient:
    """
    Optimized HTTP client for local Ollama LLM inference.
    """

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model    = settings.OLLAMA_MODEL

    def _build_prompt(self, query: str, context: str) -> str:
        """
        Build a well-structured prompt.
        Structured prompts give significantly better answers than raw concatenation.
        """
        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"{'='*60}\n"
            f"DOCUMENT CONTEXT:\n"
            f"{'='*60}\n"
            f"{context.strip()}\n\n"
            f"{'='*60}\n"
            f"INTELLIGENCE QUERY:\n"
            f"{'='*60}\n"
            f"{query.strip()}\n\n"
            f"ANSWER (based strictly on the context above):"
        )

    async def generate(self, query: str, context: str) -> str:
        """
        Generate an answer using the local Ollama LLM.

        Optimizations:
        - Structured system prompt for better quality
        - Explicit timeout to prevent hanging
        - Graceful error message if Ollama is unavailable
        """
        prompt = self._build_prompt(query, context)

        try:
            async with httpx.AsyncClient(timeout=GENERATION_TIMEOUT) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model":  self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": settings.LLM_TEMPERATURE,
                            "num_predict": settings.LLM_MAX_TOKENS,
                            # Additional options for better quality output
                            "top_p":       0.9,    # nucleus sampling
                            "repeat_penalty": 1.1, # reduce repetition
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                answer = result.get("response", "").strip()

                if not answer:
                    return "The system generated an empty response. Please rephrase your query."

                return answer

        except httpx.TimeoutException:
            logger.error("Ollama generation timed out after 120 seconds")
            return "Query timed out. The LLM is taking too long. Try a simpler query or restart Ollama."

        except httpx.ConnectError:
            logger.error("Cannot connect to Ollama — is it running?")
            return "LLM offline. Please ensure Ollama is running: 'ollama serve'"

        except Exception as e:
            logger.exception(f"Ollama generation failed: {e}")
            return f"LLM error: {str(e)}"

    async def get_status(self) -> dict:
        """
        Check Ollama server status and available models.
        """
        try:
            async with httpx.AsyncClient(timeout=STATUS_TIMEOUT) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                data   = response.json()
                models = [m["name"] for m in data.get("models", [])]
                return {
                    "online":                    True,
                    "models":                    models,
                    "configured_model_available": self.model in models,
                }

        except httpx.ConnectError:
            return {
                "online":                    False,
                "models":                    [],
                "configured_model_available": False,
            }
        except Exception as e:
            logger.warning(f"Ollama status check failed: {e}")
            return {
                "online":                    False,
                "models":                    [],
                "configured_model_available": False,
            }


# Module-level singleton
ollama_client = OllamaClient()
