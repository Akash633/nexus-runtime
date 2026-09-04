from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.registry import AgentRegistry
from app.runtime.decision_engine import DecisionEngine
from app.runtime.execution_engine import ExecutionEngine


# ==========================================================
# ROUTER
# ==========================================================

router = APIRouter(
    prefix="/agents",
    tags=["Agents"]
)


# ==========================================================
# AGENT REGISTRY
# ==========================================================

registry = AgentRegistry()


# ==========================================================
# SAMPLE AI AGENTS
# ==========================================================

registry.register({
    "id": "gpt-agent",
    "name": "GPT Agent",
    "capabilities": [
        "text",
        "coding",
        "reasoning"
    ],
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
    "cost": 0.015,
    "latency": 180
})


# ==========================================================
# ENGINES
# ==========================================================

decision_engine = DecisionEngine(registry)

execution_engine = ExecutionEngine()


# ==========================================================
# REQUEST SCHEMAS
# ==========================================================

class AgentSelectionRequest(BaseModel):
    capability: str


class AgentExecutionRequest(BaseModel):
    capability: str
    task: str


# ==========================================================
# GET ALL AGENTS
# ==========================================================

@router.get("/")
def get_agents():
    """
    Return all registered AI agents.
    """

    agents = registry.get_all_agents()

    return {
        "count": len(agents),
        "agents": agents
    }


# ==========================================================
# GET AGENTS BY CAPABILITY
# ==========================================================

@router.get("/capability/{capability}")
def get_agents_by_capability(capability: str):
    """
    Return all agents that support a specific capability.
    """

    agents = registry.find_by_capability(capability)

    return {
        "capability": capability,
        "count": len(agents),
        "agents": agents
    }


# ==========================================================
# SELECT BEST AGENT
# ==========================================================

@router.post("/select")
def select_best_agent(request: AgentSelectionRequest):
    """
    Select the best available agent based on
    capability, cost and latency.
    """

    try:

        selected_agent = decision_engine.select_agent(
            request.capability
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


# ==========================================================
# EXECUTE TASK
# ==========================================================

@router.post("/execute")
def execute_agent(request: AgentExecutionRequest):
    """
    Select the best agent and execute the task.
    """

    try:

        # --------------------------------------------------
        # Step 1: Select the best agent
        # --------------------------------------------------

        selected_agent = decision_engine.select_agent(
            request.capability
        )

        # --------------------------------------------------
        # Step 2: Execute the task
        # --------------------------------------------------

        result = execution_engine.execute(
            agent=selected_agent,
            task=request.task,
            capability=request.capability
        )

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Execution failed: {str(error)}"
        )


# ==========================================================
# AGENTS HEALTH CHECK
# ==========================================================

@router.get("/health")
def agents_health():
    """
    Check Agent Registry health.
    """

    agents = registry.get_all_agents()

    return {
        "status": "healthy",
        "registered_agents": len(agents)
    }