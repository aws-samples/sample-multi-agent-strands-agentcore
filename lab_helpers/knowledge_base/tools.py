# Knowledge Base Agent Tools

"""
Tools for the Knowledge Base Agent specializing in technical support
and troubleshooting using Bedrock Knowledge Base.
"""

from strands.tools import tool
import boto3
import json
from typing import Optional

@tool
def get_technical_support(query: str, max_results: int = 3) -> str:
    """Get technical support information from the knowledge base.
    
    Args:
        query (str): The technical support query
        max_results (int): Maximum number of results to return
    
    Returns:
        str: Technical support information and troubleshooting steps
    """
    
    # Simulated knowledge base for technical support
    # In a real implementation, this would query Bedrock Knowledge Base
    knowledge_base = {
        "overheating": {
            "title": "Device Overheating Issues",
            "solution": """
**Common Causes & Solutions:**

1. **Check Ventilation**
   - Ensure device vents are not blocked
   - Clean dust from fans and vents using compressed air
   - Use device on hard, flat surfaces for better airflow

2. **Monitor Resource Usage**
   - Close unnecessary applications
   - Check Task Manager/Activity Monitor for high CPU usage
   - Update drivers and software

3. **Environmental Factors**
   - Keep device away from direct sunlight
   - Ensure room temperature is below 80°F (27°C)
   - Consider using a cooling pad for laptops

4. **Hardware Issues**
   - Thermal paste may need replacement (professional service)
   - Internal fans might be failing
   - Battery swelling can cause overheating
            """,
            "severity": "medium"
        },
        "battery": {
            "title": "Battery Drain and Performance Issues", 
            "solution": """
**Battery Optimization Steps:**

1. **Check Battery Health**
   - iOS: Settings > Battery > Battery Health
   - Android: Settings > Battery > Battery Usage
   - Windows: powercfg /batteryreport

2. **Optimize Settings**
   - Reduce screen brightness
   - Turn off location services for unused apps
   - Disable background app refresh
   - Use power saving mode

3. **Update Software**
   - Install latest OS updates
   - Update all applications
   - Reset network settings if needed

4. **Hardware Considerations**
   - Battery may need replacement after 2-3 years
   - Avoid extreme temperatures
   - Don't let battery completely drain regularly
            """,
            "severity": "low"
        },
        "connectivity": {
            "title": "Wireless Connectivity Problems",
            "solution": """
**WiFi/Bluetooth Troubleshooting:**

1. **Basic Troubleshooting**
   - Restart device and router
   - Forget and reconnect to network
   - Check if other devices have same issue

2. **Network Settings**
   - Reset network settings
   - Update network drivers
   - Check for interference (2.4GHz vs 5GHz)

3. **Advanced Solutions**
   - Update router firmware
   - Change DNS settings (8.8.8.8, 1.1.1.1)
   - Check for IP conflicts

4. **Hardware Issues**
   - WiFi antenna may be damaged
   - Bluetooth module might need replacement
   - Contact support for hardware diagnostics
            """,
            "severity": "medium"
        },
        "performance": {
            "title": "Slow Performance and Lag Issues",
            "solution": """
**Performance Optimization:**

1. **Storage Management**
   - Free up disk space (keep 15% free minimum)
   - Run disk cleanup utilities
   - Move files to external storage

2. **Memory Optimization**
   - Close unused applications
   - Restart device regularly
   - Check for memory leaks in apps

3. **Software Maintenance**
   - Update operating system
   - Update all drivers
   - Run antivirus scan
   - Disable startup programs

4. **Hardware Upgrades**
   - Consider RAM upgrade
   - SSD upgrade for better performance
   - Check if hardware meets software requirements
            """,
            "severity": "medium"
        }
    }
    
    query_lower = query.lower()
    
    # Find relevant knowledge base entries
    relevant_entries = []
    
    for key, entry in knowledge_base.items():
        if (key in query_lower or 
            any(word in query_lower for word in key.split()) or
            any(word in entry['title'].lower() for word in query_lower.split())):
            relevant_entries.append((key, entry))
    
    if not relevant_entries:
        # Provide general troubleshooting if no specific match
        return """
📚 **General Technical Support Guidelines:**

1. **First Steps**
   - Restart the device
   - Check for software updates
   - Verify all connections are secure

2. **Common Issues**
   - Overheating: Check ventilation and clean vents
   - Battery issues: Optimize power settings
   - Connectivity: Restart router and device
   - Performance: Free up storage space

3. **When to Contact Support**
   - Hardware damage or defects
   - Issues persist after troubleshooting
   - Device under warranty needs service

📞 For specific technical issues, contact our technical support team.
        """
    
    # Format the response
    result = "🔧 **Technical Support Information:**\\n\\n"
    
    for i, (key, entry) in enumerate(relevant_entries[:max_results], 1):
        result += f"**{i}. {entry['title']}**\\n"
        result += f"🚨 Severity: {entry['severity'].title()}\\n"
        result += f"{entry['solution']}\\n"
        
        if i < len(relevant_entries[:max_results]):
            result += "\\n" + "-" * 50 + "\\n\\n"
    
    result += "\\n📞 If these steps don't resolve the issue, please contact technical support for further assistance."
    
    return result

@tool 
def search_knowledge_base(topic: str, category: str = "general") -> str:
    """Search the technical knowledge base for specific topics.
    
    Args:
        topic (str): The topic to search for
        category (str): Category to search within (general, hardware, software, network)
    
    Returns:
        str: Knowledge base search results
    """
    
    # Simulated knowledge base search
    # In production, this would use Bedrock Knowledge Base retrieval
    
    categories = {
        "hardware": [
            "CPU overheating solutions",
            "RAM upgrade compatibility", 
            "Hard drive replacement procedures",
            "Graphics card troubleshooting",
            "Power supply diagnostics"
        ],
        "software": [
            "Operating system optimization",
            "Driver update procedures",
            "Application compatibility issues",
            "Security software configuration",
            "System restore procedures"
        ],
        "network": [
            "WiFi connectivity troubleshooting",
            "Ethernet connection issues",
            "VPN setup and configuration",
            "Firewall configuration",
            "Network speed optimization"
        ],
        "general": [
            "Device maintenance schedules",
            "Warranty information and claims",
            "Data backup procedures", 
            "Security best practices",
            "Performance monitoring tools"
        ]
    }
    
    category_lower = category.lower()
    topic_lower = topic.lower()
    
    if category_lower not in categories:
        available_categories = ", ".join(categories.keys())
        return f"❌ Category '{category}' not found. Available categories: {available_categories}"
    
    # Find matching topics
    matching_topics = [
        item for item in categories[category_lower]
        if any(word in item.lower() for word in topic_lower.split())
    ]
    
    if not matching_topics:
        return f"❌ No knowledge base entries found for '{topic}' in category '{category}'"
    
    result = f"📖 **Knowledge Base Results for '{topic}' in {category.title()}:**\\n\\n"
    
    for i, item in enumerate(matching_topics[:3], 1):
        result += f"{i}. {item}\\n"
    
    result += f"\\n📚 Found {len(matching_topics)} relevant entries. Use get_technical_support() for detailed solutions."
    
    return result