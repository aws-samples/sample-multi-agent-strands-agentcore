"""
Knowledge Base Agent Runtime
Specialized service for technical support using Bedrock Knowledge Base
"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp  #### AGENTCORE RUNTIME - LINE 1 ####
from strands import Agent
from strands.models import BedrockModel
from lab_helpers.utils import get_ssm_parameter
from lab_helpers.lab1_multi_agent import (
    get_technical_support,
    KNOWLEDGE_BASE_PROMPT
)
from lab_helpers.lab2_multi_agent_memory import (
    MultiAgentMemoryHooks,
    create_or_get_multi_agent_memory
)
from bedrock_agentcore.memory import MemoryClient
import uuid

# Initialize model and memory
MODEL_ID = "amazon.nova-pro-v1:0"
model = BedrockModel(model_id=MODEL_ID)
memory_client = MemoryClient()
memory_id = create_or_get_multi_agent_memory()

# Create knowledge base specific memory hooks
SESSION_ID = str(uuid.uuid4())
CUSTOMER_ID = "customer_001"
memory_hooks = MultiAgentMemoryHooks(
    memory_id, memory_client, CUSTOMER_ID, SESSION_ID,
    agent_type="knowledge_base"
)

# Create knowledge base agent
knowledge_base_agent = Agent(
    model=model,
    tools=[get_technical_support],
    system_prompt=KNOWLEDGE_BASE_PROMPT,
    hooks=[memory_hooks]
)

# Initialize the AgentCore Runtime App
app = BedrockAgentCoreApp()  #### AGENTCORE RUNTIME - LINE 2 ####

@app.entrypoint  #### AGENTCORE RUNTIME - LINE 3 ####
def invoke(payload):
    """Knowledge Base Agent Runtime entrypoint"""
    user_input = payload.get("prompt", "")
    response = knowledge_base_agent(user_input)
    return response.message["content"][0]["text"]

if __name__ == "__main__":
    app.run()  #### AGENTCORE RUNTIME - LINE 4 ####
