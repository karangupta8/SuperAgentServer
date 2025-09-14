"""
Base adapter system for exposing agents across different protocols.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel

from ..agent.base_agent import AgentRequest, AgentResponse, BaseAgent


class AdapterConfig(BaseModel):
    """Configuration for an adapter."""
    name: str
    prefix: str
    enabled: bool = True
    config: Dict[str, Any] = {}


class BaseAdapter(ABC):
    """
    Abstract base class for all protocol adapters.
    
    Each adapter is responsible for:
    1. Mapping inputs/outputs to its protocol format
    2. Registering itself with the FastAPI app
    3. Serving a manifest/schema if required
    """
    
    def __init__(self, agent: BaseAgent, config: AdapterConfig):
        self.agent = agent
        self.config = config
        self.router = APIRouter(prefix=f"/{config.prefix}")
        self._setup_routes()
    
    @abstractmethod
    def _setup_routes(self) -> None:
        """Set up the FastAPI routes for this adapter."""
        pass
    
    @abstractmethod
    async def _process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request in the adapter's protocol format.
        
        Args:
            request_data: Raw request data in the adapter's format
            
        Returns:
            Response data in the adapter's format
        """
        pass
    
    @abstractmethod
    def get_manifest(self) -> Dict[str, Any]:
        """
        Get the adapter's manifest/schema.
        
        Returns:
            Manifest data for this adapter
        """
        pass
    
    def register_with_app(self, app: FastAPI) -> None:
        """Register this adapter's routes with the FastAPI app."""
        app.include_router(self.router)
    
    async def _convert_to_agent_request(self, request_data: Dict[str, Any]) -> AgentRequest:
        """Convert adapter-specific request to AgentRequest."""
        # Default implementation - can be overridden by subclasses
        return AgentRequest(
            message=request_data.get("message", ""),
            session_id=request_data.get("session_id"),
            metadata=request_data.get("metadata", {}),
            tools=request_data.get("tools")
        )
    
    async def _convert_from_agent_response(self, response: AgentResponse) -> Dict[str, Any]:
        """Convert AgentResponse to adapter-specific format."""
        # Default implementation - can be overridden by subclasses
        return {
            "message": response.message,
            "session_id": response.session_id,
            "metadata": response.metadata,
            "tools_used": response.tools_used,
            "timestamp": response.timestamp.isoformat()
        }


class AdapterRegistry:
    """Registry for managing all protocol adapters."""
    
    def __init__(self):
        self._adapters: Dict[str, BaseAdapter] = {}
        self._adapter_types: Dict[str, Type[BaseAdapter]] = {}
    
    def register_adapter_type(self, name: str, adapter_class: Type[BaseAdapter]) -> None:
        """Register an adapter type."""
        self._adapter_types[name] = adapter_class
    
    def create_adapter(self, name: str, agent: BaseAgent, config: AdapterConfig) -> BaseAdapter:
        """Create and register an adapter instance."""
        if name not in self._adapter_types:
            raise ValueError(f"Unknown adapter type: {name}")
        
        adapter = self._adapter_types[name](agent, config)
        self._adapters[config.name] = adapter
        return adapter
    
    def get_adapter(self, name: str) -> Optional[BaseAdapter]:
        """Get an adapter by name."""
        return self._adapters.get(name)
    
    def get_all_adapters(self) -> Dict[str, BaseAdapter]:
        """Get all registered adapters."""
        return self._adapters.copy()
    
    def register_all_with_app(self, app: FastAPI) -> None:
        """Register all adapters with the FastAPI app."""
        for adapter in self._adapters.values():
            adapter.register_with_app(app)
    
    def get_manifests(self) -> Dict[str, Dict[str, Any]]:
        """Get manifests for all adapters."""
        return {
            name: adapter.get_manifest()
            for name, adapter in self._adapters.items()
        }
