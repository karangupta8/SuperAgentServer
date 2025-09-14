"""
Automated tests for SuperAgentServer using pytest and TestClient.
"""
import asyncio
import os
import pytest, time
from fastapi.testclient import TestClient
from src.super_agent_server.server import app

def test_root(client: TestClient):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "SuperAgentServer"


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


@pytest.mark.requires_agent
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


@pytest.mark.requires_agent
def test_agent_schema_endpoint(client: TestClient):
    """Test the agent schema endpoint."""
    response = client.get("/agent/schema")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "description" in data


@pytest.mark.requires_agent
def test_mcp_list_tools(client: TestClient):
    """Test the MCP tools/list endpoint."""
    response = client.post("/mcp/tools/list")
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "tools" in data["result"]
    assert len(data["result"]["tools"]) > 0
    assert data["result"]["tools"][0]["name"] == "chat"


@pytest.mark.requires_agent
def test_mcp_call_tool(client: TestClient):
    """Test the MCP tools/call endpoint."""
    response = client.post(
        "/mcp/tools/call",
        json={
            "method": "tools/call",
            "params": {
                "name": "chat",
                "arguments": {"message": "Hello from MCP test"},
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "content" in data["result"]
    assert data["result"]["content"][0]["type"] == "text"


@pytest.mark.requires_agent
def test_webhook_generic(client: TestClient):
    """Test the generic webhook endpoint."""
    response = client.post(
        "/webhook",
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


def test_agent_chat_uninitialized(uninitialized_client: TestClient):
    """Test that agent chat returns 503 when agent is not initialized."""
    response = uninitialized_client.post(
        "/agent/chat", json={"message": "Hello there!", "session_id": "pytest-session"}
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "Agent not initialized. Check server logs for details."


@pytest.mark.requires_agent
@pytest.mark.asyncio
async def test_websocket_chat_stream(client: TestClient):
    """Test the WebSocket streaming endpoint for a successful stream."""
    try:
        with client.websocket_connect("/chat/stream") as websocket:
            # Send a message in LangServe format
            input_data = {"input": {"input": "Hello, stream!", "chat_history": []}}
            websocket.send_json([input_data])

            # Receive and validate events
            start_event_received = False
            stream_content = ""
            end_event_received = False

            # Use an explicit timeout to prevent tests from hanging
            start_time = time.time()
            timeout = 20  # seconds

            while time.time() - start_time < timeout:
                data = websocket.receive_json(timeout=1)
                event_type = data.get("event")

                if event_type == "on_chat_model_start":
                    start_event_received = True
                elif event_type == "on_chat_model_stream":
                    chunk = data.get("data", {}).get("chunk", {})
                    if chunk and "content" in chunk:
                        stream_content += chunk["content"]
                elif event_type == "on_chat_model_end":
                    end_event_received = True
                    break  # Exit loop once the stream ends

            if not end_event_received:
                pytest.fail(f"WebSocket test timed out after {timeout} seconds.")

            assert start_event_received, "Did not receive the 'on_chat_model_start' event"
            assert len(stream_content) > 0, "Streamed content was empty"
            assert end_event_received, "Did not receive the 'on_chat_model_end' event"
    except Exception as e:
        pytest.fail(f"WebSocket test failed with an exception: {e}")


@pytest.mark.asyncio
async def test_websocket_uninitialized_agent(uninitialized_client: TestClient):
    """Test WebSocket connection fails gracefully when agent is not initialized."""
    with uninitialized_client.websocket_connect("/chat/stream") as websocket:
        response = websocket.receive_json()
        assert response["event"] == "error"
        assert "Agent not initialized" in response["data"]["error"]
