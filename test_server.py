"""
Automated tests for SuperAgentServer using pytest and TestClient.
"""
import os
import pytest
from fastapi.testclient import TestClient
from server import app

# Condition to skip tests that require an initialized agent
AGENT_NOT_INITIALIZED = os.getenv("OPENAI_API_KEY") is None


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
    # The agent's initialization depends on the OPENAI_API_KEY env var.
    # The test should respect this state to be reliable in any environment.
    agent_should_be_initialized = os.getenv("OPENAI_API_KEY") is not None

    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["agent_initialized"] is agent_should_be_initialized
    if agent_should_be_initialized:
        assert data["adapters"] > 0
    else:
        assert data["adapters"] == 0


@pytest.mark.skipif(AGENT_NOT_INITIALIZED, reason="OPENAI_API_KEY not set, agent not initialized")
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


@pytest.mark.skipif(AGENT_NOT_INITIALIZED, reason="OPENAI_API_KEY not set, agent not initialized")
def test_mcp_list_tools(client: TestClient):
    """Test the MCP tools/list endpoint."""
    response = client.post("/mcp/tools/list")
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "tools" in data["result"]
    assert len(data["result"]["tools"]) > 0
    assert data["result"]["tools"][0]["name"] == "agent_chat"


@pytest.mark.skipif(AGENT_NOT_INITIALIZED, reason="OPENAI_API_KEY not set, agent not initialized")
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


@pytest.mark.skipif(AGENT_NOT_INITIALIZED, reason="OPENAI_API_KEY not set, agent not initialized")
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


@pytest.mark.skipif(AGENT_NOT_INITIALIZED, reason="OPENAI_API_KEY not set, agent not initialized")
def test_websocket_chat_stream(client: TestClient):
    """Test the WebSocket streaming endpoint for a successful stream."""
    try:
        with client.websocket_connect("/chat/stream") as websocket:
            # Send a message in LangServe format
            input_data = {
                "input": {"input": "Hello, stream!", "chat_history": []}
            }
            websocket.send_json([input_data])

            # Receive and validate events
            start_event_received = False
            stream_content = ""
            end_event_received = False

            # The test client's receive_json has a default timeout
            while True:
                data = websocket.receive_json()
                event_type = data.get("event")

                if event_type == "on_chat_model_start":
                    start_event_received = True
                elif event_type == "on_chat_model_stream":
                    stream_content += data.get("data", {}).get("chunk", {}).get("content", "")
                elif event_type == "on_chat_model_end":
                    end_event_received = True
                    break  # End of stream

            assert start_event_received, "Did not receive the 'on_chat_model_start' event"
            assert len(stream_content) > 0, "Streamed content was empty"
            assert end_event_received, "Did not receive the 'on_chat_model_end' event"
    except Exception as e:
        pytest.fail(f"WebSocket test failed with an exception: {e}")
