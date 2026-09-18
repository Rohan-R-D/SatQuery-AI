"""
Backward compatibility layer for Agent Orchestrator.
All agent logic has moved to the `agents/` package.
"""
from agents.supervisor_agent import supervisor_agent, agent_orchestrator, SupervisorAgent

# Re-export SupervisorAgent as AgentOrchestrator alias
AgentOrchestrator = SupervisorAgent

__all__ = [
    "supervisor_agent",
    "agent_orchestrator",
    "SupervisorAgent",
    "AgentOrchestrator"
]
