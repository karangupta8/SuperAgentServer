"""
Adapter system for exposing agents across different protocols.
"""

from .base_adapter import BaseAdapter, AdapterRegistry
from .mcp_adapter import MCPAdapter
from .webhook_adapter import WebhookAdapter
from .a2a_adapter import A2AAdapter
from .acp_adapter import ACPAdapter

__all__ = ["BaseAdapter", "AdapterRegistry", "MCPAdapter", "WebhookAdapter", "A2AAdapter", "ACPAdapter"]
