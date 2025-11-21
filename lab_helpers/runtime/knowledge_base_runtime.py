"""
Knowledge Base Agent Runtime
Specialized service for technical support using Bedrock Knowledge Base
"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp  #### AGENTCORE RUNTIME - LINE 1 ####
from strands import Agent
from strands.models import BedrockModel
from lab_helpers.utils import get_ssm_parameter
from strands import tool


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
from lab_helpers.lab2_multi_agent_memory import (
    MultiAgentMemoryHooks,
    create_or_get_multi_agent_memory
)
from bedrock_agentcore.memory import MemoryClient
import uuid

# Initialize model and memory
MODEL_ID = "us.amazon.nova-pro-v1:0"
model = BedrockModel(model_id=MODEL_ID, temperature=0.1)
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
