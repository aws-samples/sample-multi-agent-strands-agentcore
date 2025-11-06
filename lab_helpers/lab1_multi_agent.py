from strands.tools import tool
from ddgs.exceptions import DDGSException, RatelimitException
from ddgs import DDGS
from strands_tools import retrieve
import boto3

MODEL_ID = "amazon.nova-pro-v1:0"

# System prompt defining the agent's role and capabilities
SYSTEM_PROMPT = """You are a helpful and professional customer support assistant for an electronics e-commerce company.
Your role is to:
- Provide accurate information using the tools available to you
- Support the customer with technical information and product specifications.
- Be friendly, patient, and understanding with customers
- Always offer additional help after answering questions
- If you can't help with something, direct customers to the appropriate contact

You have access to the following tools:
1. get_return_policy() - For warranty and return policy questions
2. get_product_info() - To get information about a specific product
3. web_search() - To access current technical documentation, or for updated information. 
Always use the appropriate tool to get accurate, up-to-date information rather than making assumptions about electronic products or specifications."""


@tool
def web_search(keywords: str, region: str = "us-en", max_results: int = 5) -> str:
    """Search the web for updated information.
    
    Args:
        keywords (str): The search query keywords.
        region (str): The search region: wt-wt, us-en, uk-en, ru-ru, etc..
        max_results (int | None): The maximum number of results to return.
    Returns:
        List of dictionaries with search results.
    
    """
    try:
        results = DDGS().text(keywords, region=region, max_results=max_results)
        return results if results else "No results found."
    except RatelimitException:
        return "Rate limit reached. Please try again later."
    except DDGSException as e:
        return f"Search error: {e}"
    except Exception as e:
        return f"Search error: {str(e)}"


@tool
def get_return_policy(product_category: str) -> str:
    """
    Get return policy information for a specific product category.

    Args:
        product_category: Electronics category (e.g., 'smartphones', 'laptops', 'accessories')

    Returns:
        Formatted return policy details including timeframes and conditions
    """
    # Mock return policy database - in real implementation, this would query policy database
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

    # Default policy for unlisted categories
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


@tool
def get_product_info(product_type: str) -> str:
    """
    Get detailed technical specifications and information for electronics products.

    Args:
        product_type: Electronics product type (e.g., 'laptops', 'smartphones', 'headphones', 'monitors')
    Returns:
        Formatted product information including warranty, features, and policies
    """
    # Mock product catalog - in real implementation, this would query a product database
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

@tool
def get_technical_support(issue_description: str) -> str:
	try:
		# Get KB ID from parameter store
		ssm = boto3.client('ssm')
		account_id = boto3.client('sts').get_caller_identity()['Account']
		region = boto3.Session().region_name

		kb_id = ssm.get_parameter(Name=f"/{account_id}-{region}/kb/knowledge-base-id")['Parameter']['Value']
		print(f"Successfully retrieved KB ID: {kb_id}")

		# Use strands retrieve tool
		tool_use = {
			"toolUseId": "tech_support_query",
			"input": {
				"text": issue_description,
				"knowledgeBaseId": kb_id,
				"region": region,
				"numberOfResults": 3,
				"score": 0.4
			}
		}

		result = retrieve.retrieve(tool_use)

		if result["status"] == "success":
			return result["content"][0]["text"]
		else:
			return f"Unable to access technical support documentation. Error: {result['content'][0]['text']}"

	except Exception as e:
		print(f"Detailed error in get_technical_support: {str(e)}")
		return f"Unable to access technical support documentation. Error: {str(e)}"

# System prompts for different agent types
ORCHESTRATOR_PROMPT = """You are an intelligent orchestrator agent for a customer support system.
Your role is to analyze customer queries and route them to the most appropriate specialized agent:

1. **Customer Support Agent** - For general product questions, returns, warranties, and customer service
2. **Knowledge Base Agent** - For technical support, troubleshooting, and detailed technical documentation

Analyze the customer's query and determine which agent would be best suited to help them.
Provide clear routing decisions and coordinate responses when multiple agents are needed."""

CUSTOMER_SUPPORT_PROMPT = """You are a helpful and professional customer support assistant for an electronics e-commerce company.
Your role is to:
- Provide accurate information using the tools available to you
- Support the customer with technical information and product specifications.
- Be friendly, patient, and understanding with customers
- Always offer additional help after answering questions
- If you can't help with something, direct customers to the appropriate contact

You have access to the following tools:
1. get_return_policy() - For warranty and return policy questions
2. get_product_info() - To get information about a specific product
3. web_search() - To access current technical documentation, or for updated information. 
Always use the appropriate tool to get accurate, up-to-date information rather than making assumptions about electronic products or specifications."""

KNOWLEDGE_BASE_PROMPT = """You are a technical support specialist with access to comprehensive knowledge bases.
Your role is to:
- Provide detailed technical support and troubleshooting guidance
- Access technical documentation and knowledge bases for accurate information
- Help customers resolve technical issues with their electronic products
- Provide step-by-step troubleshooting instructions when needed

Use the get_technical_support() tool to access relevant technical documentation and provide accurate, helpful responses."""

@tool
def route_to_agent(query: str, agent_type: str = None) -> str:
    """Route a customer query to the appropriate specialized agent.
    
    Args:
        query (str): The customer's query or request
        agent_type (str): Optional specific agent type to route to ('customer_support', 'knowledge_base')
    
    Returns:
        str: Routing decision and any additional context
    """
    query_lower = query.lower()
    
    # Determine routing based on query content
    if agent_type:
        return f"Routing to {agent_type} agent: {query}"
    
    # Technical support keywords
    technical_keywords = ['troubleshoot', 'error', 'not working', 'broken', 'fix', 'technical', 'support', 'issue', 'problem']
    
    # Customer service keywords  
    service_keywords = ['return', 'refund', 'warranty', 'policy', 'order', 'shipping', 'product info', 'specifications']
    
    if any(keyword in query_lower for keyword in technical_keywords):
        return f"Routing to knowledge_base agent for technical support: {query}"
    elif any(keyword in query_lower for keyword in service_keywords):
        return f"Routing to customer_support agent for general support: {query}"
    else:
        return f"Routing to customer_support agent for general inquiry: {query}"

@tool
def coordinate_multi_agent_response(responses: list) -> str:
    """Coordinate and synthesize responses from multiple agents.
    
    Args:
        responses (list): List of responses from different agents
        
    Returns:
        str: Coordinated response combining insights from multiple agents
    """
    if not responses:
        return "No responses received from agents."
    
    if len(responses) == 1:
        return responses[0]
    
    # Combine multiple responses
    coordinated = "Based on input from our specialized agents:\n\n"
    for i, response in enumerate(responses, 1):
        coordinated += f"Agent {i}: {response}\n\n"
    
    coordinated += "This coordinated response provides comprehensive support for your inquiry."
    return coordinated