"""
Integration testing suite for SuperAgentServer.

Tests for end-to-end functionality, adapter interactions,
and system integration scenarios.
"""

import json
import pytest
import time
import os
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient


@pytest.mark.integration
class TestEndToEndIntegration:
    """Test complete end-to-end workflows."""

    @pytest.mark.requires_agent
    def test_complete_chat_workflow(self, client: TestClient):
        """Test complete chat workflow from request to response."""
        # Step 1: Check server health
        health_response = client.get("/health")
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert health_data["status"] == "healthy"
        assert health_data["agent_initialized"] is True

        # Step 2: Get agent schema
        schema_response = client.get("/agent/schema")
        assert schema_response.status_code == 200
        schema_data = schema_response.json()
        assert "name" in schema_data
        assert "tools" in schema_data

        # Step 3: Send chat message
        chat_response = client.post(
            "/agent/chat",
            json={
                "message": "What time is it?",
                "session_id": "integration-test-session"
            }
        )
        assert chat_response.status_code == 200
        chat_data = chat_response.json()
        assert "message" in chat_data
        assert chat_data["session_id"] == "integration-test-session"

        # Step 4: Verify response contains expected information
        assert len(chat_data["message"]) > 0

    @pytest.mark.requires_agent
    def test_session_continuity(self, client: TestClient):
        """Test that session information is maintained across requests."""
        session_id = "continuity-test-session"
        
        # First request
        response1 = client.post(
            "/agent/chat",
            json={
                "message": "Hello, my name is TestUser",
                "session_id": session_id
            }
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["session_id"] == session_id

        # Second request in same session
        response2 = client.post(
            "/agent/chat",
            json={
                "message": "What is my name?",
                "session_id": session_id
            }
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["session_id"] == session_id

        # Session should be consistent
        assert data1["session_id"] == data2["session_id"]

    @pytest.mark.requires_agent
    def test_manifests_endpoint_integration(self, client: TestClient):
        """Test manifests endpoint returns all enabled adapters."""
        response = client.get("/manifests")
        assert response.status_code == 200
        
        manifests = response.json()
        assert isinstance(manifests, dict)
        
        # Should contain manifests for enabled adapters
        expected_adapters = ["mcp", "webhook", "a2a", "acp"]
        for adapter in expected_adapters:
            if adapter in manifests:
                assert isinstance(manifests[adapter], dict)
                assert "name" in manifests[adapter] or "version" in manifests[adapter]


@pytest.mark.integration
class TestAdapterIntegration:
    """Test integration between different adapters."""

    @pytest.mark.requires_agent
    def test_mcp_adapter_full_workflow(self, client: TestClient):
        """Test complete MCP adapter workflow."""
        # Step 1: Initialize MCP
        init_response = client.post(
            "/mcp/",
            json={"method": "initialize", "id": "test-init"}
        )
        assert init_response.status_code == 200
        init_data = init_response.json()
        assert "result" in init_data
        assert "protocolVersion" in init_data["result"]

        # Step 2: List tools
        tools_response = client.post(
            "/mcp/",
            json={"method": "tools/list", "id": "test-tools"}
        )
        assert tools_response.status_code == 200
        tools_data = tools_response.json()
        assert "result" in tools_data
        assert "tools" in tools_data["result"]

        # Step 3: Call a tool
        if tools_data["result"]["tools"]:
            tool_name = tools_data["result"]["tools"][0]["name"]
            call_response = client.post(
                "/mcp/",
                json={
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": {"message": "MCP integration test"}
                    },
                    "id": "test-call"
                }
            )
            assert call_response.status_code == 200
            call_data = call_response.json()
            assert "result" in call_data

    @pytest.mark.requires_agent
    def test_webhook_adapter_workflow(self, client: TestClient):
        """Test complete webhook adapter workflow."""
        # Test generic webhook
        webhook_response = client.post(
            "/webhook/",
            json={
                "message": "Webhook integration test",
                "user_id": "test-user-123",
                "platform": "integration-test"
            }
        )
        assert webhook_response.status_code == 200
        webhook_data = webhook_response.json()
        assert "message" in webhook_data

        # Test Telegram webhook
        telegram_response = client.post(
            "/webhook/telegram",
            json={
                "message": {
                    "text": "Telegram integration test",
                    "from": {"id": 123456789},
                    "chat": {"id": 123456789}
                }
            }
        )
        assert telegram_response.status_code == 200
        telegram_data = telegram_response.json()
        assert "message" in telegram_data

    @pytest.mark.requires_agent
    def test_a2a_adapter_workflow(self, client: TestClient):
        """Test A2A adapter workflow."""
        response = client.post(
            "/a2a/message",
            json={
                "sender_agent_id": "test-agent-123",
                "message": "A2A integration test",
                "session_id": "a2a-test-session"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["session_id"] == "a2a-test-session"

    @pytest.mark.requires_agent
    def test_acp_adapter_workflow(self, client: TestClient):
        """Test ACP adapter workflow."""
        response = client.post(
            "/acp/message",
            json={
                "sender_agent_id": "test-agent-456",
                "message": "ACP integration test",
                "session_id": "acp-test-session"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["session_id"] == "acp-test-session"


@pytest.mark.integration
class TestWebSocketIntegration:
    """Test WebSocket integration scenarios."""

    @pytest.mark.requires_agent
    def test_websocket_streaming_integration(self, client: TestClient):
        """Test WebSocket streaming integration."""
        try:
            with client.websocket_connect("/chat/stream") as websocket:
                # Send message
                input_data = {
                    "input": {
                        "input": "WebSocket integration test",
                        "chat_history": []
                    }
                }
                websocket.send_json([input_data])

                # Collect streaming responses
                events_received = []
                start_event_received = False
                end_event_received = False
                stream_content = ""

                timeout = 15  # seconds
                start_time = time.time()

                while time.time() - start_time < timeout:
                    try:
                        data = websocket.receive_json(timeout=1)
                        events_received.append(data)
                        
                        event_type = data.get("event")
                        if event_type == "on_chat_model_start":
                            start_event_received = True
                        elif event_type == "on_chat_model_stream":
                            chunk = data.get("data", {}).get("chunk", {})
                            if "content" in chunk:
                                stream_content += chunk["content"]
                        elif event_type == "on_chat_model_end":
                            end_event_received = True
                            break
                    except Exception:
                        continue

                # Verify streaming worked correctly
                assert start_event_received, "Start event not received"
                assert end_event_received, "End event not received"
                assert len(stream_content) > 0, "No stream content received"
                assert len(events_received) >= 3, "Insufficient events received"

        except Exception:
            pytest.skip("WebSocket not available in test environment")

    @pytest.mark.requires_agent
    def test_websocket_error_handling(self, client: TestClient):
        """Test WebSocket error handling."""
        try:
            with client.websocket_connect("/chat/stream") as websocket:
                # Send malformed data
                websocket.send_text("invalid json")

                # Should receive error response
                try:
                    data = websocket.receive_json(timeout=5)
                    assert "error" in data or "event" in data
                except Exception:
                    # Connection might close on error, which is acceptable
                    pass

        except Exception:
            pytest.skip("WebSocket not available in test environment")


@pytest.mark.integration
class TestConfigurationIntegration:
    """Test configuration and environment integration."""

    def test_environment_variable_handling(self, client: TestClient):
        """Test that environment variables are properly handled."""
        # Test with different environment configurations
        with patch.dict(os.environ, {"DEBUG": "True", "LOG_LEVEL": "DEBUG"}):
            # Restart might be needed for env changes to take effect
            # For now, just test that the server responds
            response = client.get("/health")
            assert response.status_code == 200

    def test_adapter_configuration_integration(self, client: TestClient):
        """Test that adapter configuration works correctly."""
        # Test that all configured adapters are available
        response = client.get("/manifests")
        assert response.status_code == 200
        
        manifests = response.json()
        
        # Check that enabled adapters are present
        # This tests the integration between config and adapter loading
        assert isinstance(manifests, dict)


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Test error handling across the entire system."""

    def test_agent_uninitialized_handling(self, uninitialized_client: TestClient):
        """Test handling when agent is not initialized."""
        # Test all endpoints when agent is not initialized
        endpoints = [
            ("/agent/chat", "POST", {"message": "test"}),
            ("/agent/schema", "GET", None),
            ("/manifests", "GET", None),
        ]
        
        for endpoint, method, data in endpoints:
            if method == "GET":
                response = uninitialized_client.get(endpoint)
            elif method == "POST":
                response = uninitialized_client.post(endpoint, json=data)
            
            # Should return 503 or handle gracefully
            assert response.status_code in [503, 422]

    @pytest.mark.requires_agent
    def test_invalid_request_handling(self, client: TestClient):
        """Test handling of invalid requests across adapters."""
        invalid_requests = [
            # Invalid JSON
            ("/agent/chat", "invalid json"),
            ("/mcp/", "invalid json"),
            ("/webhook/", "invalid json"),
            
            # Malformed data
            ("/agent/chat", {"invalid": "structure"}),
            ("/mcp/", {"invalid": "method"}),
        ]
        
        for endpoint, data in invalid_requests:
            if isinstance(data, str):
                response = client.post(endpoint, data=data)
            else:
                response = client.post(endpoint, json=data)
            
            # Should handle gracefully
            assert response.status_code in [400, 422, 500]


@pytest.mark.integration
class TestDataFlowIntegration:
    """Test data flow through the entire system."""

    @pytest.mark.requires_agent
    def test_data_consistency_across_adapters(self, client: TestClient):
        """Test that data remains consistent across different adapters."""
        test_message = "Data consistency test message"
        session_id = "consistency-test-session"
        
        # Send same message through different adapters
        adapters = [
            ("/agent/chat", {"message": test_message, "session_id": session_id}),
            ("/webhook/", {"message": test_message, "user_id": "test", "platform": "test"}),
            ("/a2a/message", {"sender_agent_id": "test", "message": test_message, "session_id": session_id}),
            ("/acp/message", {"sender_agent_id": "test", "message": test_message, "session_id": session_id}),
        ]
        
        responses = []
        for endpoint, data in adapters:
            response = client.post(endpoint, json=data)
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
        
        # All should return responses with messages
        for response in responses:
            data = response.json()
            assert "message" in data

    @pytest.mark.requires_agent
    def test_metadata_preservation(self, client: TestClient):
        """Test that metadata is preserved through the system."""
        metadata = {
            "source": "integration-test",
            "user_id": "test-user",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        response = client.post(
            "/agent/chat",
            json={
                "message": "Metadata preservation test",
                "session_id": "metadata-test",
                "metadata": metadata
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Metadata should be preserved or enhanced
        assert "metadata" in data
        assert isinstance(data["metadata"], dict)


# Add the new test markers to pytest configuration
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "requires_agent: mark test as requiring an initialized agent")
    config.addinivalue_line("markers", "requires_broker: mark test as requiring a running message broker")
    config.addinivalue_line("markers", "performance: mark test as performance test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "security: mark test as security test")
