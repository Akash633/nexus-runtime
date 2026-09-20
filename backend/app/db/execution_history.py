import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List


class ExecutionHistory:
    """
    Persistent storage for Nexus Runtime execution history.
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
                CREATE TABLE IF NOT EXISTS execution_history (
                    execution_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    latency_ms REAL NOT NULL,
                    success INTEGER NOT NULL,
                    error TEXT,
                    timestamp TEXT NOT NULL
                )
                """
            )

            connection.commit()

    def record_execution(
        self,
        agent_id: str,
        latency_ms: float,
        success: bool,
        error: str | None = None
    ) -> int:

        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        with self._get_connection() as connection:

            cursor = connection.execute(
                """
                INSERT INTO execution_history (
                    agent_id,
                    latency_ms,
                    success,
                    error,
                    timestamp
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    agent_id,
                    latency_ms,
                    1 if success else 0,
                    error,
                    timestamp
                )
            )

            connection.commit()

            return cursor.lastrowid

    def get_all(
        self
    ) -> List[Dict[str, Any]]:

        with self._get_connection() as connection:

            rows = connection.execute(
                """
                SELECT
                    execution_id,
                    agent_id,
                    latency_ms,
                    success,
                    error,
                    timestamp
                FROM execution_history
                ORDER BY execution_id ASC
                """
            ).fetchall()

        return [
            {
                "execution_id": row["execution_id"],
                "agent_id": row["agent_id"],
                "latency_ms": row["latency_ms"],
                "success": bool(row["success"]),
                "error": row["error"],
                "timestamp": row["timestamp"]
            }
            for row in rows
        ]

    def get_agent_stats(
        self,
        agent_id: str
    ) -> Dict[str, Any]:
        """
        Calculate performance statistics
        for one agent.
        """

        with self._get_connection() as connection:

            row = connection.execute(
                """
                SELECT
                    COUNT(*) AS total_executions,

                    SUM(
                        CASE
                            WHEN success = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS successful_executions,

                    SUM(
                        CASE
                            WHEN success = 0
                            THEN 1
                            ELSE 0
                        END
                    ) AS failed_executions,

                    AVG(latency_ms) AS average_latency_ms

                FROM execution_history

                WHERE agent_id = ?
                """,
                (agent_id,)
            ).fetchone()

        total = row["total_executions"] or 0
        successful = (
            row["successful_executions"] or 0
        )
        failed = (
            row["failed_executions"] or 0
        )

        average_latency = (
            row["average_latency_ms"]
            if row["average_latency_ms"]
            is not None
            else 0.0
        )

        if total > 0:

            success_rate = (
                successful / total
            ) * 100

        else:

            success_rate = 0.0

        return {
            "agent_id": agent_id,
            "total_executions": total,
            "successful_executions": successful,
            "failed_executions": failed,
            "success_rate": round(
                success_rate,
                2
            ),
            "average_latency_ms": round(
                average_latency,
                2
            )
        }

    def get_all_agent_stats(
        self
    ) -> List[Dict[str, Any]]:
        """
        Calculate performance statistics
        for every agent that has execution history.
        """

        with self._get_connection() as connection:

            rows = connection.execute(
                """
                SELECT DISTINCT agent_id
                FROM execution_history
                ORDER BY agent_id
                """
            ).fetchall()

        return [
            self.get_agent_stats(
                row["agent_id"]
            )
            for row in rows
        ]

    def count(self) -> int:

        with self._get_connection() as connection:

            result = connection.execute(
                """
                SELECT COUNT(*)
                FROM execution_history
                """
            ).fetchone()

        return result[0]

    def clear(self):

        with self._get_connection() as connection:

            connection.execute(
                """
                DELETE FROM execution_history
                """
            )

            connection.commit()