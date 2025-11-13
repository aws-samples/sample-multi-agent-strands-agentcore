from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from lab_helpers.lab1_multi_agent import route_to_agent, coordinate_multi_agent_response, ORCHESTRATOR_PROMPT

MODEL_ID = "us.amazon.nova-pro-v1:0"
model = BedrockModel(model_id=MODEL_ID)

# Create orchestrator agent without memory hooks to avoid constructor issues
orchestrator = Agent(
    model=model,
    tools=[route_to_agent, coordinate_multi_agent_response],
    system_prompt=ORCHESTRATOR_PROMPT
)

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    user_input = payload.get("prompt", "")
    response = orchestrator(user_input)
    return response.message["content"][0]["text"]

if __name__ == "__main__":
    app.run()