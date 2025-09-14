"""
Tests for the A2A adapter endpoints.
"""
import os
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
    """Test that A2A endpoint returns 503 when agent is not initialized."""
    response = uninitialized_client.post(
        "/a2a/message",
        json={
            "sender_agent_id": "test-sender-agent",
            "message": "Hello from another agent!",
            "session_id": "a2a-session-uninitialized",
        },
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "Agent not initialized. Check server logs for details."


@pytest.mark.requires_agent
def test_a2a_message_validation_error(client: TestClient):
    """Test the A2A message endpoint for validation errors."""
    # Test with missing 'message' field
    response = client.post(
        "/a2a/message",
        json={"sender_agent_id": "test-sender-agent", "session_id": "a2a-session-validation-error"},
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any("message" in error.get("loc", []) and error.get("type") == "missing" for error in data["detail"])

    # Test with missing 'sender_agent_id' field
    response = client.post(
        "/a2a/message",
        json={"message": "A message without a sender", "session_id": "a2a-session-validation-error-2"},
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any("sender_agent_id" in error.get("loc", []) and error.get("type") == "missing" for error in data["detail"])
