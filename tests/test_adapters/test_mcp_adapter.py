"""
Adapter-specific tests for MCP.
"""

import pytest


@pytest.mark.requires_agent
def test_mcp_tools_list(client):
    """Test MCP tools list endpoint."""
    response = client.post("/mcp/", json={"method": "tools/list"})
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "tools" in data["result"]
    assert len(data["result"]["tools"]) > 0
    # The first tool is get_current_time, not chat
    assert data["result"]["tools"][0]["name"] == "get_current_time"


@pytest.mark.requires_agent
def test_mcp_tool_call(client):
    """Test MCP tool call endpoint."""
    response = client.post(
        "/mcp/",
        json={
            "method": "tools/call",
            "params": {
                "name": "chat",
                "arguments": {
                    "message": "Hello from MCP test",
                    "session_id": "mcp-test-session-123"
                },
            }
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "content" in data["result"]
    assert len(data["result"]["content"]) > 0
    assert data["result"]["content"][0]["type"] == "text"
    assert isinstance(data["result"]["content"][0]["text"], str)
