from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.registry import AgentRegistry
from app.db.execution_history import ExecutionHistory
from app.runtime.decision_engine import DecisionEngine
from app.runtime.execution_engine import ExecutionEngine


router = APIRouter(
    prefix="/agents",
    tags=["Agents"]
)


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


execution_history = ExecutionHistory()


execution_engine = ExecutionEngine(
    execution_history=execution_history
)


decision_engine = DecisionEngine(
    registry,
    execution_engine.latency_history
)


class AgentSelectionRequest(BaseModel):
    capability: str


class AgentExecutionRequest(BaseModel):
    capability: str
    task: str
    simulate_failure_for: Optional[str] = None


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
                "message": "All capable agents failed",
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


@router.get("/latency-history")
def get_latency_history():

    history = execution_history.get_all()

    return {
        "count": len(history),
        "history": history
    }


@router.get("/health")
def agents_health():

    agents = registry.get_all_agents()

    return {
        "status": "healthy",
        "registered_agents": len(agents)
    }


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