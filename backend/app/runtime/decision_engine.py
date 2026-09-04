from typing import Dict, Any, List


class DecisionEngine:
    """
    Selects the best AI agent for a given task.
    """

    def __init__(self, agent_registry):
        self.agent_registry = agent_registry

    def select_agent(self, required_capability: str) -> Dict[str, Any]:
        """
        Select the best available agent based on:
        1. Capability
        2. Cost
        3. Latency
        """

        candidates: List[Dict[str, Any]] = (
            self.agent_registry.find_by_capability(required_capability)
        )

        if not candidates:
            raise ValueError(
                f"No agent available for capability: {required_capability}"
            )

        # Lower cost is better.
        # If cost is equal, lower latency is better.
        best_agent = min(
            candidates,
            key=lambda agent: (
                agent.get("cost", float("inf")),
                agent.get("latency", float("inf")),
            ),
        )

        return best_agent