from typing import Dict, List, Any


class AgentRegistry:
    """
    Maintains the list of AI agents available to Nexus Runtime.
    """

    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}

    def register(self, agent: Dict[str, Any]) -> None:
        """
        Register a new AI agent.
        """
        agent_id = agent["id"]
        self.agents[agent_id] = agent

    def unregister(self, agent_id: str) -> bool:
        """
        Remove an agent from the registry.
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True

        return False

    def get_agent(self, agent_id: str) -> Dict[str, Any] | None:
        """
        Get a specific agent.
        """
        return self.agents.get(agent_id)

    def get_all_agents(self) -> List[Dict[str, Any]]:
        """
        Return all registered agents.
        """
        return list(self.agents.values())

    def find_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """
        Find agents that support a specific capability.
        """
        return [
            agent
            for agent in self.agents.values()
            if capability in agent.get("capabilities", [])
        ]