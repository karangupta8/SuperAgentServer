# src/super_agent_server/__init__.py
"""
SuperAgentServer - Universal Agent Adapter Layer for LangChain agents
"""

from .adapters import AdapterConfig, AdapterRegistry
from .agent import AgentRequest, AgentResponse, BaseAgent, ExampleAgent
from .server import app, create_app

__version__ = "0.1.0"
__all__ = [
    "BaseAgent", 
    "AgentResponse", 
    "AgentRequest", 
    "ExampleAgent",
    "AdapterRegistry",
    "AdapterConfig", 
    "create_app",
    "app"
]