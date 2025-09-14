"""
Tests for the Webhook adapter endpoints.
"""

import pytest


def test_webhook_generic_endpoint(client):
    """Test the generic webhook endpoint."""
    response = client.post(
        "/webhook/",
        json={
            "message": "Hello from webhook test",
            "user_id": "test-user",
            "platform": "test",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert isinstance(data["message"], str) and len(data["message"]) > 0