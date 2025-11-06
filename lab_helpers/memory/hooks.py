# Multi-Agent Memory Hooks

"""
Memory hooks for the multi-agent customer support system.
Provides specialized memory behavior for different agent types while enabling cross-agent context sharing.
"""

import logging
from typing import Dict, List, Any, Optional

from strands.hooks import AfterInvocationEvent, HookProvider, HookRegistry, MessageAddedEvent
from bedrock_agentcore.memory import MemoryClient

logger = logging.getLogger(__name__)


class BaseMultiAgentMemoryHook(HookProvider):
    """Base memory hook for multi-agent system with shared context capabilities"""

    def __init__(self, memory_id: str, client: MemoryClient, actor_id: str, session_id: str, agent_type: str):
        self.memory_id = memory_id
        self.client = client
        self.actor_id = actor_id
        self.session_id = session_id
        self.agent_type = agent_type
        
        # Cache memory strategies for performance
        self._namespaces = None

    @property
    def namespaces(self) -> Dict[str, List[str]]:
        """Get available memory namespaces (cached)"""
        if self._namespaces is None:
            try:
                strategies = self.client.get_memory_strategies(self.memory_id)
                self._namespaces = {
                    strategy["type"]: strategy["namespaces"]
                    for strategy in strategies
                }
            except Exception as e:
                logger.error(f"Failed to get memory strategies: {e}")
                self._namespaces = {}
        return self._namespaces

    def get_relevant_namespaces(self) -> List[str]:
        """Get namespaces relevant to this agent type"""
        relevant = []
        for strategy_type, namespaces in self.namespaces.items():
            for namespace in namespaces:
                # All agents can access customer namespaces for cross-agent context
                if "customer" in namespace:
                    relevant.append(namespace.format(actorId=self.actor_id))
        return relevant

    def retrieve_agent_context(self, event: MessageAddedEvent):
        """Retrieve context relevant to this agent from memory"""
        messages = event.agent.messages
        if (
            messages[-1]["role"] == "user"
            and "toolResult" not in messages[-1]["content"][0]
        ):
            user_query = messages[-1]["content"][0]["text"]

            try:
                all_context = []
                relevant_namespaces = self.get_relevant_namespaces()

                for namespace in relevant_namespaces:
                    memories = self.client.retrieve_memories(
                        memory_id=self.memory_id,
                        namespace=namespace,
                        query=user_query,
                        top_k=2,
                    )
                    
                    for memory in memories:
                        if isinstance(memory, dict):
                            content = memory.get("content", {})
                            if isinstance(content, dict):
                                text = content.get("text", "").strip()
                                if text:
                                    # Extract namespace type for context labeling
                                    namespace_parts = namespace.split("/")
                                    namespace_type = namespace_parts[1] if len(namespace_parts) > 1 else "general"
                                    all_context.append(f"[{namespace_type.upper()}] {text}")

                # Inject context into the query if available
                if all_context:
                    context_text = "\n".join(all_context)
                    original_text = messages[-1]["content"][0]["text"]
                    messages[-1]["content"][0]["text"] = (
                        f"Agent Context ({self.agent_type}):\n{context_text}\n\n{original_text}"
                    )
                    logger.info(f"[{self.agent_type}] Retrieved {len(all_context)} context items")

            except Exception as e:
                logger.error(f"[{self.agent_type}] Failed to retrieve context: {e}")

    def save_agent_interaction(self, event: AfterInvocationEvent):
        """Save interaction with agent-specific context"""
        try:
            messages = event.agent.messages
            if len(messages) >= 2 and messages[-1]["role"] == "assistant":
                # Extract last user query and agent response
                user_query = None
                agent_response = None

                for msg in reversed(messages):
                    if msg["role"] == "assistant" and not agent_response:
                        agent_response = msg["content"][0]["text"]
                    elif (
                        msg["role"] == "user"
                        and not user_query
                        and "toolResult" not in msg["content"][0]
                    ):
                        user_query = msg["content"][0]["text"]
                        break

                if user_query and agent_response:
                    # Add agent type context to the interaction
                    enhanced_response = f"[{self.agent_type}] {agent_response}"
                    
                    self.client.create_event(
                        memory_id=self.memory_id,
                        actor_id=self.actor_id,
                        session_id=self.session_id,
                        messages=[
                            (user_query, "USER"),
                            (enhanced_response, "ASSISTANT"),
                        ],
                    )
                    logger.info(f"[{self.agent_type}] Saved interaction to memory")

        except Exception as e:
            logger.error(f"[{self.agent_type}] Failed to save interaction: {e}")

    def register_hooks(self, registry: HookRegistry) -> None:
        """Register memory hooks for this agent"""
        registry.add_callback(MessageAddedEvent, self.retrieve_agent_context)
        registry.add_callback(AfterInvocationEvent, self.save_agent_interaction)
        logger.info(f"[{self.agent_type}] Memory hooks registered")


class OrchestratorMemoryHook(BaseMultiAgentMemoryHook):
    """Specialized memory hook for orchestrator agent with routing intelligence"""
    
    def __init__(self, memory_id: str, client: MemoryClient, actor_id: str, session_id: str):
        super().__init__(memory_id, client, actor_id, session_id, "Orchestrator")
    
    def save_routing_decision(self, user_query: str, selected_agent: str, reasoning: str):
        """Save orchestrator routing decisions for learning"""
        try:
            routing_info = f"Query: {user_query}\nRouted to: {selected_agent}\nReasoning: {reasoning}"
            
            self.client.create_event(
                memory_id=self.memory_id,
                actor_id=self.actor_id,
                session_id=self.session_id,
                messages=[
                    (f"Routing Decision: {routing_info}", "OTHER"),
                ],
            )
            logger.info(f"[Orchestrator] Saved routing decision: {selected_agent}")
        except Exception as e:
            logger.error(f"[Orchestrator] Failed to save routing decision: {e}")

    def get_routing_context(self, query: str) -> List[str]:
        """Get routing context from past decisions"""
        try:
            # Store routing decisions in customer semantic memory for now
            semantic_namespace = f"support/customer/{self.actor_id}/semantic"
            memories = self.client.retrieve_memories(
                memory_id=self.memory_id,
                namespace=semantic_namespace,
                query=f"routing decision {query}",
                top_k=2,
            )
            
            context = []
            for memory in memories:
                if isinstance(memory, dict):
                    content = memory.get("content", {})
                    if isinstance(content, dict):
                        text = content.get("text", "").strip()
                        if "routing decision" in text.lower():
                            context.append(text)
            
            return context
        except Exception as e:
            logger.error(f"[Orchestrator] Failed to get routing context: {e}")
            return []


class CustomerSupportMemoryHook(BaseMultiAgentMemoryHook):
    """Specialized memory hook for customer support agent with preference learning"""
    
    def __init__(self, memory_id: str, client: MemoryClient, actor_id: str, session_id: str):
        super().__init__(memory_id, client, actor_id, session_id, "CustomerSupport")

    def get_customer_preferences(self, query: str) -> List[str]:
        """Get customer preferences relevant to the query"""
        try:
            preferences_namespace = f"support/customer/{self.actor_id}/preferences"
            memories = self.client.retrieve_memories(
                memory_id=self.memory_id,
                namespace=preferences_namespace,
                query=query,
                top_k=3,
            )
            
            preferences = []
            for memory in memories:
                if isinstance(memory, dict):
                    content = memory.get("content", {})
                    if isinstance(content, dict):
                        text = content.get("text", "").strip()
                        if text:
                            preferences.append(text)
            
            return preferences
        except Exception as e:
            logger.error(f"[CustomerSupport] Failed to get customer preferences: {e}")
            return []


class KnowledgeBaseMemoryHook(BaseMultiAgentMemoryHook):
    """Specialized memory hook for knowledge base agent with technical solution persistence"""
    
    def __init__(self, memory_id: str, client: MemoryClient, actor_id: str, session_id: str):
        super().__init__(memory_id, client, actor_id, session_id, "KnowledgeBase")
    
    def save_technical_solution(self, problem: str, solution: str, success: bool):
        """Save technical solutions for future reference"""
        try:
            solution_info = f"Problem: {problem}\nSolution: {solution}\nSuccess: {success}"
            
            self.client.create_event(
                memory_id=self.memory_id,
                actor_id=self.actor_id,
                session_id=self.session_id,
                messages=[
                    (f"Technical Solution: {solution_info}", "OTHER"),
                ],
            )
            logger.info(f"[KnowledgeBase] Saved technical solution (success: {success})")
        except Exception as e:
            logger.error(f"[KnowledgeBase] Failed to save technical solution: {e}")

    def get_technical_history(self, query: str) -> List[str]:
        """Get relevant technical solutions from history"""
        try:
            # Store technical solutions in customer semantic memory for now
            semantic_namespace = f"support/customer/{self.actor_id}/semantic"
            memories = self.client.retrieve_memories(
                memory_id=self.memory_id,
                namespace=semantic_namespace,
                query=f"technical solution {query}",
                top_k=2,
            )
            
            solutions = []
            for memory in memories:
                if isinstance(memory, dict):
                    content = memory.get("content", {})
                    if isinstance(content, dict):
                        text = content.get("text", "").strip()
                        if "technical solution" in text.lower():
                            solutions.append(text)
            
            return solutions
        except Exception as e:
            logger.error(f"[KnowledgeBase] Failed to get technical history: {e}")
            return []