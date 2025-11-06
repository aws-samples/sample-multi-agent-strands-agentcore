# Multi-Agent Memory Client

"""
Enhanced memory client for multi-agent systems with specialized operations
and cross-agent context management.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.constants import StrategyType

from ..shared.utils import get_region, progress_tracker

logger = logging.getLogger(__name__)


class MultiAgentMemoryClient:
    """Enhanced memory client for multi-agent customer support system"""
    
    def __init__(self, region_name: Optional[str] = None):
        self.region_name = region_name or get_region()
        self.client = MemoryClient(region_name=self.region_name)
        self._memory_id = None
        
    @property
    def memory_id(self) -> Optional[str]:
        """Get the current memory ID"""
        if self._memory_id is None:
            # Try to get from progress tracker
            progress = progress_tracker.progress
            self._memory_id = progress.get('setup_status', {}).get('memory_id')
        return self._memory_id
    
    @memory_id.setter
    def memory_id(self, value: str):
        """Set the memory ID and save to progress tracker"""
        self._memory_id = value
        if 'setup_status' not in progress_tracker.progress:
            progress_tracker.progress['setup_status'] = {}
        progress_tracker.progress['setup_status']['memory_id'] = value
        progress_tracker.save_progress()

    def create_multi_agent_memory(self, name: str = "MultiAgentCustomerSupportMemory") -> str:
        """Create memory resource optimized for multi-agent systems"""
        
        strategies = [
            {
                StrategyType.USER_PREFERENCE.value: {
                    "name": "CustomerPreferences",
                    "description": "Customer preferences and behavior patterns",
                    "namespaces": ["support/customer/{actorId}/preferences"],
                }
            },
            {
                StrategyType.SEMANTIC.value: {
                    "name": "CustomerSemanticMemory",
                    "description": "Factual information shared across agents",
                    "namespaces": ["support/customer/{actorId}/semantic"],
                }
            },
        ]
        
        try:
            logger.info("Creating multi-agent memory infrastructure...")
            response = self.client.create_memory_and_wait(
                name=name,
                description="Multi-agent customer support system memory",
                strategies=strategies,
                event_expiry_days=90,
            )
            
            memory_id = response["id"]
            self.memory_id = memory_id  # This will save to progress tracker
            
            logger.info(f"Multi-agent memory created: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"Failed to create multi-agent memory: {e}")
            raise

    def get_or_create_memory(self, name: str = "MultiAgentCustomerSupportMemory") -> str:
        """Get existing memory or create new one"""
        
        # Try to get existing memory
        if self.memory_id:
            try:
                self.client.gmcp_client.get_memory(memoryId=self.memory_id)
                logger.info(f"Using existing memory: {self.memory_id}")
                return self.memory_id
            except Exception:
                logger.warning("Existing memory ID not valid, creating new memory")
        
        # Create new memory
        return self.create_multi_agent_memory(name)

    def seed_multi_agent_interactions(self, actor_id: str, interactions: List[Tuple[str, str]]):
        """Seed memory with multi-agent customer interactions"""
        
        if not self.memory_id:
            raise ValueError("Memory ID not set. Create memory first.")
        
        try:
            self.client.create_event(
                memory_id=self.memory_id,
                actor_id=actor_id,
                session_id="historical_interactions",
                messages=interactions
            )
            logger.info(f"Seeded {len(interactions)} interactions for actor {actor_id}")
            
        except Exception as e:
            logger.error(f"Failed to seed interactions: {e}")
            raise

    def seed_routing_decisions(self, actor_id: str, routing_decisions: List[Tuple[str, str, str]]):
        """Seed orchestrator routing decisions"""
        
        if not self.memory_id:
            raise ValueError("Memory ID not set. Create memory first.")
        
        try:
            for query, agent, reasoning in routing_decisions:
                routing_info = f"Query: {query}\nRouted to: {agent}\nReasoning: {reasoning}"
                self.client.create_event(
                    memory_id=self.memory_id,
                    actor_id=actor_id,
                    session_id="routing_history",
                    messages=[(f"Routing Decision: {routing_info}", "SYSTEM")]
                )
            
            logger.info(f"Seeded {len(routing_decisions)} routing decisions for actor {actor_id}")
            
        except Exception as e:
            logger.error(f"Failed to seed routing decisions: {e}")
            raise

    def get_cross_agent_context(self, actor_id: str, query: str, agent_types: List[str] = None) -> Dict[str, List[str]]:
        """Get context from multiple agent namespaces"""
        
        if not self.memory_id:
            return {}
        
        agent_types = agent_types or ["customer", "orchestrator", "technical"]
        context = {}
        
        for agent_type in agent_types:
            try:
                namespace = f"support/{agent_type}/{actor_id}"
                if agent_type == "customer":
                    # Check both preferences and semantic for customer
                    for subtype in ["preferences", "semantic"]:
                        full_namespace = f"{namespace}/{subtype}"
                        memories = self.client.retrieve_memories(
                            memory_id=self.memory_id,
                            namespace=full_namespace,
                            query=query,
                            top_k=2
                        )
                        
                        context[f"{agent_type}_{subtype}"] = [
                            memory.get("content", {}).get("text", "")
                            for memory in memories
                            if isinstance(memory, dict) and memory.get("content", {}).get("text")
                        ]
                else:
                    # Single namespace for other agent types
                    subtype = "routing" if agent_type == "orchestrator" else "solutions"
                    full_namespace = f"{namespace}/{subtype}"
                    memories = self.client.retrieve_memories(
                        memory_id=self.memory_id,
                        namespace=full_namespace,
                        query=query,
                        top_k=2
                    )
                    
                    context[agent_type] = [
                        memory.get("content", {}).get("text", "")
                        for memory in memories
                        if isinstance(memory, dict) and memory.get("content", {}).get("text")
                    ]
                    
            except Exception as e:
                logger.error(f"Failed to get context for {agent_type}: {e}")
                context[agent_type] = []
        
        return context

    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get statistics about the memory system"""
        
        if not self.memory_id:
            return {"error": "No memory ID available"}
        
        try:
            # Get memory details
            memory_info = self.client.gmcp_client.get_memory(memoryId=self.memory_id)
            strategies = self.client.get_memory_strategies(self.memory_id)
            
            stats = {
                "memory_id": self.memory_id,
                "memory_name": memory_info.get("name", "Unknown"),
                "status": memory_info.get("status", "Unknown"),
                "strategies": len(strategies),
                "namespaces": []
            }
            
            # Collect all namespaces
            for strategy in strategies:
                stats["namespaces"].extend(strategy.get("namespaces", []))
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get memory statistics: {e}")
            return {"error": str(e)}

    def cleanup_memory(self) -> bool:
        """Clean up memory resources"""
        
        if not self.memory_id:
            logger.warning("No memory ID to cleanup")
            return True
        
        try:
            # Note: AgentCore Memory doesn't have direct delete API
            # Memory resources are managed by AWS and will expire based on event_expiry_days
            logger.info(f"Memory {self.memory_id} will expire automatically based on retention policy")
            
            # Clear from progress tracker
            if 'setup_status' in progress_tracker.progress:
                progress_tracker.progress['setup_status'].pop('memory_id', None)
                progress_tracker.save_progress()
            
            self._memory_id = None
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup memory: {e}")
            return False