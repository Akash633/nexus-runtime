from typing import Dict, Any

from groq import Groq

from app.api.core.config import GROQ_API_KEY
from app.providers.provider_base import AIProvider


class GroqProvider(AIProvider):
    """
    Groq implementation of the AIProvider interface.
    """

    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not configured")

        self.client = Groq(api_key=GROQ_API_KEY)

    def execute(
        self,
        task: str,
        capability: str
    ) -> Dict[str, Any]:

        if not task or not task.strip():
            raise ValueError("Task cannot be empty")

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": task
                }
            ]
        )

        return {
            "success": True,
            "provider": "groq",
            "capability": capability,
            "task": task,
            "result": response.choices[0].message.content
        }