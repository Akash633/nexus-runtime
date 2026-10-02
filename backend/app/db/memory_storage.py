import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List


class MemoryStorage:
    """
    Persistent storage for Nexus Runtime memories.

    Stores contextual information about previous AI executions,
    including the task, selected agent, result, and performance.
    """

    def __init__(
        self,
        database_path: str | None = None
    ):
        if database_path is None:

            project_root = (
                Path(__file__).resolve().parents[2]
            )

            database_path = (
                project_root
                / "data"
                / "nexus_runtime.db"
            )

        self.database_path = Path(
            database_path
        )

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self._initialize_database()

    def _get_connection(self):

        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = sqlite3.Row

        return connection

    def _initialize_database(self):

        with self._get_connection() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    memory_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT NOT NULL,
                    capability TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    agent_name TEXT,
                    execution_id INTEGER,
                    success INTEGER NOT NULL,
                    latency_ms REAL,
                    full_response TEXT,
                    summary TEXT,
                    timestamp TEXT NOT NULL
                )
                """
            )

            connection.commit()

    def save_memory(
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

        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        with self._get_connection() as connection:

            cursor = connection.execute(
                """
                INSERT INTO memories (
                    task,
                    capability,
                    agent_id,
                    agent_name,
                    execution_id,
                    success,
                    latency_ms,
                    full_response,
                    summary,
                    timestamp
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task,
                    capability,
                    agent_id,
                    agent_name,
                    execution_id,
                    1 if success else 0,
                    latency_ms,
                    full_response,
                    summary,
                    timestamp
                )
            )

            connection.commit()

            return cursor.lastrowid

    def get_memory(
        self,
        memory_id: int
    ) -> Dict[str, Any] | None:

        with self._get_connection() as connection:

            row = connection.execute(
                """
                SELECT
                    memory_id,
                    task,
                    capability,
                    agent_id,
                    agent_name,
                    execution_id,
                    success,
                    latency_ms,
                    full_response,
                    summary,
                    timestamp
                FROM memories
                WHERE memory_id = ?
                """,
                (memory_id,)
            ).fetchone()

        if row is None:
            return None

        return self._row_to_dict(row)

    def get_all_memories(
        self
    ) -> List[Dict[str, Any]]:

        with self._get_connection() as connection:

            rows = connection.execute(
                """
                SELECT
                    memory_id,
                    task,
                    capability,
                    agent_id,
                    agent_name,
                    execution_id,
                    success,
                    latency_ms,
                    full_response,
                    summary,
                    timestamp
                FROM memories
                ORDER BY memory_id ASC
                """
            ).fetchall()

        return [
            self._row_to_dict(row)
            for row in rows
        ]

    def get_recent_memories(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:

        if limit <= 0:
            raise ValueError(
                "Limit must be greater than 0"
            )

        with self._get_connection() as connection:

            rows = connection.execute(
                """
                SELECT
                    memory_id,
                    task,
                    capability,
                    agent_id,
                    agent_name,
                    execution_id,
                    success,
                    latency_ms,
                    full_response,
                    summary,
                    timestamp
                FROM memories
                ORDER BY memory_id DESC
                LIMIT ?
                """,
                (limit,)
            ).fetchall()

        memories = [
            self._row_to_dict(row)
            for row in rows
        ]

        memories.reverse()

        return memories

    def search_memories(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:

        if not query or not query.strip():
            raise ValueError(
                "Search query cannot be empty"
            )

        if limit <= 0:
            raise ValueError(
                "Limit must be greater than 0"
            )

        search_pattern = f"%{query.strip()}%"

        with self._get_connection() as connection:

            rows = connection.execute(
                """
                SELECT
                    memory_id,
                    task,
                    capability,
                    agent_id,
                    agent_name,
                    execution_id,
                    success,
                    latency_ms,
                    full_response,
                    summary,
                    timestamp
                FROM memories
                WHERE
                    task LIKE ?
                    OR capability LIKE ?
                    OR agent_name LIKE ?
                    OR full_response LIKE ?
                    OR summary LIKE ?
                ORDER BY memory_id DESC
                LIMIT ?
                """,
                (
                    search_pattern,
                    search_pattern,
                    search_pattern,
                    search_pattern,
                    search_pattern,
                    limit
                )
            ).fetchall()

        return [
            self._row_to_dict(row)
            for row in rows
        ]

    def count(self) -> int:

        with self._get_connection() as connection:

            result = connection.execute(
                """
                SELECT COUNT(*)
                FROM memories
                """
            ).fetchone()

        return result[0]

    def clear(self) -> None:

        with self._get_connection() as connection:

            connection.execute(
                """
                DELETE FROM memories
                """
            )

            connection.commit()

    @staticmethod
    def _row_to_dict(
        row: sqlite3.Row
    ) -> Dict[str, Any]:

        return {
            "memory_id": row["memory_id"],
            "task": row["task"],
            "capability": row["capability"],
            "agent_id": row["agent_id"],
            "agent_name": row["agent_name"],
            "execution_id": row["execution_id"],
            "success": bool(row["success"]),
            "latency_ms": row["latency_ms"],
            "full_response": row["full_response"],
            "summary": row["summary"],
            "timestamp": row["timestamp"]
        }