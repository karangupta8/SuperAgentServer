"""
Adapter-specific tests.
"""

import pytest
from unittest.mock import Mock, patch
from src.super_agent_server.adapters.mcp_adapter import MCPAdapter
from src.super_agent_server.agent.base_agent import AgentRequest, AgentResponse


class TestMCPAdapter:
    """Test cases for MCP adapter."""
    
    def test_mcp_adapter_initialization(self):
        """Test MCP adapter initializes correctly."""
        adapter = MCPAdapter(Mock(), Mock())
        assert adapter is not None
    
    def test_mcp_tools_list(self, client):
        """Test MCP tools list endpoint."""
        response = client.post("/mcp/tools/list")
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "tools" in data["result"]
    
    def test_mcp_tool_call(self, client, sample_agent_request):
        """Test MCP tool call endpoint."""
        response = client.post(
            "/mcp/tools/call",
            json={
                "method": "tools/call",
                "params": {
                    "name": "agent_chat",
                    "arguments": sample_agent_request
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data

