from bedrock_agentcore.runtime import BedrockAgentCoreApp
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

# Initialize model and memory (following original pattern)
MODEL_ID = "us.amazon.nova-pro-v1:0"
model = BedrockModel(model_id=MODEL_ID)
memory_client = MemoryClient()
memory_id = create_or_get_multi_agent_memory()

# Create orchestrator-specific memory hooks
SESSION_ID = str(uuid.uuid4())
ACTOR_ID = "customer_001"
memory_hooks = MultiAgentMemoryHooks(
    memory_id, memory_client, ACTOR_ID, SESSION_ID
)

# Create the orchestrator agent with routing tools
agent = Agent(
    model=model,
    tools=[route_to_agent, coordinate_multi_agent_response],
    system_prompt=ORCHESTRATOR_PROMPT,
    hooks=[memory_hooks]
)

# Initialize the AgentCore Runtime App
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    """AgentCore Runtime entrypoint function"""
    user_input = payload.get("prompt", "")
    
    # Invoke the orchestrator agent
    response = agent(user_input)
    return response.message["content"][0]["text"]

if __name__ == "__main__":
    app.run()