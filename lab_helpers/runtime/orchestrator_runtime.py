"""
Orchestrator Runtime for Multi-Agent System
Handles request routing and coordination across specialized agents
"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp  #### AGENTCORE RUNTIME - LINE 1 ####
from strands import Agent
from strands.models import BedrockModel
from lab_helpers.utils import get_ssm_parameter
from lab_helpers.lab1_multi_agent import (
    route_to_agent,
    coordinate_multi_agent_response,
    ORCHESTRATOR_PROMPT
)
from lab_helpers.lab2_multi_agent_memory import (
    MultiAgentMemoryHooks,
    create_or_get_multi_agent_memory
)
from bedrock_agentcore.memory import MemoryClient
import uuid
import json

# Initialize model and memory
MODEL_ID = "amazon.nova-pro-v1:0"
model = BedrockModel(model_id=MODEL_ID)
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
