"""
Customer Support Agent Runtime
Specialized service for customer support queries with gateway integration
"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp  #### AGENTCORE RUNTIME - LINE 1 ####
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from lab_helpers.utils import get_ssm_parameter, get_cognito_client_secret
from lab_helpers.lab1_multi_agent import (
    get_product_info,
    get_return_policy,
    CUSTOMER_SUPPORT_PROMPT
)
from lab_helpers.lab2_multi_agent_memory import (
    MultiAgentMemoryHooks,
    create_or_get_multi_agent_memory
)
from bedrock_agentcore.memory import MemoryClient
import uuid
import requests

# Initialize model and memory
MODEL_ID = "us.amazon.nova-pro-v1:0"
model = BedrockModel(model_id=MODEL_ID)
memory_client = MemoryClient()
memory_id = create_or_get_multi_agent_memory()

# Create customer support specific memory hooks
SESSION_ID = str(uuid.uuid4())
CUSTOMER_ID = "customer_001"
memory_hooks = MultiAgentMemoryHooks(
    memory_id, memory_client, CUSTOMER_ID, SESSION_ID,
    agent_type="customer_support"
)

# Gateway integration (from Lab 3)
def get_token(client_id: str, client_secret: str, scope_string: str, url: str) -> dict:
    try:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope_string,
        }
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        return {"error": str(err)}

# Initialize gateway connection
try:
    gateway_access_token = get_token(
        get_ssm_parameter("/app/reinvent/agentcore/machine_client_id"),
        get_cognito_client_secret(),
        get_ssm_parameter("/app/reinvent/agentcore/cognito_auth_scope"),
        get_ssm_parameter("/app/reinvent/agentcore/cognito_token_url")
    )
    gateway_url = get_ssm_parameter("/app/reinvent/agentcore/gateway_url")
    mcp_client = MCPClient(
        lambda: streamablehttp_client(
            gateway_url,
            headers={"Authorization": f"Bearer {gateway_access_token['access_token']}"},
        )
    )
    mcp_client.start()
    gateway_tools = mcp_client.list_tools_sync()
    all_tools = [get_product_info, get_return_policy] + gateway_tools
except Exception as e:
    print(f"Gateway integration failed: {e}")
    all_tools = [get_product_info, get_return_policy]

# Create customer support agent
customer_support_agent = Agent(
    model=model,
    tools=all_tools,
    system_prompt=CUSTOMER_SUPPORT_PROMPT,
    hooks=[memory_hooks]
)

# Initialize the AgentCore Runtime App
app = BedrockAgentCoreApp()  #### AGENTCORE RUNTIME - LINE 2 ####

@app.entrypoint  #### AGENTCORE RUNTIME - LINE 3 ####
def invoke(payload):
    """Customer Support Agent Runtime entrypoint"""
    user_input = payload.get("prompt", "")
    response = customer_support_agent(user_input)
    return response.message["content"][0]["text"]

if __name__ == "__main__":
    app.run()  #### AGENTCORE RUNTIME - LINE 4 ####
