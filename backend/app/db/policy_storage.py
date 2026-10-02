import sqlite3
from pathlib import Path
from typing import Dict, Any


class PolicyStorage:
    """
    Persistent storage for Nexus Runtime policy configuration.
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
                CREATE TABLE IF NOT EXISTS policy_config (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    allowed_agents TEXT NOT NULL,
                    blocked_agents TEXT NOT NULL,
                    preferred_max_cost REAL
                )
                """
            )

            connection.commit()

    def save_policy(
        self,
        policy: Dict[str, Any]
    ) -> None:

        import json

        allowed_agents = json.dumps(
            policy.get("hard", {}).get(
                "allowed_agents", []
            )
        )

        blocked_agents = json.dumps(
            policy.get("hard", {}).get(
                "blocked_agents", []
            )
        )

        preferred_max_cost = (
            policy.get("soft", {}).get(
                "preferred_max_cost"
            )
        )

        with self._get_connection() as connection:

            connection.execute(
                """
                INSERT INTO policy_config (
                    id,
                    allowed_agents,
                    blocked_agents,
                    preferred_max_cost
                )
                VALUES (1, ?, ?, ?)

                ON CONFLICT(id)
                DO UPDATE SET
                    allowed_agents = excluded.allowed_agents,
                    blocked_agents = excluded.blocked_agents,
                    preferred_max_cost =
                        excluded.preferred_max_cost
                """,
                (
                    allowed_agents,
                    blocked_agents,
                    preferred_max_cost
                )
            )

            connection.commit()

    def load_policy(self) -> Dict[str, Any] | None:

        import json

        with self._get_connection() as connection:

            row = connection.execute(
                """
                SELECT
                    allowed_agents,
                    blocked_agents,
                    preferred_max_cost
                FROM policy_config
                WHERE id = 1
                """
            ).fetchone()

        if row is None:
            return None

        return {
            "hard": {
                "allowed_agents": json.loads(
                    row["allowed_agents"]
                ),
                "blocked_agents": json.loads(
                    row["blocked_agents"]
                )
            },
            "soft": {
                "preferred_max_cost": (
                    row["preferred_max_cost"]
                )
            }
        }