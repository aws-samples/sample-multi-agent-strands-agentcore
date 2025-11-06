"""
Minimal Runtime for Multi-Agent System
Simple orchestrator that handles basic routing without complex dependencies
"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
import json

# Initialize model
MODEL_ID = "amazon.nova-pro-v1:0"
model = BedrockModel(model_id=MODEL_ID)

# Simple orchestrator prompt
ORCHESTRATOR_PROMPT = """You are an intelligent customer support orchestrator. 
Your role is to help customers with their queries by providing helpful responses.

For customer support questions, provide direct assistance.
For technical questions, offer technical guidance.
Always be helpful, professional, and concise."""

# Create simple orchestrator agent
orchestrator = Agent(
    model=model,
    system_prompt=ORCHESTRATOR_PROMPT
)

# Initialize the AgentCore Runtime App
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    """Minimal orchestrator runtime entrypoint"""
    try:
        user_input = payload.get("prompt", "")
        if not user_input:
            return "Hello! How can I help you today?"
        
        # Use orchestrator to handle the request
        response = orchestrator(user_input)
        return response.message["content"][0]["text"]
    
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}. Please try again."

if __name__ == "__main__":
    app.run()