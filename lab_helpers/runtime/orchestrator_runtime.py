import os
import urllib.parse
import uuid

import boto3
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.runtime import BedrockAgentCoreApp, RequestContext
from lab_helpers.lab2_multi_agent_memory import (
    MultiAgentMemoryHooks,
    create_or_get_multi_agent_memory,
)
from strands import Agent
from strands.models import BedrockModel
from strands_tools.a2a_client import A2AClientToolProvider


def get_agent_url(agent_type: str) -> str:
    agent_arn = os.environ[f"AGENTCORE_{agent_type.upper()}_ARN"]
    region = boto3.session.Session().region_name or "us-west-2"

    encoded_arn = urllib.parse.quote(agent_arn, safe='')
    url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations/"
    return url

def get_a2a_providers(agent_arns: list[str], bearer_token: str) -> A2AClientToolProvider:
    httpx_client_args = {
        "headers": {
            "Authorization": f"Bearer {bearer_token}",
        },
        "timeout": 300
    }
    return A2AClientToolProvider(
        known_agent_urls=agent_arns,
        httpx_client_args=httpx_client_args
    )

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

# Create orchestrator agent with A2A tools
ORCHESTRATOR_PROMPT = """You are an intelligent orchestrator agent for a customer support system."""

# Try to get agent URLs from environment (for AgentCore Runtime)
# If not available (Lab 5), skip this initialization
AGENT_URLS = []
try:
    agents = [
        'customer_support',
        'knowledge_base'
    ]
    AGENT_URLS = [get_agent_url(agent) for agent in agents]
    print(f"Agent URLs: {AGENT_URLS}")
except KeyError:
    # Environment variables not set - running in local mode (Lab 5)
    print("Running in local mode - agent URLs will be initialized on demand")

# Initialize the AgentCore Runtime App
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload, context: RequestContext):
    # Extract bearer token from request headers via AgentCore RequestContext
    request_headers = context.request_headers
    auth_header = request_headers.get("Authorization", "")
    bearer_token = auth_header.removeprefix("Bearer ").strip()
    print(bearer_token[:20])
    if not bearer_token:
        raise ValueError("Missing Authorization bearer token in request headers")

    provider = get_a2a_providers(AGENT_URLS, bearer_token)

    orchestrator = Agent(
        model=model,
        tools=[provider.tools],
        system_prompt=ORCHESTRATOR_PROMPT,
        hooks=[memory_hooks]
    )

    user_input = payload.get("prompt", "")
    response = orchestrator(user_input)
    return response.message["content"][0]["text"]

if __name__ == "__main__":
    app.run()