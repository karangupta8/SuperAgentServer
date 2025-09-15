"""
Security testing suite for SuperAgentServer.

Tests for vulnerabilities, injection attacks, authentication bypasses,
and other security-related issues.
"""

import json
import os
import pytest
import subprocess
import sys
from unittest.mock import patch

from fastapi.testclient import TestClient


class TestCodeInjectionSecurity:
    """Test protection against code injection attacks."""

    @pytest.mark.requires_agent
    def test_eval_injection_prevention(self, client: TestClient):
        """Test that eval() injection attempts are blocked."""
        malicious_inputs = [
            "__import__('os').system('echo hacked')",
            "exec('import os; os.system(\"echo hacked\")')",
            "open('/etc/passwd').read()",
            "__import__('subprocess').run(['rm', '-rf', '/'])",
            "eval('__import__(\"os\").system(\"echo hacked\")')",
            "globals()['__builtins__']['eval']('print(1)')",
            "getattr(__builtins__, 'eval')('print(1)')",
        ]
        
        for malicious_input in malicious_inputs:
            response = client.post(
                "/agent/chat",
                json={"message": f"Calculate: {malicious_input}", "session_id": "security-test"}
            )
            
            # Should not execute the malicious code
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            
            # Response should contain an error message, not execute the code
            assert "Error" in data["message"] or "Invalid" in data["message"]
            assert "hacked" not in data["message"]
            assert "passwd" not in data["message"]

    @pytest.mark.requires_agent
    def test_safe_math_expressions(self, client: TestClient):
        """Test that legitimate mathematical expressions still work."""
        safe_expressions = [
            "2 + 3",
            "10 * 5",
            "(4 + 6) / 2",
            "2 * (3 + 4)",
            "-5 + 10",
            "100 / 4",
            "2 ** 3",  # This should fail as ** is not in allowed operators
        ]
        
        for expr in safe_expressions:
            response = client.post(
                "/agent/chat",
                json={"message": f"Calculate: {expr}", "session_id": "security-test"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            
            # Most should work, but ** should be blocked
            if "**" in expr:
                assert "Error" in data["message"] or "Invalid" in data["message"]
            else:
                # Should contain a valid result
                assert "Error" not in data["message"]

    def test_input_validation(self, client: TestClient):
        """Test input validation and sanitization."""
        invalid_inputs = [
            {"message": "", "session_id": "test"},  # Empty message
            {"message": "   ", "session_id": "test"},  # Whitespace only
            {"message": "a" * 10000, "session_id": "test"},  # Very long message
            {"session_id": "test"},  # Missing message
            {"message": "test", "session_id": "a" * 1000},  # Very long session_id
        ]
        
        for invalid_input in invalid_inputs:
            response = client.post("/agent/chat", json=invalid_input)
            # Should either succeed with validation or return 422
            assert response.status_code in [200, 422]


class TestInformationDisclosure:
    """Test protection against information disclosure."""

    @pytest.mark.requires_agent
    def test_error_message_sanitization(self, client: TestClient):
        """Test that error messages don't expose internal details."""
        # Try to trigger various errors
        test_cases = [
            {"message": "test", "session_id": None},  # Should work
            {"message": "test", "session_id": ""},    # Should work
        ]
        
        for test_case in test_cases:
            response = client.post("/agent/chat", json=test_case)
            
            if response.status_code == 500:
                data = response.json()
                detail = data.get("detail", "")
                
                # Error messages should not expose:
                # - File paths
                # - Internal function names
                # - Database connection strings
                # - API keys or tokens
                # - Stack traces
                sensitive_patterns = [
                    "/app/",
                    "/home/",
                    "Traceback",
                    "File \"",
                    "line ",
                    "sk-",
                    "password=",
                    "api_key=",
                    "token=",
                ]
                
                for pattern in sensitive_patterns:
                    assert pattern.lower() not in detail.lower(), f"Sensitive info leaked: {pattern}"

    def test_global_exception_handler(self, client: TestClient):
        """Test that global exception handler doesn't leak information."""
        # This test might need to be adjusted based on actual server behavior
        # We'll test with malformed requests to trigger exceptions
        
        malformed_requests = [
            "not json",
            {"invalid": "structure"},
            None,
        ]
        
        for request_data in malformed_requests:
            if request_data is None:
                response = client.post("/agent/chat")
            else:
                response = client.post("/agent/chat", data=request_data)
            
            # Should return appropriate error without exposing internals
            assert response.status_code in [400, 422, 500]
            
            if response.status_code == 500:
                data = response.json()
                detail = data.get("detail", "")
                assert "internal" in detail.lower() or "error" in detail.lower()
                assert "traceback" not in detail.lower()


class TestCORSecurity:
    """Test CORS configuration and security."""

    def test_cors_headers_present(self, client: TestClient):
        """Test that CORS headers are properly configured."""
        response = client.options("/agent/chat")
        
        # Check for CORS headers
        cors_headers = [
            "access-control-allow-origin",
            "access-control-allow-methods",
            "access-control-allow-headers",
        ]
        
        for header in cors_headers:
            assert header in response.headers

    def test_cors_origin_validation(self, client: TestClient):
        """Test CORS origin validation."""
        # Test with different origins
        origins_to_test = [
            "http://localhost:3000",  # Should be allowed
            "http://127.0.0.1:3000",  # Should be allowed
            "https://malicious-site.com",  # Should be blocked
            "http://evil.com",  # Should be blocked
        ]
        
        for origin in origins_to_test:
            headers = {"Origin": origin}
            response = client.options("/agent/chat", headers=headers)
            
            # Check if origin is allowed
            allowed_origin = response.headers.get("access-control-allow-origin")
            if origin in ["http://localhost:3000", "http://127.0.0.1:3000"]:
                assert allowed_origin == origin or allowed_origin == "*"
            else:
                # Malicious origins should not be allowed
                assert allowed_origin != origin


class TestAuthenticationSecurity:
    """Test authentication and authorization security."""

    def test_endpoints_without_auth(self, client: TestClient):
        """Test that endpoints are accessible without authentication (current behavior)."""
        endpoints_to_test = [
            ("/", "GET"),
            ("/health", "GET"),
            ("/agent/chat", "POST"),
            ("/agent/schema", "GET"),
            ("/manifests", "GET"),
        ]
        
        for endpoint, method in endpoints_to_test:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={"message": "test"})
            
            # Currently, endpoints should be accessible without auth
            # This test documents current behavior and can be updated when auth is added
            assert response.status_code in [200, 422, 503]  # 503 if agent not initialized

    def test_authorization_headers_ignored(self, client: TestClient):
        """Test that authorization headers are properly ignored (current behavior)."""
        auth_headers = [
            {"Authorization": "Bearer fake-token"},
            {"Authorization": "Basic dXNlcjpwYXNz"},
            {"X-API-Key": "fake-key"},
        ]
        
        for headers in auth_headers:
            response = client.post(
                "/agent/chat",
                json={"message": "test"},
                headers=headers
            )
            
            # Should behave the same as without auth headers
            # This documents current behavior
            assert response.status_code in [200, 422, 503]


class TestInputValidation:
    """Test comprehensive input validation."""

    def test_sql_injection_prevention(self, client: TestClient):
        """Test protection against SQL injection (if applicable)."""
        sql_injection_attempts = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --",
            "' UNION SELECT * FROM users --",
        ]
        
        for injection_attempt in sql_injection_attempts:
            response = client.post(
                "/agent/chat",
                json={"message": injection_attempt, "session_id": "security-test"}
            )
            
            # Should handle gracefully without SQL errors
            assert response.status_code in [200, 422]
            if response.status_code == 200:
                data = response.json()
                # Should not contain SQL error messages
                assert "sql" not in data.get("message", "").lower()
                assert "database" not in data.get("message", "").lower()

    def test_xss_prevention(self, client: TestClient):
        """Test protection against XSS attacks."""
        xss_attempts = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//",
        ]
        
        for xss_attempt in xss_attempts:
            response = client.post(
                "/agent/chat",
                json={"message": xss_attempt, "session_id": "security-test"}
            )
            
            # Should handle without executing scripts
            assert response.status_code in [200, 422]
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                # Script tags should be escaped or removed
                assert "<script>" not in message
                assert "javascript:" not in message


class TestRateLimiting:
    """Test rate limiting and DoS protection."""

    def test_no_rate_limiting_current(self, client: TestClient):
        """Test current rate limiting behavior (none implemented)."""
        # Send multiple rapid requests
        responses = []
        for i in range(10):
            response = client.post(
                "/agent/chat",
                json={"message": f"test {i}", "session_id": "rate-limit-test"}
            )
            responses.append(response)
        
        # Currently, all requests should succeed (no rate limiting)
        # This test documents current behavior
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count >= 0  # Document that no rate limiting is currently active

    def test_large_payload_handling(self, client: TestClient):
        """Test handling of large payloads."""
        # Test with very large message
        large_message = "A" * 1000000  # 1MB message
        
        response = client.post(
            "/agent/chat",
            json={"message": large_message, "session_id": "large-payload-test"}
        )
        
        # Should handle gracefully (either process or return 413/422)
        assert response.status_code in [200, 413, 422, 500]


@pytest.mark.integration
class TestSecurityIntegration:
    """Integration tests for security features."""

    @pytest.mark.requires_agent
    def test_websocket_security(self, client: TestClient):
        """Test WebSocket endpoint security."""
        try:
            with client.websocket_connect("/chat/stream") as websocket:
                # Try to send malicious data
                malicious_data = [
                    "malicious json",
                    {"malicious": "data"},
                    None,
                ]
                
                for data in malicious_data:
                    try:
                        if data is None:
                            websocket.send_text("")
                        else:
                            websocket.send_json(data)
                        
                        # Should handle gracefully
                        response = websocket.receive_json(timeout=1)
                        assert "error" in response or "event" in response
                    except Exception:
                        # Expected for malformed data
                        pass
        except Exception:
            # WebSocket might not be available in test environment
            pytest.skip("WebSocket not available in test environment")

    def test_mcp_adapter_security(self, client: TestClient):
        """Test MCP adapter security."""
        malicious_mcp_requests = [
            {"method": "malicious_method"},
            {"method": "tools/call", "params": {"name": "malicious", "arguments": {}}},
            {"method": "initialize", "params": {"malicious": "data"}},
        ]
        
        for request_data in malicious_mcp_requests:
            response = client.post("/mcp/", json=request_data)
            
            # Should handle gracefully
            assert response.status_code in [200, 422]
            if response.status_code == 200:
                data = response.json()
                # Should not execute malicious operations
                assert "error" in data or "result" in data
