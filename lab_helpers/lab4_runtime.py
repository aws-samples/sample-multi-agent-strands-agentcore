from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from lab_helpers.utils import get_ssm_parameter
from lab_helpers.lab1_multi_agent import (
    get_return_policy,
    get_product_info,
    get_technical_support,
    CUSTOMER_SUPPORT_PROMPT
)
from lab_helpers.lab2_multi_agent_memory import (
    CustomerSupportMemoryHooks,
    create_or_get_memory_resource
)
from bedrock_agentcore.memory import MemoryClient
import uuid

# Initialize model and memory (following exact original pattern)
MODEL_ID = "amazon.nova-pro-v1:0"
model = BedrockModel(model_id=MODEL_ID)
memory_client = MemoryClient()

# Get memory ID from SSM (same as original)
memory_id = get_ssm_parameter("/app/reinvent/agentcore/memory_id")

# Create memory hooks (exact original pattern)
ACTOR_ID = "customer_001"
SESSION_ID = str(uuid.uuid4())
memory_hooks = CustomerSupportMemoryHooks(
    memory_id, memory_client, ACTOR_ID, SESSION_ID
)

# Create the agent with all customer support tools (exact original pattern)
agent = Agent(
    model=model,
    tools=[get_return_policy, get_product_info, get_technical_support],
    system_prompt=CUSTOMER_SUPPORT_PROMPT,
    hooks=[memory_hooks],
)

# Initialize the AgentCore Runtime App
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    """AgentCore Runtime entrypoint function"""
    user_input = payload.get("prompt", "")
    
    # Invoke the agent
    response = agent(user_input)
    return response.message["content"][0]["text"]

if __name__ == "__main__":
    app.run()