import httpx
from typing import Optional, Dict, Any, List
from loguru import logger
from config import settings
import time

class OllamaClient:
    def __init__(self) -> None:
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL

    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        format_type: Optional[str] = None
    ) -> str:
        """
        Send a generation request to the local Ollama LLM endpoint.
        Returns the generated string.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": settings.LLM_TEMPERATURE,
                "num_predict": settings.LLM_MAX_TOKENS
            }
        }
        if system_prompt:
            payload["system"] = system_prompt
        if format_type:
            # Ollama supports format="json" to force JSON schema output
            payload["format"] = format_type

        try:
            logger.info(f"Dispatching prompt to Ollama model='{self.model}'...")
            logger.info(
                f"Prompt length: {len(prompt)} chars | "
                f"Model: {self.model} | "
                f"Max Tokens: {settings.LLM_MAX_TOKENS}"
            )

            start_time = time.time()

            async with httpx.AsyncClient(timeout=300) as client:
                response = await client.post(url, json=payload)

            elapsed_time = time.time() - start_time

            logger.info(
                f"Ollama request completed in {elapsed_time:.2f} seconds"
            )

            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "").strip()
                logger.info(
                    f"Ollama response generated successfully. "
                    f"Output length: {len(response_text)} chars"
                )
                return response_text
            else:
                err_msg = f"Ollama generation failed with status code {response.status_code}: {response.text}"
                logger.error(err_msg)
                raise Exception(err_msg)

        except Exception as e:
            logger.error(f"Error communicating with local Ollama service: {e}")
            raise RuntimeError(
                f"Local LLM (Ollama) at {self.base_url} is unreachable or returned an error. "
                "Ensure Ollama is running and the model is pulled."
            ) from e

    async def get_status(self) -> Dict[str, Any]:
        """Verify if the Ollama service is reachable and return installed models."""
        url = f"{self.base_url}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    models_data = response.json().get("models", [])
                    models = [m["name"] for m in models_data]
                    # Check if the configured model is installed (could have version suffix like ':latest')
                    is_model_available = any(
                        self.model in m or m.startswith(self.model)
                        for m in models
                    )
                    return {
                        "online": True,
                        "models": models,
                        "configured_model": self.model,
                        "configured_model_available": is_model_available,
                        "error_detail": None
                    }
                else:
                    return {
                        "online": False,
                        "models": [],
                        "configured_model": self.model,
                        "configured_model_available": False,
                        "error_detail": f"Ollama API returned HTTP {response.status_code}"
                    }
        except Exception as e:
            return {
                "online": False,
                "models": [],
                "configured_model": self.model,
                "configured_model_available": False,
                "error_detail": f"Could not reach Ollama at {self.base_url}. Error: {str(e)}"
            }

ollama_client = OllamaClient()