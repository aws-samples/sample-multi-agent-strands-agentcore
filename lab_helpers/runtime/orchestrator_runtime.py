"""
Orchestrator Runtime for Multi-Agent System
Handles request routing and coordination across specialized agents
"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp  #### AGENTCORE RUNTIME - LINE 1 ####
from strands import Agent
from strands.models import BedrockModel
from lab_helpers.utils import get_ssm_parameter
from strands import tool

# Self-contained tools for runtime
@tool
def route_to_agent(query: str, agent_type: str = None) -> str:
    """Route a customer query to the appropriate specialized agent."""
    query_lower = query.lower()
    
    if agent_type:
        return f"Routing to {agent_type} agent: {query}"
    
    technical_keywords = ['troubleshoot', 'error', 'not working', 'broken', 'fix', 'technical', 'support', 'issue', 'problem']
    service_keywords = ['return', 'refund', 'warranty', 'policy', 'order', 'shipping', 'product info', 'specifications']
    
    if any(keyword in query_lower for keyword in technical_keywords):
        return f"Routing to knowledge_base agent for technical support: {query}"
    elif any(keyword in query_lower for keyword in service_keywords):
        return f"Routing to customer_support agent for general support: {query}"
    else:
        return f"Routing to customer_support agent for general inquiry: {query}"

@tool
def coordinate_multi_agent_response(responses: list) -> str:
    """Coordinate and synthesize responses from multiple agents."""
    if not responses:
        return "No responses received from agents."
    
    if len(responses) == 1:
        return responses[0]
    
    coordinated = "Based on input from our specialized agents:\n\n"
    for i, response in enumerate(responses, 1):
        coordinated += f"Agent {i}: {response}\n\n"
    
    coordinated += "This coordinated response provides comprehensive support for your inquiry."
    return coordinated

ORCHESTRATOR_PROMPT = """You are an intelligent orchestrator agent for a customer support system.

IMPORTANT: You MUST use the routing tools to analyze and route customer queries.

For ANY customer query, you MUST call route_to_agent() to determine the best agent.
If multiple agents are needed, use coordinate_multi_agent_response().

Available tools:
1. route_to_agent(query, agent_type) - REQUIRED to analyze and route customer queries
2. coordinate_multi_agent_response(responses) - Use when combining multiple agent responses

Always call route_to_agent() first to properly analyze the customer's request."""
from lab_helpers.lab2_multi_agent_memory import (
    MultiAgentMemoryHooks,
    create_or_get_multi_agent_memory
)
from bedrock_agentcore.memory import MemoryClient
import uuid
import json

# Initialize model and memory
MODEL_ID = "us.amazon.nova-pro-v1:0"
model = BedrockModel(model_id=MODEL_ID, temperature=0.1)
memory_client = MemoryClient()
memory_id = create_or_get_multi_agent_memory()

# Create orchestrator-specific memory hooks
SESSION_ID = str(uuid.uuid4())
CUSTOMER_ID = "customer_001"
memory_hooks = MultiAgentMemoryHooks(
    memory_id, memory_client, CUSTOMER_ID, SESSION_ID,
    agent_type="orchestrator"
)

# Create orchestrator agent with routing tools
orchestrator = Agent(
    model=model,
    tools=[route_to_agent, coordinate_multi_agent_response],
    system_prompt=ORCHESTRATOR_PROMPT,
    hooks=[memory_hooks]
)

# Initialize the AgentCore Runtime App
app = BedrockAgentCoreApp()  #### AGENTCORE RUNTIME - LINE 2 ####

@app.entrypoint  #### AGENTCORE RUNTIME - LINE 3 ####
def invoke(payload):
    """Orchestrator Runtime entrypoint - routes requests to appropriate agents"""
    user_input = payload.get("prompt", "")

    # Use orchestrator to determine routing and coordinate response
    response = orchestrator(user_input)
    return response.message["content"][0]["text"]

if __name__ == "__main__":
    app.run()  #### AGENTCORE RUNTIME - LINE 4 ####
