class AgentSystem:
    def __init__(self):
        self.agents = {}

    def register_agent(self, name: str, agent_callable):
        self.agents[name] = agent_callable

    def execute_agent(self, name: str, payload: dict):
        agent = self.agents.get(name)
        if not agent:
            raise ValueError(f"Agent '{name}' not found")
        return agent(payload)

    def list_agents(self):
        return list(self.agents.keys())
