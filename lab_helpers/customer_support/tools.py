# Customer Support Agent Tools

"""
Tools for the Customer Support Agent specializing in product information,
return policies, and general customer support tasks.
"""

from strands.tools import tool
from ddgs.exceptions import DDGSException, RatelimitException
from ddgs import DDGS
import json

@tool
def get_product_info(product_category: str) -> str:
    """Get detailed product information and specifications.
    
    Args:
        product_category (str): The category of product to get information about
        (e.g., 'laptops', 'smartphones', 'headphones', 'gaming consoles')
    
    Returns:
        str: Detailed product information and specifications
    """
    
    # Simulated product database
    products = {
        "laptops": {
            "Gaming Laptop Pro": {
                "price": "$1,299",
                "specs": "Intel i7, 16GB RAM, RTX 4060, 512GB SSD",
                "features": "144Hz display, RGB keyboard, advanced cooling"
            },
            "Business Laptop Elite": {
                "price": "$899", 
                "specs": "Intel i5, 8GB RAM, Integrated graphics, 256GB SSD",
                "features": "Lightweight, 12-hour battery, fingerprint reader"
            }
        },
        "smartphones": {
            "iPhone 14": {
                "price": "$799",
                "specs": "A15 Bionic chip, 128GB storage, 6.1-inch display",
                "features": "Advanced camera system, Face ID, 5G capable"
            },
            "Galaxy S23": {
                "price": "$699",
                "specs": "Snapdragon 8 Gen 2, 128GB storage, 6.1-inch display", 
                "features": "Triple camera, S Pen compatible, wireless charging"
            }
        },
        "headphones": {
            "Gaming Headset X": {
                "price": "$149",
                "specs": "7.1 surround sound, 50mm drivers, USB/3.5mm",
                "features": "Noise canceling mic, RGB lighting, comfortable padding"
            },
            "Wireless Earbuds Pro": {
                "price": "$199",
                "specs": "Active noise cancellation, 6-hour battery + case",
                "features": "Wireless charging, water resistant, premium audio"
            }
        },
        "gaming consoles": {
            "Gaming Console Pro": {
                "price": "$499",
                "specs": "Custom AMD processor, 1TB SSD, 4K gaming",
                "features": "Ray tracing, 120fps support, backward compatibility"
            }
        }
    }
    
    category_lower = product_category.lower()
    
    if category_lower in products:
        category_products = products[category_lower]
        result = f"📱 **{product_category.title()} Available:**\\n\\n"
        
        for product_name, details in category_products.items():
            result += f"**{product_name}**\\n"
            result += f"💰 Price: {details['price']}\\n"
            result += f"⚙️ Specs: {details['specs']}\\n"
            result += f"✨ Features: {details['features']}\\n\\n"
        
        return result
    else:
        available_categories = ", ".join(products.keys())
        return f"❌ Product category '{product_category}' not found. Available categories: {available_categories}"

@tool
def get_return_policy(product_category: str) -> str:
    """Get return policy information for specific product categories.
    
    Args:
        product_category (str): The category of product to get return policy for
    
    Returns:
        str: Return policy information for the specified category
    """
    
    # Return policies by category
    policies = {
        "electronics": {
            "return_period": "30 days",
            "condition": "Original packaging and accessories required",
            "restocking_fee": "15% for opened items",
            "exceptions": "Custom configured items non-returnable"
        },
        "laptops": {
            "return_period": "30 days", 
            "condition": "Must be in original condition with all accessories",
            "restocking_fee": "20% if opened and used",
            "exceptions": "Custom builds and software installations void return"
        },
        "smartphones": {
            "return_period": "14 days",
            "condition": "Must be unlocked and factory reset",
            "restocking_fee": "25% restocking fee applies",
            "exceptions": "Carrier-locked phones have different terms"
        },
        "headphones": {
            "return_period": "30 days",
            "condition": "Hygiene seal must be intact for returns",
            "restocking_fee": "No restocking fee if unopened",
            "exceptions": "Wireless earbuds non-returnable once opened"
        },
        "gaming": {
            "return_period": "30 days",
            "condition": "All original packaging and accessories required", 
            "restocking_fee": "10% restocking fee",
            "exceptions": "Digital game codes cannot be returned"
        }
    }
    
    category_lower = product_category.lower()
    
    # Check for exact match or partial match
    policy = None
    if category_lower in policies:
        policy = policies[category_lower]
        category_name = category_lower
    else:
        # Check for partial matches
        for key in policies.keys():
            if category_lower in key or key in category_lower:
                policy = policies[key]
                category_name = key
                break
    
    if policy:
        result = f"📋 **Return Policy for {category_name.title()}:**\\n\\n"
        result += f"⏰ **Return Period:** {policy['return_period']}\\n"
        result += f"📦 **Condition:** {policy['condition']}\\n"
        result += f"💵 **Restocking Fee:** {policy['restocking_fee']}\\n"
        result += f"⚠️ **Exceptions:** {policy['exceptions']}\\n\\n"
        result += "📞 For specific questions, contact customer service at 1-800-SUPPORT"
        return result
    else:
        available_categories = ", ".join(policies.keys())
        return f"❌ No return policy found for '{product_category}'. Available categories: {available_categories}"

@tool
def web_search(keywords: str, region: str = "us-en", max_results: int = 5) -> str:
    """Search the web for updated information.
    
    Args:
        keywords (str): The search query keywords
        region (str): The search region (us-en, uk-en, etc.)
        max_results (int): Maximum number of results to return
    
    Returns:
        str: Search results or error message
    """
    try:
        results = DDGS().text(keywords, region=region, max_results=max_results)
        
        if not results:
            return "No search results found."
        
        # Format results for better readability
        formatted_results = "🔍 **Web Search Results:**\\n\\n"
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            body = result.get('body', 'No description')
            href = result.get('href', 'No URL')
            
            formatted_results += f"**{i}. {title}**\\n"
            formatted_results += f"📝 {body[:200]}{'...' if len(body) > 200 else ''}\\n"
            formatted_results += f"🔗 {href}\\n\\n"
        
        return formatted_results
        
    except RatelimitException:
        return "⚠️ Search rate limit reached. Please try again later."
    except DDGSException as e:
        return f"❌ Search error: {e}"
    except Exception as e:
        return f"❌ Unexpected search error: {str(e)}"