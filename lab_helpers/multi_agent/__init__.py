# Multi-Agent System Components

"""
Core components for multi-agent orchestration and coordination.
"""

from enum import Enum
from typing import Dict, Any, Optional

class AgentType(Enum):
    """Enumeration of available agent types"""
    ORCHESTRATOR = "orchestrator"
    CUSTOMER_SUPPORT = "customer_support"
    KNOWLEDGE_BASE = "knowledge_base"

class QueryType(Enum):
    """Classification of customer query types"""
    PRODUCT_INFO = "product_info"
    RETURN_POLICY = "return_policy"
    TECHNICAL_SUPPORT = "technical_support"
    GENERAL_SEARCH = "general_search"
    COMPLEX_MULTI_STEP = "complex_multi_step"

# Global agent registry for communication
AGENT_REGISTRY = {}

def register_agent(agent_type: AgentType, agent_instance) -> None:
    """Register an agent in the global registry"""
    AGENT_REGISTRY[agent_type.value] = agent_instance
    print(f"📝 Registered {agent_type.value} agent")

def get_agent(agent_type: AgentType):
    """Retrieve an agent from the registry"""
    return AGENT_REGISTRY.get(agent_type.value)

def list_registered_agents() -> Dict[str, Any]:
    """List all registered agents"""
    return {
        agent_type: {
            "available": agent is not None,
            "tools": len(agent.tools) if hasattr(agent, 'tools') and agent else 0
        }
        for agent_type, agent in AGENT_REGISTRY.items()
    }

__all__ = [
    "AgentType",
    "QueryType", 
    "AGENT_REGISTRY",
    "register_agent",
    "get_agent",
    "list_registered_agents"
]