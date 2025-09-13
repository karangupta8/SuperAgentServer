"""
Adapter system for exposing agents across different protocols.
"""

from .base_adapter import BaseAdapter, AdapterRegistry
from .mcp_adapter import MCPAdapter
from .webhook_adapter import WebhookAdapter

__all__ = ["BaseAdapter", "AdapterRegistry", "MCPAdapter", "WebhookAdapter"]
