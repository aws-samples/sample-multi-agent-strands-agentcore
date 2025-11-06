# Memory Utilities for Multi-Agent System

"""
Utility functions and classes for managing memory in multi-agent systems.
Includes namespace management, seeding utilities, and memory analysis tools.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from bedrock_agentcore.memory import MemoryClient

logger = logging.getLogger(__name__)


@dataclass
class MemoryNamespace:
    """Represents a memory namespace with metadata"""
    name: str
    agent_type: str
    strategy_type: str
    description: str
    
    def format_for_actor(self, actor_id: str) -> str:
        """Format namespace with actor ID"""
        return self.name.format(actorId=actor_id)


class MemoryNamespaceManager:
    """Manages memory namespaces for multi-agent systems"""
    
    # Predefined namespaces for multi-agent customer support (simplified)
    NAMESPACES = [
        MemoryNamespace(
            name="support/customer/{actorId}/preferences",
            agent_type="all",
            strategy_type="USER_PREFERENCE",
            description="Customer preferences and behavior patterns"
        ),
        MemoryNamespace(
            name="support/customer/{actorId}/semantic", 
            agent_type="all",
            strategy_type="SEMANTIC",
            description="Factual information shared across agents"
        ),
    ]
    
    @classmethod
    def get_namespaces_for_agent(cls, agent_type: str) -> List[MemoryNamespace]:
        """Get namespaces relevant to a specific agent type"""
        return [
            ns for ns in cls.NAMESPACES 
            if ns.agent_type == agent_type or ns.agent_type == "all"
        ]
    
    @classmethod
    def get_all_namespaces(cls) -> List[MemoryNamespace]:
        """Get all available namespaces"""
        return cls.NAMESPACES.copy()
    
    @classmethod
    def format_namespaces_for_actor(cls, actor_id: str, agent_type: str = None) -> List[str]:
        """Format namespaces for a specific actor and optionally filter by agent type"""
        namespaces = cls.get_namespaces_for_agent(agent_type) if agent_type else cls.get_all_namespaces()
        return [ns.format_for_actor(actor_id) for ns in namespaces]


class MemorySeeder:
    """Utility class for seeding memory with realistic multi-agent data"""
    
    def __init__(self, memory_client: MemoryClient, memory_id: str):
        self.client = memory_client
        self.memory_id = memory_id
    
    def seed_customer_interactions(self, actor_id: str) -> bool:
        """Seed realistic customer support interactions"""
        
        interactions = [
            # Initial customer support interaction
            (
                "I need help with my MacBook Pro that's overheating during video editing. It's getting really hot and the fans are loud.",
                "USER"
            ),
            (
                "I can help with thermal management issues. Let me check your system specifications and provide some optimization tips. Your MacBook Pro model and usage pattern suggests this is likely related to intensive video processing workloads. [Handled by CustomerSupport]",
                "ASSISTANT"
            ),
            
            # Technical support handoff
            (
                "The basic tips didn't work. I'm still getting thermal throttling during 4K video exports in Final Cut Pro.",
                "USER"
            ),
            (
                "For persistent thermal issues during 4K video exports, let me provide advanced troubleshooting steps including Activity Monitor analysis, thermal paste considerations, and professional video editing optimization settings. [Handled by KnowledgeBase]",
                "ASSISTANT"
            ),
            
            # Customer preferences emerge
            (
                "I'm looking for a new laptop under $1500 for programming and light gaming. I prefer ThinkPad models and need good Linux compatibility.",
                "USER"
            ),
            (
                "Based on your preferences for ThinkPad models and Linux compatibility, I'd recommend the ThinkPad E series or T series within your budget. Both offer excellent development environments and gaming capabilities. [Handled by CustomerSupport]",
                "ASSISTANT"
            ),
            
            # Gaming headphone inquiry
            (
                "What's your return policy on gaming headphones? I need low latency for competitive FPS games like CS2 and Valorant.",
                "USER"
            ),
            (
                "Our gaming headphones have a 30-day return policy. For competitive FPS gaming, you'll want headphones with under 40ms latency. I can recommend several models that meet these requirements. [Handled by CustomerSupport]",
                "ASSISTANT"
            ),
            
            # Technical follow-up
            (
                "My MacBook is still having issues. Can you help me check if it's a hardware problem?",
                "USER"
            ),
            (
                "Let's run comprehensive hardware diagnostics. Based on your previous thermal issues, we should check the cooling system, thermal sensors, and CPU performance under load. I'll guide you through Apple Diagnostics. [Handled by KnowledgeBase]",
                "ASSISTANT"
            ),
        ]
        
        try:
            self.client.create_event(
                memory_id=self.memory_id,
                actor_id=actor_id,
                session_id="historical_session_1",
                messages=interactions
            )
            logger.info(f"Seeded {len(interactions)} customer interactions for {actor_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to seed customer interactions: {e}")
            return False
    
    def seed_routing_decisions(self, actor_id: str) -> bool:
        """Seed orchestrator routing decisions"""
        
        routing_decisions = [
            ("Thermal management and overheating issues", "KnowledgeBase", "Technical problem requiring specialized troubleshooting"),
            ("Product recommendations and pricing", "CustomerSupport", "General product inquiry within customer support scope"),
            ("Return policy questions", "CustomerSupport", "Policy-related inquiry handled by customer support"),
            ("Hardware diagnostics and advanced troubleshooting", "KnowledgeBase", "Complex technical issue requiring knowledge base expertise"),
            ("Gaming headphone recommendations", "CustomerSupport", "Product recommendation with customer preference consideration"),
            ("Linux compatibility questions", "CustomerSupport", "Product compatibility inquiry for customer support"),
        ]
        
        try:
            for query, agent, reasoning in routing_decisions:
                routing_info = f"Query: {query}\nRouted to: {agent}\nReasoning: {reasoning}"
                self.client.create_event(
                    memory_id=self.memory_id,
                    actor_id=actor_id,
                    session_id="routing_history",
                    messages=[(f"Routing Decision: {routing_info}", "OTHER")]
                )
            
            logger.info(f"Seeded {len(routing_decisions)} routing decisions for {actor_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to seed routing decisions: {e}")
            return False
    
    def seed_technical_solutions(self, actor_id: str) -> bool:
        """Seed technical solutions and troubleshooting history"""
        
        solutions = [
            (
                "MacBook Pro overheating during video editing",
                "Check Activity Monitor for CPU usage, reset SMC, verify thermal paste, adjust video export settings for lower CPU load",
                True
            ),
            (
                "Gaming headphone audio latency issues",
                "Use wired connection for competitive gaming, check audio driver settings, disable audio enhancements, use dedicated gaming audio profiles",
                True
            ),
            (
                "Linux compatibility for ThinkPad models",
                "Verify hardware compatibility list, check for proprietary drivers, test with live USB before purchase, consider certified Linux models",
                True
            ),
        ]
        
        try:
            for problem, solution, success in solutions:
                solution_info = f"Problem: {problem}\nSolution: {solution}\nSuccess: {success}"
                self.client.create_event(
                    memory_id=self.memory_id,
                    actor_id=actor_id,
                    session_id="technical_solutions",
                    messages=[(f"Technical Solution: {solution_info}", "OTHER")]
                )
            
            logger.info(f"Seeded {len(solutions)} technical solutions for {actor_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to seed technical solutions: {e}")
            return False
    
    def seed_all_data(self, actor_id: str) -> Dict[str, bool]:
        """Seed all types of memory data"""
        
        results = {
            "customer_interactions": self.seed_customer_interactions(actor_id),
            "routing_decisions": self.seed_routing_decisions(actor_id),
            "technical_solutions": self.seed_technical_solutions(actor_id),
        }
        
        success_count = sum(results.values())
        logger.info(f"Seeding completed: {success_count}/{len(results)} successful")
        
        return results


class MemoryAnalyzer:
    """Utility class for analyzing memory contents and patterns"""
    
    def __init__(self, memory_client: MemoryClient, memory_id: str):
        self.client = memory_client
        self.memory_id = memory_id
    
    def analyze_customer_preferences(self, actor_id: str, query: str = "customer preferences") -> Dict[str, Any]:
        """Analyze customer preferences from memory"""
        
        try:
            namespace = f"support/customer/{actor_id}/preferences"
            memories = self.client.retrieve_memories(
                memory_id=self.memory_id,
                namespace=namespace,
                query=query,
                top_k=10
            )
            
            preferences = []
            for memory in memories:
                if isinstance(memory, dict):
                    content = memory.get("content", {})
                    if isinstance(content, dict):
                        text = content.get("text", "").strip()
                        if text:
                            preferences.append(text)
            
            return {
                "namespace": namespace,
                "total_preferences": len(preferences),
                "preferences": preferences,
                "query_used": query
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze customer preferences: {e}")
            return {"error": str(e)}
    
    def analyze_technical_solutions(self, actor_id: str, query: str = "technical solutions") -> Dict[str, Any]:
        """Analyze technical solutions from memory"""
        
        try:
            namespace = f"support/technical/{actor_id}/solutions"
            memories = self.client.retrieve_memories(
                memory_id=self.memory_id,
                namespace=namespace,
                query=query,
                top_k=10
            )
            
            solutions = []
            for memory in memories:
                if isinstance(memory, dict):
                    content = memory.get("content", {})
                    if isinstance(content, dict):
                        text = content.get("text", "").strip()
                        if text:
                            solutions.append(text)
            
            return {
                "namespace": namespace,
                "total_solutions": len(solutions),
                "solutions": solutions,
                "query_used": query
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze technical solutions: {e}")
            return {"error": str(e)}
    
    def analyze_routing_patterns(self, actor_id: str, query: str = "routing decisions") -> Dict[str, Any]:
        """Analyze orchestrator routing patterns"""
        
        try:
            namespace = f"support/orchestrator/{actor_id}/routing"
            memories = self.client.retrieve_memories(
                memory_id=self.memory_id,
                namespace=namespace,
                query=query,
                top_k=10
            )
            
            patterns = []
            agent_counts = {}
            
            for memory in memories:
                if isinstance(memory, dict):
                    content = memory.get("content", {})
                    if isinstance(content, dict):
                        text = content.get("text", "").strip()
                        if text:
                            patterns.append(text)
                            # Count agent routing
                            if "CustomerSupport" in text:
                                agent_counts["CustomerSupport"] = agent_counts.get("CustomerSupport", 0) + 1
                            elif "KnowledgeBase" in text:
                                agent_counts["KnowledgeBase"] = agent_counts.get("KnowledgeBase", 0) + 1
            
            return {
                "namespace": namespace,
                "total_patterns": len(patterns),
                "patterns": patterns,
                "agent_distribution": agent_counts,
                "query_used": query
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze routing patterns: {e}")
            return {"error": str(e)}
    
    def get_comprehensive_analysis(self, actor_id: str) -> Dict[str, Any]:
        """Get comprehensive memory analysis for an actor"""
        
        return {
            "actor_id": actor_id,
            "customer_preferences": self.analyze_customer_preferences(actor_id),
            "technical_solutions": self.analyze_technical_solutions(actor_id),
            "routing_patterns": self.analyze_routing_patterns(actor_id),
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }