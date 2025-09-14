"""
Adapter system for exposing agents across different protocols.
"""

from .base_adapter import AdapterConfig, BaseAdapter, AdapterRegistry
from . import mcp_adapter
from . import webhook_adapter
from . import a2a_adapter
from . import acp_adapter


__all__ = [
    "AdapterConfig", "BaseAdapter", "AdapterRegistry",
    "mcp_adapter", "webhook_adapter", "a2a_adapter", "acp_adapter"
]
