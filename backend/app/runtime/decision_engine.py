from typing import Dict, Any, List

from app.agents.registry import AgentRegistry
from app.runtime.policy_engine import PolicyEngine


class DecisionEngine:
    """
    Adaptive decision engine for Nexus Runtime.

    Agents are ranked using:
    - Capability fit
    - Cost
    - Actual / estimated latency
    - Historical success rate

    Before ranking, the Policy Engine evaluates each
    candidate agent.

    Hard policy violations remove an agent from
    the candidate pool.

    Soft policy effects are preserved as information
    for the Decision Engine and future scoring logic.
    """

    def __init__(
        self,
        registry: AgentRegistry,
        latency_history: List[Dict[str, Any]] | None = None,
        policy_engine: PolicyEngine | None = None
    ):
        self.registry = registry

        self.latency_history = (
            latency_history
            if latency_history is not None
            else []
        )

        self.policy_engine = (
            policy_engine
            if policy_engine is not None
            else PolicyEngine()
        )

    def get_actual_latency(
        self,
        agent_id: str
    ) -> float | None:
        """
        Calculate average actual latency for an agent.
        """

        agent_latencies = [
            record["latency_ms"]
            for record in self.latency_history
            if record.get("agent_id") == agent_id
            and record.get("latency_ms") is not None
        ]

        if not agent_latencies:
            return None

        return sum(agent_latencies) / len(agent_latencies)

    def get_success_rate(
        self,
        agent_id: str
    ) -> float:
        """
        Calculate historical success rate for an agent.

        Returns:
            Value between 0.0 and 1.0
        """

        agent_records = [
            record
            for record in self.latency_history
            if record.get("agent_id") == agent_id
        ]

        if not agent_records:
            return 0.5

        successful_executions = sum(
            1
            for record in agent_records
            if record.get("success") is True
        )

        total_executions = len(agent_records)

        return (
            successful_executions
            / total_executions
        )

    def get_capability_score(
        self,
        agent: Dict[str, Any],
        capability: str
    ) -> float:
        """
        Get the agent's capability-fit score
        for the requested capability.

        The score is expected to be between
        0.0 and 1.0.

        If an agent supports the capability but
        has no explicit capability score, a neutral
        fallback score of 0.5 is used.
        """

        capability_scores = agent.get(
            "capability_scores",
            {}
        )

        score = capability_scores.get(
            capability,
            0.5
        )

        try:
            score = float(score)
        except (TypeError, ValueError):
            score = 0.5

        return max(
            0.0,
            min(1.0, score)
        )

    def get_policy_approved_agents(
        self,
        capability: str
    ) -> List[Dict[str, Any]]:
        """
        Get agents that satisfy all hard policies.

        Soft policy effects are attached to each
        approved agent but do not remove the agent.
        """

        capable_agents = self.registry.find_by_capability(
            capability
        )

        if not capable_agents:
            raise ValueError(
                f"No agent available for capability: {capability}"
            )

        approved_agents = []

        for agent in capable_agents:

            policy_result = (
                self.policy_engine.evaluate_agent(
                    agent,
                    capability
                )
            )

            if not policy_result["allowed"]:
                continue

            agent["policy"] = {
                "allowed": True,
                "hard_policy_violations": [],
                "soft_policy_effects": (
                    policy_result[
                        "soft_policy_effects"
                    ]
                )
            }

            approved_agents.append(agent)

        if not approved_agents:
            raise ValueError(
                "No agent satisfies the active "
                f"policies for capability: {capability}"
            )

        return approved_agents

    def rank_agents(
        self,
        capability: str
    ) -> List[Dict[str, Any]]:
        """
        Rank policy-approved agents using adaptive scoring.

        Score components:

        Capability Fit : 30%
        Cost           : 28%
        Latency        : 20%
        Success Rate   : 22%

        Hard policy violations are excluded before
        scoring.

        Soft policy effects are currently preserved
        as metadata and will be incorporated into
        adaptive scoring in a later step.
        """

        agents = self.get_policy_approved_agents(
            capability
        )

        effective_latencies = []

        for agent in agents:

            agent_id = agent.get("id")

            actual_latency = self.get_actual_latency(
                agent_id
            )

            if actual_latency is not None:
                effective_latency = actual_latency
            else:
                effective_latency = agent.get(
                    "latency",
                    float("inf")
                )

            success_rate = self.get_success_rate(
                agent_id
            )

            capability_score = (
                self.get_capability_score(
                    agent,
                    capability
                )
            )

            effective_latencies.append(
                effective_latency
            )

            agent["_effective_latency"] = (
                effective_latency
            )

            agent["_success_rate"] = (
                success_rate
            )

            agent["_capability_score"] = (
                capability_score
            )

        costs = [
            agent.get(
                "cost",
                float("inf")
            )
            for agent in agents
        ]

        min_cost = min(costs)
        max_cost = max(costs)

        min_latency = min(effective_latencies)
        max_latency = max(effective_latencies)

        def calculate_score(
            agent: Dict[str, Any]
        ) -> float:

            cost = agent.get(
                "cost",
                float("inf")
            )

            latency = agent.get(
                "_effective_latency",
                float("inf")
            )

            success_rate = agent.get(
                "_success_rate",
                0.5
            )

            capability_score = agent.get(
                "_capability_score",
                0.5
            )

            # Cost score
            if max_cost == min_cost:
                cost_score = 1.0
            else:
                cost_score = (
                    (max_cost - cost)
                    / (max_cost - min_cost)
                )

            # Latency score
            if max_latency == min_latency:
                latency_score = 1.0
            else:
                latency_score = (
                    (max_latency - latency)
                    / (max_latency - min_latency)
                )

            # Nexus adaptive score
            final_score = (
                0.30 * capability_score
                + 0.28 * cost_score
                + 0.20 * latency_score
                + 0.22 * success_rate
            )

            return round(
                final_score,
                4
            )

        for agent in agents:

            agent["capability_score"] = round(
                agent["_capability_score"],
                4
            )

            agent["score"] = calculate_score(
                agent
            )

            agent["success_rate"] = round(
                agent["_success_rate"] * 100,
                2
            )

        # Highest score first
        agents.sort(
            key=lambda agent: agent["score"],
            reverse=True
        )

        # Remove internal calculation fields
        for agent in agents:

            agent.pop(
                "_effective_latency",
                None
            )

            agent.pop(
                "_success_rate",
                None
            )

            agent.pop(
                "_capability_score",
                None
            )

        return agents

    def select_agent(
        self,
        capability: str
    ) -> Dict[str, Any]:
        """
        Select the highest-ranked policy-approved agent.
        """

        ranked_agents = self.rank_agents(
            capability
        )

        return ranked_agents[0]