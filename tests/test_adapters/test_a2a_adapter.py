"""
Tests for the A2A adapter endpoints.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.requires_agent
def test_a2a_message_endpoint(client: TestClient):
    """Test the A2A message endpoint for successful communication."""
    response = client.post(
        "/a2a/message",
        json={
            "sender_agent_id": "test-sender-agent",
            "message": "Hello from another agent!",
            "session_id": "a2a-session-123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert isinstance(data["message"], str)
    assert data["session_id"] == "a2a-session-123"
    assert "metadata" in data
    assert data["metadata"]["source_protocol"] == "a2a"


def test_a2a_message_uninitialized(uninitialized_client: TestClient):
    """Test A2A message endpoint when agent is not initialized."""
    response = uninitialized_client.post(
        "/a2a/message",
        json={
            "sender_agent_id": "test-sender-agent",
            "message": "Hello from another agent!",
            "session_id": "a2a-session-123",
        },
    )
    assert response.status_code == 503
    assert (
        response.json()["detail"] ==
        "Agent not initialized. Check server logs for details."
    )


@pytest.mark.requires_agent
def test_a2a_message_invalid_payload(client: TestClient):
    """Test A2A message endpoint with invalid payload."""
    response = client.post(
        "/a2a/message",
        json={
            "sender_agent_id": "test-sender-agent",
            # Missing required 'message' field
            "session_id": "a2a-session-123",
        },
    )
    assert response.status_code == 422


@pytest.mark.requires_agent
def test_a2a_message_empty_message(client: TestClient):
    """Test A2A message endpoint with empty message."""
    response = client.post(
        "/a2a/message",
        json={
            "sender_agent_id": "test-sender-agent",
            "message": "",
            "session_id": "a2a-session-123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert isinstance(data["message"], str)


@pytest.mark.requires_agent
def test_a2a_message_without_session_id(client: TestClient):
    """Test A2A message endpoint without session ID."""
    response = client.post(
        "/a2a/message",
        json={
            "sender_agent_id": "test-sender-agent",
            "message": "Hello from another agent!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert isinstance(data["message"], str)
    assert data["session_id"] is None
