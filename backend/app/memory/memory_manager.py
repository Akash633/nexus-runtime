from typing import Dict, Any, List

from app.db.memory_storage import MemoryStorage


class MemoryManager:
    """
    Memory Manager for Nexus Runtime.

    Responsible for creating, retrieving, searching,
    and managing contextual memories from previous
    AI executions.
    """

    def __init__(
        self,
        memory_storage: MemoryStorage | None = None
    ):
        self.memory_storage = (
            memory_storage
            if memory_storage is not None
            else MemoryStorage()
        )

    def remember(
        self,
        task: str,
        capability: str,
        agent_id: str,
        agent_name: str | None,
        execution_id: int | None,
        success: bool,
        latency_ms: float | None,
        full_response: str | None,
        summary: str | None
    ) -> int:
        """
        Store a new execution memory.
        """

        if not task or not task.strip():
            raise ValueError(
                "Task cannot be empty"
            )

        if not capability or not capability.strip():
            raise ValueError(
                "Capability cannot be empty"
            )

        if not agent_id or not agent_id.strip():
            raise ValueError(
                "Agent ID cannot be empty"
            )

        return self.memory_storage.save_memory(
            task=task,
            capability=capability,
            agent_id=agent_id,
            agent_name=agent_name,
            execution_id=execution_id,
            success=success,
            latency_ms=latency_ms,
            full_response=full_response,
            summary=summary
        )

    def get_memory(
        self,
        memory_id: int
    ) -> Dict[str, Any] | None:
        """
        Retrieve one memory by its ID.
        """

        if memory_id <= 0:
            raise ValueError(
                "Memory ID must be greater than 0"
            )

        return self.memory_storage.get_memory(
            memory_id
        )

    def get_recent_memories(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the most recent memories.
        """

        return self.memory_storage.get_recent_memories(
            limit=limit
        )

    def search(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search previous memories using a text query.
        """

        if not query or not query.strip():
            raise ValueError(
                "Search query cannot be empty"
            )

        return self.memory_storage.search_memories(
            query=query,
            limit=limit
        )

    def get_all_memories(
        self
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all stored memories.
        """

        return self.memory_storage.get_all_memories()

    def count(self) -> int:
        """
        Return the total number of stored memories.
        """

        return self.memory_storage.count()

    def clear(self) -> None:
        """
        Clear all stored memories.

        This is mainly useful for testing and
        development.
        """

        self.memory_storage.clear()