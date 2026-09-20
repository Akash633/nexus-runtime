from abc import ABC, abstractmethod
from typing import Dict, Any


class AIProvider(ABC):
    """
    Base interface for all AI providers.
    """

    @abstractmethod
    def execute(
        self,
        task: str,
        capability: str
    ) -> Dict[str, Any]:
        """
        Execute an AI task and return the result.
        """
        pass