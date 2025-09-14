"""
Base agent abstraction that all LangChain agents should inherit from.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field
import asyncio
from datetime import datetime


class AgentRequest(BaseModel):
    """Standard request format for all agents."""
    message: str = Field(..., description="The input message to the agent")
    session_id: Optional[str] = Field(None, description="Session identifier for conversation continuity")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    tools: Optional[List[str]] = Field(None, description="Available tools for the agent to use")


class AgentResponse(BaseModel):
    """Standard response format for all agents."""
    message: str = Field(..., description="The agent's response message")
    session_id: Optional[str] = Field(None, description="Session identifier")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional response metadata")
    tools_used: Optional[List[str]] = Field(None, description="Tools used in generating the response")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the SuperAgentServer.
    
    This provides a standardized interface that all adapters can use,
    regardless of the underlying LangChain implementation.
    """
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent. Called once before first use."""
        pass
    
    @abstractmethod
    async def process(self, request: AgentRequest) -> AgentResponse:
        """
        Process a request and return a response.
        
        Args:
            request: The agent request
            
        Returns:
            AgentResponse: The agent's response
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the agent's schema for auto-generation of adapter manifests.
        
        Returns:
            Dict containing the agent's input/output schema
        """
        pass
    
    async def ensure_initialized(self) -> None:
        """Ensure the agent is initialized before processing."""
        if not self._initialized:
            await self.initialize()
            self._initialized = True
    
    async def __call__(self, request: AgentRequest) -> AgentResponse:
        """Make the agent callable."""
        await self.ensure_initialized()
        return await self.process(request)
