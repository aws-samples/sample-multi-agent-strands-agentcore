# Orchestrator Agent Implementation

"""
Orchestrator agent for multi-agent customer support system.
Handles intelligent routing between specialized agents with optional memory enhancement.
"""

import logging
from typing import Dict, Any, Tuple, Optional

from strands import Agent
from strands.models import BedrockModel

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """Basic orchestrator agent for routing customer queries"""
    
    def __init__(self, model: BedrockModel, customer_support_agent: Agent, knowledge_base_agent: Agent):
        self.model = model
        self.customer_support = customer_support_agent
        self.knowledge_base = knowledge_base_agent
        
        # Create routing agent
        self.routing_agent = Agent(
            model=model,
            system_prompt="""
You are an Orchestrator Agent that routes customer queries to appropriate specialists.

Available agents:
- CustomerSupport: Product info, returns, policies, general inquiries, recommendations
- KnowledgeBase: Technical issues, troubleshooting, hardware problems, complex technical support

Analyze the customer query and determine which agent can best help.
Consider the complexity and type of the request.

Respond with: ROUTE_TO: [CustomerSupport|KnowledgeBase] - [brief reasoning]
"""
        )
    
    def route_query(self, query: str) -> Tuple[Agent, str]:
        """Route query to appropriate agent"""
        try:
            # Get routing decision
            response = self.routing_agent.invoke(f"Route this query: {query}")
            routing_response = response.get('content', [{}])[0].get('text', '')
            
            # Parse routing decision
            if "ROUTE_TO: CustomerSupport" in routing_response:
                return self.customer_support, "CustomerSupport"
            elif "ROUTE_TO: KnowledgeBase" in routing_response:
                return self.knowledge_base, "KnowledgeBase"
            else:
                # Default to customer support
                return self.customer_support, "CustomerSupport"
                
        except Exception as e:
            logger.error(f"Routing failed: {e}")
            return self.customer_support, "CustomerSupport"
    
    def handle_query(self, query: str) -> Dict[str, Any]:
        """Handle customer query with routing"""
        print(f"\n🎯 Orchestrator analyzing query...")
        
        # Route to appropriate agent
        selected_agent, agent_name = self.route_query(query)
        
        print(f"📍 Routed to: {agent_name}")
        
        # Execute query with selected agent
        response = selected_agent.invoke(query)
        
        return {
            'routed_to': agent_name,
            'response': response
        }


class MemoryEnhancedOrchestrator:
    """Memory-enhanced orchestrator with routing intelligence"""
    
    def __init__(self, model: BedrockModel, customer_support_agent: Agent, 
                 knowledge_base_agent: Agent, memory_hook: Optional[Any] = None):
        self.model = model
        self.customer_support = customer_support_agent
        self.knowledge_base = knowledge_base_agent
        self.memory_hook = memory_hook
        
        # Create memory-enhanced routing agent
        hooks = [memory_hook] if memory_hook else []
        
        self.routing_agent = Agent(
            model=model,
            hooks=hooks,
            system_prompt="""
You are an Orchestrator Agent with memory of past routing decisions.

Available agents:
- CustomerSupport: Product info, returns, policies, general inquiries, recommendations
- KnowledgeBase: Technical issues, troubleshooting, hardware problems, complex technical support

Analyze customer queries and route them to the most appropriate agent.
Use your memory of past successful routing decisions to improve accuracy.
Consider customer history and preferences when making routing decisions.

Respond with: ROUTE_TO: [CustomerSupport|KnowledgeBase] - [reasoning]
"""
        )
    
    def route_query(self, query: str) -> Tuple[Agent, str]:
        """Route query to appropriate agent using memory-enhanced decision making"""
        try:
            # Get routing decision from memory-enhanced agent
            response = self.routing_agent.invoke(f"Route this query: {query}")
            routing_response = response.get('content', [{}])[0].get('text', '')
            
            # Parse routing decision
            if "ROUTE_TO: CustomerSupport" in routing_response:
                selected_agent = self.customer_support
                agent_name = "CustomerSupport"
            elif "ROUTE_TO: KnowledgeBase" in routing_response:
                selected_agent = self.knowledge_base
                agent_name = "KnowledgeBase"
            else:
                # Default to customer support
                selected_agent = self.customer_support
                agent_name = "CustomerSupport"
                routing_response = "Default routing to CustomerSupport"
            
            # Save routing decision to memory if memory hook is available
            if self.memory_hook and hasattr(self.memory_hook, 'save_routing_decision'):
                self.memory_hook.save_routing_decision(query, agent_name, routing_response)
            
            return selected_agent, agent_name
            
        except Exception as e:
            logger.error(f"Memory-enhanced routing failed: {e}")
            return self.customer_support, "CustomerSupport"
    
    def handle_query(self, query: str) -> Dict[str, Any]:
        """Handle customer query with memory-enhanced routing"""
        print(f"\n🎯 Orchestrator analyzing query with memory context...")
        
        # Route to appropriate agent
        selected_agent, agent_name = self.route_query(query)
        
        print(f"📍 Routed to: {agent_name}")
        
        # Execute query with selected agent
        response = selected_agent.invoke(query)
        
        return {
            'routed_to': agent_name,
            'response': response
        }