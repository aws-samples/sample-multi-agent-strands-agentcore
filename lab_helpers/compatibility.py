# Compatibility layer for Lab 3
from strands import tool

# Import the complete memory hooks from lab2
from .lab2_multi_agent_memory import CustomerSupportMemoryHooks, create_or_get_memory_resource

# Define agent tools (same as in notebooks)
@tool(
    name="get_product_info",
    description="Get detailed product information and specifications"
)
def get_product_info(product_name: str) -> str:
    """Get product information for customer inquiries"""
    products = {
        "laptop": "Gaming Laptop Pro: 16GB RAM, RTX 4060, Intel i7, $1299",
        "headphones": "Gaming Headset X1: Wireless, 40ms latency, $199",
        "phone": "Smartphone Ultra: 128GB, 5G, Triple camera, $899"
    }
    
    for key, info in products.items():
        if key in product_name.lower():
            return f"Product Information: {info}"
    
    return "Product not found. Please check our catalog for available items."

@tool(
    name="get_return_policy",
    description="Get return policy information for products"
)
def get_return_policy(product_type: str) -> str:
    """Get return policy for different product categories"""
    policies = {
        "electronics": "30-day return policy with original packaging",
        "headphones": "30-day return policy, must be in original condition",
        "laptops": "15-day return policy for laptops, restocking fee may apply"
    }
    
    for key, policy in policies.items():
        if key in product_type.lower():
            return f"Return Policy: {policy}"
    
    return "Standard 30-day return policy applies. Contact support for details."

@tool(
    name="get_technical_support",
    description="Get technical support information from knowledge base"
)
def get_technical_support(issue: str) -> str:
    """Get technical support solutions"""
    solutions = {
        "overheating": "Check ventilation, clean fans, monitor CPU usage, consider thermal paste replacement",
        "battery": "Calibrate battery, check power settings, replace if over 2 years old",
        "performance": "Update drivers, check for malware, increase RAM if needed"
    }
    
    for key, solution in solutions.items():
        if key in issue.lower():
            return f"Technical Solution: {solution}"
    
    return "Please provide more details about the technical issue for specific troubleshooting steps."

# System prompt for agents
SYSTEM_PROMPT = """
You are a Customer Support Agent with access to customer memory and preferences.
Use customer context to provide personalized recommendations and support.
Handle product inquiries, return policies, and general customer service.
Always acknowledge customer preferences and past interactions when relevant.
"""

