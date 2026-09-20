from typing import Dict, Any

from google import genai

from app.api.core.config import GEMINI_API_KEY
from app.providers.provider_base import AIProvider


class GeminiProvider(AIProvider):
    """
    Gemini implementation of the AIProvider interface.
    """

    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured")

        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def execute(
        self,
        task: str,
        capability: str
    ) -> Dict[str, Any]:

        if not task or not task.strip():
            raise ValueError("Task cannot be empty")

        response = self.client.models.generate_content(
            model="gemini-3.6-flash",
            contents=task
        )

        return {
            "success": True,
            "provider": "gemini",
            "capability": capability,
            "task": task,
            "result": response.text
        }