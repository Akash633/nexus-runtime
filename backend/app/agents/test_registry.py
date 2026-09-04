from registry import AgentRegistry


registry = AgentRegistry()

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

print("All Agents:")
print(registry.get_all_agents())

print("\nAgents capable of image:")
print(registry.find_by_capability("image"))