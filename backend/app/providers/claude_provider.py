from typing import Dict, Any

from anthropic import Anthropic

from app.api.core.config import ANTHROPIC_API_KEY
from app.providers.provider_base import AIProvider


class ClaudeProvider(AIProvider):
    """
    Anthropic Claude implementation of the AIProvider interface.
    """

    def __init__(self):
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not configured")

        self.client = Anthropic(
            api_key=ANTHROPIC_API_KEY
        )

    def execute(
        self,
        task: str,
        capability: str
    ) -> Dict[str, Any]:

        if not task or not task.strip():
            raise ValueError("Task cannot be empty")

        response = self.client.messages.create(
            model="claude-opus-5",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": task
                }
            ]
        )

        result = ""

        for block in response.content:
            if block.type == "text":
                result += block.text

        return {
            "success": True,
            "provider": "anthropic",
            "capability": capability,
            "task": task,
            "result": result
        }