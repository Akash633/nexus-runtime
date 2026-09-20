from typing import Dict, Any

from openai import OpenAI

from app.api.core.config import OPENAI_API_KEY
from app.providers.provider_base import AIProvider


class OpenAIProvider(AIProvider):
    """
    OpenAI implementation of the AIProvider interface.
    """

    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured")

        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def execute(
        self,
        task: str,
        capability: str
    ) -> Dict[str, Any]:

        if not task or not task.strip():
            raise ValueError("Task cannot be empty")

        response = self.client.responses.create(
            model="gpt-5.6-luna",
            input=task
        )

        return {
            "success": True,
            "provider": "openai",
            "capability": capability,
            "task": task,
            "result": response.output_text
        }