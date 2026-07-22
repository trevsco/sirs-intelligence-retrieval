"""
llm/ollama_client.py
---------------------
Optimized Ollama client for SIRS.
"""

from click import prompt
import httpx
from loguru import logger
from config import settings

# ── Timeout settings ──────────────────────────────────────────────────────────
GENERATION_TIMEOUT = 600
STATUS_TIMEOUT = 10

# ── System prompt ─────────────────────────────────────────────────────────────
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

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL

    def _build_prompt(self, query: str, context: str) -> str:
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
        Existing RAG generation (used by chat).
        """

        prompt = self._build_prompt(query, context)

        try:
            async with httpx.AsyncClient(timeout=GENERATION_TIMEOUT) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "num_predict": 1024,
                            "top_p": 0.85,
                            "repeat_penalty": 1.15,
                            "num_ctx": 16384
                        }
                    }
                )

                response.raise_for_status()

                result = response.json()

                answer = result.get("response", "").strip()

                if not answer:
                    return "The system generated an empty response."

                return answer

        except httpx.TimeoutException:
            logger.error("Ollama generation timed out")
            return "Query timed out."

        except httpx.ConnectError:
            logger.error("Cannot connect to Ollama")
            return "LLM offline. Please start Ollama."

        except Exception as e:
            logger.exception(f"Ollama generation failed: {e}")
            return f"LLM error: {str(e)}"

    async def generate_analysis(self, prompt: str) -> str:
        """
        Used ONLY for Document Analysis.
        No RAG system prompt is added.
        """

        try:
            async with httpx.AsyncClient(timeout=GENERATION_TIMEOUT) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            # Lower temperature for more factual responses
                            "temperature": 0.1,

                            # Limit output length for faster CPU inference
                            "num_predict": 2000,

                            # More focused generation
                            "top_p": 0.85,

                            # Reduce repetition
                            "repeat_penalty": 1.25,

                            # Increase context window
                            "num_ctx": 16384
                        }   
                    }
                )

                response.raise_for_status()

                result = response.json()

                print("\n========== RAW OLLAMA RESPONSE ==========\n")
                print(result)
                print("\n========== END RAW RESPONSE ==========\n")

                answer = result.get("response", "").strip()

                print("\n========== MODEL OUTPUT ==========\n")
                print(answer)
                print("\n========== END MODEL OUTPUT ==========\n")

                print("Prompt length:", len(prompt))
                print(prompt[-1000:])
                if not answer:
                    return "The system generated an empty response."


                return answer

        except httpx.TimeoutException:
            logger.error("Analysis timed out")
            return "Analysis timed out."

        except httpx.ConnectError:
            logger.error("Cannot connect to Ollama")
            return "LLM offline. Please start Ollama."

        except Exception as e:
            logger.exception(f"Analysis generation failed: {e}")
            return f"LLM error: {str(e)}"

    async def get_status(self) -> dict:
        try:
            async with httpx.AsyncClient(timeout=STATUS_TIMEOUT) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()

                data = response.json()

                models = [m["name"] for m in data.get("models", [])]

                return {
                    "online": True,
                    "models": models,
                    "configured_model_available": self.model in models
                }

        except httpx.ConnectError:
            return {
                "online": False,
                "models": [],
                "configured_model_available": False
            }

        except Exception as e:
            logger.warning(f"Ollama status check failed: {e}")
            return {
                "online": False,
                "models": [],
                "configured_model_available": False
            }


ollama_client = OllamaClient()