from typing import Dict, Any


class ExecutionEngine:
    """
    Executes tasks using the agent selected by the Decision Engine.

    Currently this is a mock execution layer.
    Actual OpenAI/Gemini/Claude API integration will be added later.
    """

    def __init__(self):
        self.execution_count = 0

    def execute(
        self,
        agent: Dict[str, Any],
        task: str,
        capability: str
    ) -> Dict[str, Any]:

        self.execution_count += 1

        if not task or not task.strip():
            raise ValueError("Task cannot be empty")

        agent_id = agent.get("id")
        agent_name = agent.get("name")

        if not agent_id:
            raise ValueError("Invalid agent: missing agent id")

        if capability not in agent.get("capabilities", []):
            raise ValueError(
                f"Agent '{agent_id}' does not support capability '{capability}'"
            )

        # Mock execution for now
        result = (
            f"Task received successfully by {agent_name}. "
            f"Capability: {capability}. "
            f"Task: {task}"
        )

        return {
            "success": True,
            "execution_id": self.execution_count,
            "agent_id": agent_id,
            "agent_name": agent_name,
            "capability": capability,
            "task": task,
            "result": result
        }