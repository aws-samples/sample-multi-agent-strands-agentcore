# Memory Components for Multi-Agent System

"""
Memory integration components for the multi-agent customer support system.
Provides AgentCore Memory capabilities across orchestrator and specialized agents.
"""

from .hooks import (
    BaseMultiAgentMemoryHook,
    OrchestratorMemoryHook,
    CustomerSupportMemoryHook,
    KnowledgeBaseMemoryHook
)

from .client import MultiAgentMemoryClient
from .utils import MemoryNamespaceManager, MemorySeeder

__all__ = [
    'BaseMultiAgentMemoryHook',
    'OrchestratorMemoryHook', 
    'CustomerSupportMemoryHook',
    'KnowledgeBaseMemoryHook',
    'MultiAgentMemoryClient',
    'MemoryNamespaceManager',
    'MemorySeeder'
]