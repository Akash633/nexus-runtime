import pytest

from app.agents.registry import AgentRegistry
from app.runtime.decision_engine import DecisionEngine


def create_registry():
    registry = AgentRegistry()

    registry.register({
        "id": "gpt-agent",
        "name": "GPT Agent",
        "capabilities": ["text", "coding", "reasoning"],
        "cost": 0.02,
        "latency": 200,
    })

    registry.register({
        "id": "gemini-agent",
        "name": "Gemini Agent",
        "capabilities": ["text", "image", "reasoning"],
        "cost": 0.01,
        "latency": 150,
    })

    registry.register({
        "id": "coding-agent",
        "name": "Coding Agent",
        "capabilities": ["coding"],
        "cost": 0.01,
        "latency": 100,
    })

    return registry


def test_select_agent_by_capability():
    registry = create_registry()
    engine = DecisionEngine(registry)

    result = engine.select_agent("image")

    assert result["id"] == "gemini-agent"


def test_select_lowest_cost_agent():
    registry = create_registry()
    engine = DecisionEngine(registry)

    result = engine.select_agent("coding")

    assert result["id"] == "coding-agent"


def test_select_lowest_latency_when_cost_is_equal():
    registry = AgentRegistry()

    registry.register({
        "id": "agent-a",
        "name": "Agent A",
        "capabilities": ["text"],
        "cost": 0.01,
        "latency": 200,
    })

    registry.register({
        "id": "agent-b",
        "name": "Agent B",
        "capabilities": ["text"],
        "cost": 0.01,
        "latency": 100,
    })

    engine = DecisionEngine(registry)

    result = engine.select_agent("text")

    assert result["id"] == "agent-b"


def test_no_agent_for_capability():
    registry = create_registry()
    engine = DecisionEngine(registry)

    with pytest.raises(ValueError):
        engine.select_agent("audio")