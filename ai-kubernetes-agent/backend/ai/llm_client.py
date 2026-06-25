import httpx
from typing import Any
from loguru import logger

from ..core.config import settings


class LLMClient:
    """Client for OpenRouter LLM API."""

    def __init__(self):
        """Initialize LLM client."""
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model
        self.base_url = "https://openrouter.ai/api/v1"
        self.timeout = 60  # seconds

    async def generate(self, prompt: str) -> dict[str, Any]:
        """
        Generate response from LLM.

        Args:
            prompt: The prompt to send to LLM

        Returns:
            Dictionary with response content and metadata
        """
        if not self.api_key:
            logger.error("OpenRouter API key not configured")
            return {
                "success": False,
                "error": "OpenRouter API key not configured",
                "content": "",
            }

        logger.info(f"Sending prompt to LLM (model: {self.model})")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-kubernetes-agent.com",
            "X-Title": "AI Kubernetes Agent",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,  # Low temperature for consistent, focused responses
            "max_tokens": 2000,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )

                if response.status_code != 200:
                    logger.error(f"LLM API error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}",
                        "content": "",
                    }

                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

                logger.info("LLM response received successfully")
                return {
                    "success": True,
                    "content": content,
                    "model": self.model,
                }

        except httpx.TimeoutException:
            logger.error("LLM API request timed out")
            return {
                "success": False,
                "error": "Request timed out",
                "content": "",
            }

        except Exception as e:
            logger.error(f"LLM API request failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content": "",
            }