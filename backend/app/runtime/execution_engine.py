import time
from typing import Dict, Any

from app.providers.openai_provider import OpenAIProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.groq_provider import GroqProvider
from app.db.execution_history import ExecutionHistory


class ExecutionEngine:
    """
    Executes tasks using the agent selected by the Decision Engine.

    Execution results are stored persistently so Nexus
    can learn from previous executions even after
    server restarts.
    """

    def __init__(
        self,
        execution_history: ExecutionHistory | None = None
    ):

        self.execution_history = (
            execution_history
            if execution_history is not None
            else ExecutionHistory()
        )

        self.latency_history = (
            self.execution_history.get_all()
        )

        self.openai_provider = OpenAIProvider()
        self.gemini_provider = GeminiProvider()
        self.groq_provider = GroqProvider()

    def _record_execution(
        self,
        agent_id: str,
        latency_ms: float,
        success: bool,
        error: str | None = None
    ) -> int:

        execution_id = (
            self.execution_history.record_execution(
                agent_id=agent_id,
                latency_ms=latency_ms,
                success=success,
                error=error
            )
        )

        self.latency_history.append({
            "execution_id": execution_id,
            "agent_id": agent_id,
            "latency_ms": latency_ms,
            "success": success,
            "error": error
        })

        return execution_id

    def execute(
        self,
        agent: Dict[str, Any],
        task: str,
        capability: str,
        simulate_failure: bool = False
    ) -> Dict[str, Any]:

        if not task or not task.strip():
            raise ValueError(
                "Task cannot be empty"
            )

        agent_id = agent.get("id")
        agent_name = agent.get("name")

        if not agent_id:
            raise ValueError(
                "Invalid agent: missing agent id"
            )

        if capability not in agent.get(
            "capabilities",
            []
        ):
            raise ValueError(
                f"Agent '{agent_id}' does not support "
                f"capability '{capability}'"
            )

        start_time = time.perf_counter()

        try:

            if simulate_failure:

                raise RuntimeError(
                    f"Simulated failure for {agent_id}"
                )

            if agent_id == "gpt-agent":

                provider_result = (
                    self.openai_provider.execute(
                        task=task,
                        capability=capability
                    )
                )

            elif agent_id == "gemini-agent":

                provider_result = (
                    self.gemini_provider.execute(
                        task=task,
                        capability=capability
                    )
                )

            elif agent_id == "groq-agent":

                provider_result = (
                    self.groq_provider.execute(
                        task=task,
                        capability=capability
                    )
                )

            else:

                provider_result = {
                    "success": True,
                    "provider": "mock",
                    "capability": capability,
                    "task": task,
                    "result": (
                        f"Mock execution by {agent_name}. "
                        f"Real provider integration is "
                        f"not available yet."
                    )
                }

            end_time = time.perf_counter()

            latency_ms = round(
                (end_time - start_time) * 1000,
                2
            )

            execution_id = self._record_execution(
                agent_id=agent_id,
                latency_ms=latency_ms,
                success=True
            )

            return {
                **provider_result,
                "execution_id": execution_id,
                "agent_id": agent_id,
                "agent_name": agent_name,
                "latency_ms": latency_ms
            }

        except Exception as error:

            end_time = time.perf_counter()

            latency_ms = round(
                (end_time - start_time) * 1000,
                2
            )

            self._record_execution(
                agent_id=agent_id,
                latency_ms=latency_ms,
                success=False,
                error=str(error)
            )

            raise