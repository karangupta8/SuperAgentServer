# tests/test_adapters/__init__.py
"""
Adapter-specific tests.
"""

# tests/test_adapters/test_webhook_adapter.py
"""
Tests for Webhook adapter.
"""

import pytest
from unittest.mock import Mock
from src.super_agent_server.adapters.webhook_adapter import WebhookAdapter


class TestWebhookAdapter:
    """Test cases for Webhook adapter."""
    
    def test_webhook_adapter_initialization(self):
        """Test Webhook adapter initializes correctly."""
        adapter = WebhookAdapter(Mock(), Mock())
        assert adapter is not None
    
    def test_webhook_generic_endpoint(self, client):
        """Test generic webhook endpoint."""
        response = client.post(
            "/webhook/webhook",
            json={
                "message": "Hello from webhook test",
                "user_id": "test-user",
                "platform": "test"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data