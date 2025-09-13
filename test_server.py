"""
Automated tests for SuperAgentServer using pytest and TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from server import app


@pytest.fixture(scope="module")
def client():
    """Create a TestClient instance for the FastAPI app."""
    # The TestClient will automatically handle the app's lifespan events
    with TestClient(app) as c:
        yield c


def test_root(client: TestClient):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "SuperAgentServer"
    assert "mcp" in data["adapters"]
    assert "webhook" in data["adapters"]


def test_health_check(client: TestClient):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["agent_initialized"] is True
    assert data["adapters"] > 0


def test_agent_chat(client: TestClient):
    """Test the direct agent chat endpoint."""
    response = client.post(
        "/agent/chat", json={"message": "Hello there!", "session_id": "pytest-session"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert isinstance(data["message"], str)
    assert data["session_id"] == "pytest-session"


def test_get_manifests(client: TestClient):
    """Test the manifests endpoint."""
    response = client.get("/manifests")
    assert response.status_code == 200
    data = response.json()
    assert "mcp" in data
    assert "webhook" in data
    assert "protocolVersion" in data["mcp"]
    assert "endpoints" in data["webhook"]


def test_mcp_list_tools(client: TestClient):
    """Test the MCP tools/list endpoint."""
    response = client.post("/mcp/tools/list")
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "tools" in data["result"]
    assert len(data["result"]["tools"]) > 0
    assert data["result"]["tools"][0]["name"] == "agent_chat"


def test_mcp_call_tool(client: TestClient):
    """Test the MCP tools/call endpoint."""
    response = client.post(
        "/mcp/tools/call",
        json={
            "method": "tools/call",
            "params": {
                "name": "agent_chat",
                "arguments": {"message": "Hello from MCP test"},
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "content" in data["result"]
    assert data["result"]["content"][0]["type"] == "text"


def test_webhook_generic(client: TestClient):
    """Test the generic webhook endpoint."""
    response = client.post(
        "/webhook/webhook",
        json={
            "message": "Hello from webhook test",
            "user_id": "pytest-user",
            "platform": "pytest",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["user_id"] == "pytest-user"
    assert data["platform"] == "pytest"
