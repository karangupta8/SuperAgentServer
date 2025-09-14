"""
Adapter system for exposing agents across different protocols.
"""

from . import a2a_adapter, acp_adapter, mcp_adapter, webhook_adapter
from .base_adapter import AdapterConfig, AdapterRegistry, BaseAdapter

__all__ = [
    "AdapterConfig", "BaseAdapter", "AdapterRegistry",
    "mcp_adapter", "webhook_adapter", "a2a_adapter", "acp_adapter"
]
