from typing import Dict, Any, List


class PolicyEngine:
    """
    Policy Engine for Nexus Runtime.

    Hard policies:
    - allowed_agents
    - blocked_agents
    - capability support

    Soft policies:
    - preferred maximum cost

    Hard policies can block an agent.
    Soft policies only provide preference information
    for the Decision Engine.
    """

    def __init__(
        self,
        max_cost: float | None = None,
        allowed_agents: List[str] | None = None,
        blocked_agents: List[str] | None = None,
        preferred_max_cost: float | None = None
    ):
        # Backward compatibility:
        # Existing max_cost is now treated as a
        # soft cost preference, not a hard restriction.
        self.preferred_max_cost = (
            preferred_max_cost
            if preferred_max_cost is not None
            else max_cost
        )

        self.allowed_agents = (
            allowed_agents
            if allowed_agents is not None
            else []
        )

        self.blocked_agents = (
            blocked_agents
            if blocked_agents is not None
            else []
        )

    def evaluate_agent(
        self,
        agent: Dict[str, Any],
        capability: str
    ) -> Dict[str, Any]:
        """
        Evaluate an agent against hard and soft policies.

        Returns policy evaluation details instead of
        simply returning True/False.
        """

        agent_id = agent.get("id")

        hard_policy_violations = []
        soft_policy_effects = []

        # --------------------------------------------------
        # HARD POLICY 1: Agent ID must exist
        # --------------------------------------------------

        if not agent_id:
            hard_policy_violations.append(
                "Agent is missing id"
            )

        # --------------------------------------------------
        # HARD POLICY 2: Capability must be supported
        # --------------------------------------------------

        if capability not in agent.get(
            "capabilities",
            []
        ):
            hard_policy_violations.append(
                f"Agent does not support capability "
                f"'{capability}'"
            )

        # --------------------------------------------------
        # HARD POLICY 3: Allowed agent list
        # --------------------------------------------------

        if (
            self.allowed_agents
            and agent_id not in self.allowed_agents
        ):
            hard_policy_violations.append(
                "Agent is not in allowed_agents"
            )

        # --------------------------------------------------
        # HARD POLICY 4: Explicitly blocked agent
        # --------------------------------------------------

        if agent_id in self.blocked_agents:
            hard_policy_violations.append(
                "Agent is explicitly blocked"
            )

        # --------------------------------------------------
        # SOFT POLICY: Preferred maximum cost
        # --------------------------------------------------

        agent_cost = agent.get("cost")

        if (
            self.preferred_max_cost is not None
            and isinstance(agent_cost, (int, float))
            and agent_cost > self.preferred_max_cost
        ):
            soft_policy_effects.append({
                "type": "preferred_max_cost",
                "limit": self.preferred_max_cost,
                "actual": agent_cost,
                "message": (
                    "Agent exceeds the preferred "
                    "maximum cost"
                )
            })

        # Agent is allowed only when there are
        # no hard policy violations.
        allowed = (
            len(hard_policy_violations) == 0
        )

        return {
            "agent_id": agent_id,
            "allowed": allowed,
            "hard_policy_violations": (
                hard_policy_violations
            ),
            "soft_policy_effects": (
                soft_policy_effects
            )
        }

    def validate_agent(
        self,
        agent: Dict[str, Any],
        capability: str
    ) -> bool:
        """
        Backward-compatible validation method.

        Returns True only when all hard policies pass.
        Soft policy effects do not block the agent.
        """

        evaluation = self.evaluate_agent(
            agent,
            capability
        )

        return evaluation["allowed"]

    def filter_agents(
        self,
        agents: List[Dict[str, Any]],
        capability: str
    ) -> List[Dict[str, Any]]:
        """
        Return only agents that satisfy hard policies.

        Soft policy preferences do not remove agents.
        """

        allowed_agents = []

        for agent in agents:

            if self.validate_agent(
                agent,
                capability
            ):
                allowed_agents.append(agent)

        return allowed_agents

    def get_policy(self) -> Dict[str, Any]:
        """
        Return currently active policies.
        """

        return {
            "hard": {
                "allowed_agents": (
                    self.allowed_agents
                ),
                "blocked_agents": (
                    self.blocked_agents
                )
            },
            "soft": {
                "preferred_max_cost": (
                    self.preferred_max_cost
                )
            }
        }