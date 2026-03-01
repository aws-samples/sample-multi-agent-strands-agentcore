"""
Knowledge Base Agent Runtime
Specialized service for technical support using A2A protocol
"""

import logging
import os
from strands import Agent
from strands.models import BedrockModel
from strands.multiagent.a2a import A2AServer
from strands import tool
import uvicorn
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)


# Self-contained tools for runtime
@tool
def get_technical_support(issue_description: str) -> str:
    """Get technical support solutions for common issues"""
    issue_lower = issue_description.lower()
    
    # Mock technical support solutions
    solutions = {
        "overheating": "For overheating issues: 1) Check for dust buildup in vents and clean with compressed air, 2) Ensure proper ventilation around device, 3) Close unnecessary applications, 4) Check Task Manager for high CPU usage processes, 5) Consider using a cooling pad for laptops.",
        "performance": "For performance issues: 1) Restart your device, 2) Check available storage space (keep 15% free), 3) Run disk cleanup, 4) Update drivers and software, 5) Check for malware, 6) Disable startup programs you don't need.",
        "battery": "For battery issues: 1) Calibrate battery by full discharge/charge cycle, 2) Check power settings and reduce screen brightness, 3) Close background apps, 4) Update device drivers, 5) Replace battery if over 2-3 years old.",
        "connectivity": "For connectivity issues: 1) Restart your router and device, 2) Forget and reconnect to WiFi network, 3) Update network drivers, 4) Check for interference from other devices, 5) Reset network settings if needed.",
        "slow": "For slow performance: 1) Restart device, 2) Check available RAM and storage, 3) Close unnecessary programs, 4) Run antivirus scan, 5) Update operating system and drivers, 6) Consider hardware upgrade if device is old."
    }
    
    # Find matching solution
    for keyword, solution in solutions.items():
        if keyword in issue_lower:
            return f"Technical Support Solution:\n\n{solution}\n\nIf these steps don't resolve the issue, please contact our technical support team for further assistance."
    
    return "Technical Support: Please provide more specific details about the technical issue you're experiencing. Common issues we can help with include overheating, performance problems, battery issues, connectivity problems, and slow performance. For immediate assistance, contact our technical support team."

KNOWLEDGE_BASE_PROMPT = """You are a technical support specialist with access to comprehensive knowledge bases.

IMPORTANT: For ANY technical question, you MUST call get_technical_support() with the issue description.
Never provide technical advice from memory - always use the knowledge base tool first.

Available tools:
1. get_technical_support(issue_description) - REQUIRED for all technical questions, troubleshooting, and support

Always call get_technical_support() first, then provide helpful guidance based on the knowledge base results."""

# Initialize model
MODEL_ID = "us.amazon.nova-pro-v1:0"
model = BedrockModel(model_id=MODEL_ID, temperature=0.1)

# Create knowledge base agent
knowledge_base_agent = Agent(
    name="Knowledge Base Agent",
    description="A technical support agent that provides troubleshooting guidance and technical solutions for common device issues.",
    model=model,
    tools=[get_technical_support],
    system_prompt=KNOWLEDGE_BASE_PROMPT,
    callback_handler=None
)

# Get runtime URL from environment (set by Bedrock AgentCore Runtime)
runtime_url = os.environ.get('AGENTCORE_RUNTIME_URL', 'http://0.0.0.0:9000/')
logging.info(f"A2A Server URL: {runtime_url}")

host, port = "0.0.0.0", 9000

# Create A2A server
a2a_server = A2AServer(
    agent=knowledge_base_agent,
    http_url=runtime_url,
    serve_at_root=True  # Serves at root (/) for AgentCore Runtime
)

app = FastAPI()

@app.get("/ping")
def ping():
    return {"status": "healthy"}

app.mount("/", a2a_server.to_fastapi_app())

# Export the agent for local testing (Lab 5)
# The agent is already created above, so we can just reference it directly

if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port)
