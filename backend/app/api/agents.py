from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.registry import AgentRegistry
from app.db.execution_history import ExecutionHistory
from app.db.policy_storage import PolicyStorage
from app.runtime.decision_engine import DecisionEngine
from app.runtime.execution_engine import ExecutionEngine
from app.runtime.policy_engine import PolicyEngine


router = APIRouter(
    prefix="/agents",
    tags=["Agents"]
)


# ============================================================
# AGENT REGISTRY
# ============================================================

registry = AgentRegistry()


registry.register({
    "id": "gpt-agent",
    "name": "GPT Agent",
    "capabilities": [
        "text",
        "coding",
        "reasoning"
    ],
    "capability_scores": {
        "text": 0.95,
        "coding": 0.95,
        "reasoning": 0.95
    },
    "cost": 0.02,
    "latency": 200
})


registry.register({
    "id": "gemini-agent",
    "name": "Gemini Agent",
    "capabilities": [
        "text",
        "image",
        "reasoning"
    ],
    "capability_scores": {
        "text": 0.90,
        "image": 0.98,
        "reasoning": 0.90
    },
    "cost": 0.01,
    "latency": 150
})


registry.register({
    "id": "claude-agent",
    "name": "Claude Agent",
    "capabilities": [
        "text",
        "coding",
        "reasoning"
    ],
    "capability_scores": {
        "text": 0.92,
        "coding": 0.98,
        "reasoning": 0.95
    },
    "cost": 0.015,
    "latency": 180
})


registry.register({
    "id": "groq-agent",
    "name": "Groq Agent",
    "capabilities": [
        "text",
        "coding",
        "reasoning"
    ],
    "capability_scores": {
        "text": 0.85,
        "coding": 0.85,
        "reasoning": 0.90
    },
    "cost": 0.0,
    "latency": 50
})


# ============================================================
# EXECUTION HISTORY
# ============================================================

execution_history = ExecutionHistory()


execution_engine = ExecutionEngine(
    execution_history=execution_history
)


# ============================================================
# POLICY STORAGE
# ============================================================

policy_storage = PolicyStorage()


# ============================================================
# POLICY ENGINE
# ============================================================

policy_engine = PolicyEngine()


# Load previously saved policy when the application starts.
saved_policy = policy_storage.load_policy()


if saved_policy is not None:

    policy_engine.allowed_agents = (
        saved_policy["hard"]["allowed_agents"]
    )

    policy_engine.blocked_agents = (
        saved_policy["hard"]["blocked_agents"]
    )

    policy_engine.preferred_max_cost = (
        saved_policy["soft"]["preferred_max_cost"]
    )


# ============================================================
# DECISION ENGINE
# ============================================================

decision_engine = DecisionEngine(
    registry=registry,
    latency_history=execution_engine.latency_history,
    policy_engine=policy_engine
)


# ============================================================
# REQUEST MODELS
# ============================================================

class AgentSelectionRequest(BaseModel):
    capability: str


class AgentExecutionRequest(BaseModel):
    capability: str
    task: str
    simulate_failure_for: Optional[str] = None


class PolicyUpdateRequest(BaseModel):
    allowed_agents: Optional[list[str]] = None
    blocked_agents: Optional[list[str]] = None
    preferred_max_cost: Optional[float] = None


# ============================================================
# AGENT APIs
# ============================================================

@router.get("/")
def get_agents():

    agents = registry.get_all_agents()

    return {
        "count": len(agents),
        "agents": agents
    }


@router.get("/capability/{capability}")
def get_agents_by_capability(
    capability: str
):

    agents = registry.find_by_capability(
        capability
    )

    return {
        "capability": capability,
        "count": len(agents),
        "agents": agents
    }


# ============================================================
# POLICY APIs
# ============================================================

@router.get("/policy")
def get_policy():

    return {
        "success": True,
        "policy": policy_engine.get_policy()
    }


@router.put("/policy")
def update_policy(
    request: PolicyUpdateRequest
):

    # --------------------------------------------------------
    # Update allowed agents
    # --------------------------------------------------------

    if "allowed_agents" in request.model_fields_set:

        policy_engine.allowed_agents = (
            request.allowed_agents
            if request.allowed_agents is not None
            else []
        )


    # --------------------------------------------------------
    # Update blocked agents
    # --------------------------------------------------------

    if "blocked_agents" in request.model_fields_set:

        policy_engine.blocked_agents = (
            request.blocked_agents
            if request.blocked_agents is not None
            else []
        )


    # --------------------------------------------------------
    # Update preferred maximum cost
    # --------------------------------------------------------

    if "preferred_max_cost" in request.model_fields_set:

        if (
            request.preferred_max_cost is not None
            and request.preferred_max_cost < 0
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "preferred_max_cost "
                    "cannot be negative"
                )
            )

        # None means explicitly reset the preference.
        policy_engine.preferred_max_cost = (
            request.preferred_max_cost
        )


    # --------------------------------------------------------
    # Save updated policy permanently
    # --------------------------------------------------------

    policy_storage.save_policy(
        policy_engine.get_policy()
    )


    return {
        "success": True,
        "message": "Policy updated successfully",
        "policy": policy_engine.get_policy()
    }


# ============================================================
# AGENT SELECTION
# ============================================================

@router.post("/select")
def select_best_agent(
    request: AgentSelectionRequest
):

    try:

        selected_agent = (
            decision_engine.select_agent(
                request.capability
            )
        )

        return {
            "success": True,
            "required_capability": request.capability,
            "selected_agent": selected_agent
        }

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


# ============================================================
# AGENT EXECUTION + FALLBACK
# ============================================================

@router.post("/execute")
def execute_agent(
    request: AgentExecutionRequest
):

    try:

        ranked_agents = (
            decision_engine.rank_agents(
                request.capability
            )
        )

        failed_agents = []

        for agent in ranked_agents:

            try:

                should_fail = (
                    request.simulate_failure_for
                    == agent.get("id")
                )

                result = execution_engine.execute(
                    agent=agent,
                    task=request.task,
                    capability=request.capability,
                    simulate_failure=should_fail
                )

                result["fallback_used"] = (
                    len(failed_agents) > 0
                )

                if failed_agents:

                    result["failed_agents"] = (
                        failed_agents
                    )

                return result

            except Exception as error:

                failed_agents.append({
                    "agent_id": agent.get("id"),
                    "agent_name": agent.get("name"),
                    "error": str(error)
                })


        raise HTTPException(
            status_code=503,
            detail={
                "message": (
                    "All policy-approved "
                    "agents failed"
                ),
                "failed_agents": failed_agents
            }
        )


    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


    except HTTPException:

        raise


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Execution failed: {str(error)}"
        )


# ============================================================
# EXECUTION HISTORY
# ============================================================

@router.get("/latency-history")
def get_latency_history():

    history = execution_history.get_all()

    return {
        "count": len(history),
        "history": history
    }


# ============================================================
# HEALTH
# ============================================================

@router.get("/health")
def agents_health():

    agents = registry.get_all_agents()

    return {
        "status": "healthy",
        "registered_agents": len(agents)
    }


# ============================================================
# PERFORMANCE
# ============================================================

@router.get("/performance")
def get_agent_performance():

    performance = (
        execution_history.get_all_agent_stats()
    )

    return {
        "count": len(performance),
        "agents": performance
    }


@router.get("/performance/{agent_id}")
def get_agent_agent_performance(
    agent_id: str
):

    performance = (
        execution_history.get_agent_stats(
            agent_id
        )
    )

    if performance["total_executions"] == 0:

        raise HTTPException(
            status_code=404,
            detail=(
                f"No execution history found "
                f"for agent: {agent_id}"
            )
        )

    return performance
