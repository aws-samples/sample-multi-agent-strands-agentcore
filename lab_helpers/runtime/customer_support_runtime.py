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
from strands import tool

# Self-contained tools for runtime
@tool(
    name="get_product_info",
    description="Get detailed technical specifications and information for electronics products"
)
def get_product_info(product_type: str) -> str:
    products = {
        "laptops": {
            "warranty": "1-year manufacturer warranty + optional extended coverage",
            "specs": "Intel/AMD processors, 8-32GB RAM, SSD storage, various display sizes",
            "features": "Backlit keyboards, USB-C/Thunderbolt, Wi-Fi 6, Bluetooth 5.0",
            "compatibility": "Windows 11, macOS, Linux support varies by model",
            "support": "Technical support and driver updates included"
        },
        "smartphones": {
            "warranty": "1-year manufacturer warranty",
            "specs": "5G/4G connectivity, 128GB-1TB storage, multiple camera systems",
            "features": "Wireless charging, water resistance, biometric security",
            "compatibility": "iOS/Android, carrier unlocked options available",
            "support": "Software updates and technical support included"
        },
        "headphones": {
            "warranty": "1-year manufacturer warranty",
            "specs": "Wired/wireless options, noise cancellation, 20Hz-20kHz frequency",
            "features": "Active noise cancellation, touch controls, voice assistant",
            "compatibility": "Bluetooth 5.0+, 3.5mm jack, USB-C charging",
            "support": "Firmware updates via companion app"
        },
        "monitors": {
            "warranty": "3-year manufacturer warranty",
            "specs": "4K/1440p/1080p resolutions, IPS/OLED panels, various sizes",
            "features": "HDR support, high refresh rates, adjustable stands",
            "compatibility": "HDMI, DisplayPort, USB-C inputs",
            "support": "Color calibration and technical support"
        }
    }
    product = products.get(product_type.lower())
    if not product:
        return f"Technical specifications for {product_type} not available. Please contact our technical support team for detailed product information and compatibility requirements."
    return f"Technical Information - {product_type.title()}:\n\n" \
           f"• Warranty: {product['warranty']}\n" \
           f"• Specifications: {product['specs']}\n" \
           f"• Key Features: {product['features']}\n" \
           f"• Compatibility: {product['compatibility']}\n" \
           f"• Support: {product['support']}"

@tool(
    name="get_return_policy",
    description="Get return policy information for a specific product category"
)
def get_return_policy(product_category: str) -> str:
    return_policies = {
        "smartphones": {
            "window": "30 days",
            "condition": "Original packaging, no physical damage, factory reset required",
            "process": "Online RMA portal or technical support",
            "refund_time": "5-7 business days after inspection",
            "shipping": "Free return shipping, prepaid label provided",
            "warranty": "1-year manufacturer warranty included"
        },
        "laptops": {
            "window": "30 days", 
            "condition": "Original packaging, all accessories, no software modifications",
            "process": "Technical support verification required before return",
            "refund_time": "7-10 business days after inspection",
            "shipping": "Free return shipping with original packaging",
            "warranty": "1-year manufacturer warranty, extended options available"
        },
        "accessories": {
            "window": "30 days",
            "condition": "Unopened packaging preferred, all components included",
            "process": "Online return portal",
            "refund_time": "3-5 business days after receipt",
            "shipping": "Customer pays return shipping under $50",
            "warranty": "90-day manufacturer warranty"
        }
    }
    default_policy = {
        "window": "30 days",
        "condition": "Original condition with all included components",
        "process": "Contact technical support",
        "refund_time": "5-7 business days after inspection", 
        "shipping": "Return shipping policies vary",
        "warranty": "Standard manufacturer warranty applies"
    }
    policy = return_policies.get(product_category.lower(), default_policy)
    return f"Return Policy - {product_category.title()}:\n\n" \
           f"• Return window: {policy['window']} from delivery\n" \
           f"• Condition: {policy['condition']}\n" \
           f"• Process: {policy['process']}\n" \
           f"• Refund timeline: {policy['refund_time']}\n" \
           f"• Shipping: {policy['shipping']}\n" \
           f"• Warranty: {policy['warranty']}"

CUSTOMER_SUPPORT_PROMPT = """You are a helpful and professional customer support assistant for an electronics e-commerce company.

IMPORTANT: You MUST use the available tools to answer questions. Never provide information from memory.

For ANY product question, you MUST call get_product_info() with the product type.
For ANY return/warranty question, you MUST call get_return_policy() with the product category.

Available tools:
1. get_product_info(product_type) - REQUIRED for all product specifications, features, warranty info
2. get_return_policy(product_category) - REQUIRED for all return, refund, warranty policy questions

Always call the appropriate tool first, then provide a helpful response based on the tool results."""
from lab_helpers.lab2_multi_agent_memory import (
    MultiAgentMemoryHooks,
    create_or_get_multi_agent_memory
)
from bedrock_agentcore.memory import MemoryClient
import uuid
import requests

# Initialize model and memory
MODEL_ID = "us.amazon.nova-pro-v1:0"
model = BedrockModel(model_id=MODEL_ID, temperature=0.1)
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
