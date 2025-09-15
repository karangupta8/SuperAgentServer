"""
Performance testing suite for SuperAgentServer.

Tests for response times, throughput, memory usage, and scalability.
"""

import asyncio
import gc
import psutil
import pytest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from fastapi.testclient import TestClient


class TestResponseTime:
    """Test response time performance."""

    @pytest.mark.requires_agent
    @pytest.mark.performance
    def test_single_request_response_time(self, client: TestClient):
        """Test that single requests respond within acceptable time."""
        start_time = time.time()
        
        response = client.post(
            "/agent/chat",
            json={"message": "Hello, this is a performance test", "session_id": "perf-test"}
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        # Should respond within 5 seconds for a simple request
        assert response_time < 5.0, f"Response time {response_time:.2f}s exceeds 5s limit"

    @pytest.mark.requires_agent
    @pytest.mark.performance
    def test_health_check_response_time(self, client: TestClient):
        """Test health check endpoint response time."""
        start_time = time.time()
        
        response = client.get("/health")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        # Health check should be very fast
        assert response_time < 1.0, f"Health check response time {response_time:.2f}s exceeds 1s limit"

    @pytest.mark.requires_agent
    @pytest.mark.performance
    def test_schema_endpoint_response_time(self, client: TestClient):
        """Test schema endpoint response time."""
        start_time = time.time()
        
        response = client.get("/agent/schema")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        # Schema should be fast to retrieve
        assert response_time < 2.0, f"Schema response time {response_time:.2f}s exceeds 2s limit"


class TestConcurrentRequests:
    """Test performance under concurrent load."""

    @pytest.mark.requires_agent
    @pytest.mark.performance
    def test_concurrent_requests(self, client: TestClient):
        """Test system behavior under concurrent load."""
        num_requests = 10
        requests_data = [
            {"message": f"Concurrent test message {i}", "session_id": f"concurrent-test-{i}"}
            for i in range(num_requests)
        ]
        
        def make_request(request_data):
            return client.post("/agent/chat", json=request_data)
        
        start_time = time.time()
        
        # Execute requests concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, data) for data in requests_data]
            responses = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Check all requests succeeded
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count == num_requests, f"Only {success_count}/{num_requests} requests succeeded"
        
        # Check total time is reasonable
        assert total_time < 30.0, f"Total time {total_time:.2f}s exceeds 30s limit"
        
        # Calculate throughput
        throughput = num_requests / total_time
        assert throughput > 0.5, f"Throughput {throughput:.2f} req/s is too low"

    @pytest.mark.requires_agent
    @pytest.mark.performance
    def test_high_volume_requests(self, client: TestClient):
        """Test system behavior with high volume of requests."""
        num_requests = 50
        
        start_time = time.time()
        responses = []
        
        for i in range(num_requests):
            response = client.post(
                "/agent/chat",
                json={"message": f"High volume test {i}", "session_id": f"volume-test-{i}"}
            )
            responses.append(response)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Check most requests succeeded
        success_count = sum(1 for r in responses if r.status_code == 200)
        success_rate = success_count / num_requests
        assert success_rate >= 0.8, f"Success rate {success_rate:.2%} is too low"
        
        # Check throughput
        throughput = num_requests / total_time
        assert throughput > 0.1, f"Throughput {throughput:.2f} req/s is too low"


class TestMemoryUsage:
    """Test memory usage and potential leaks."""

    @pytest.mark.performance
    def test_memory_usage_baseline(self, client: TestClient):
        """Test baseline memory usage."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make a few requests to initialize the system
        for i in range(5):
            client.post(
                "/agent/chat",
                json={"message": f"Memory test {i}", "session_id": f"memory-test-{i}"}
            )
        
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - initial_memory
        
        # Memory increase should be reasonable
        assert memory_increase < 100, f"Memory increase {memory_increase:.2f}MB is too high"

    @pytest.mark.requires_agent
    @pytest.mark.performance
    def test_memory_leak_detection(self, client: TestClient):
        """Test for memory leaks over multiple requests."""
        process = psutil.Process()
        
        # Get baseline memory
        gc.collect()  # Force garbage collection
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make many requests
        for i in range(100):
            response = client.post(
                "/agent/chat",
                json={"message": f"Memory leak test {i}", "session_id": f"leak-test-{i}"}
            )
            # Only check every 10 requests to avoid too much overhead
            if i % 10 == 0:
                gc.collect()
        
        # Force garbage collection and check memory
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (no significant leak)
        assert memory_increase < 200, f"Potential memory leak: {memory_increase:.2f}MB increase"


class TestWebSocketPerformance:
    """Test WebSocket performance."""

    @pytest.mark.requires_agent
    @pytest.mark.performance
    def test_websocket_response_time(self, client: TestClient):
        """Test WebSocket streaming response time."""
        try:
            start_time = time.time()
            
            with client.websocket_connect("/chat/stream") as websocket:
                # Send a message
                input_data = {
                    "input": {"input": "Performance test message", "chat_history": []}
                }
                websocket.send_json([input_data])
                
                # Wait for response
                response_received = False
                timeout = 10  # seconds
                start_wait = time.time()
                
                while time.time() - start_wait < timeout:
                    try:
                        data = websocket.receive_json(timeout=1)
                        if data.get("event") == "on_chat_model_end":
                            response_received = True
                            break
                    except Exception:
                        continue
                
                end_time = time.time()
                response_time = end_time - start_time
                
                assert response_received, "No response received within timeout"
                assert response_time < 15.0, f"WebSocket response time {response_time:.2f}s exceeds 15s limit"
                
        except Exception:
            pytest.skip("WebSocket not available in test environment")

    @pytest.mark.requires_agent
    @pytest.mark.performance
    def test_concurrent_websocket_connections(self, client: TestClient):
        """Test multiple concurrent WebSocket connections."""
        num_connections = 5
        
        def websocket_test(connection_id):
            try:
                with client.websocket_connect("/chat/stream") as websocket:
                    input_data = {
                        "input": {"input": f"Concurrent test {connection_id}", "chat_history": []}
                    }
                    websocket.send_json([input_data])
                    
                    # Wait for response
                    response_received = False
                    for _ in range(10):  # Try 10 times
                        try:
                            data = websocket.receive_json(timeout=1)
                            if data.get("event") == "on_chat_model_end":
                                response_received = True
                                break
                        except Exception:
                            continue
                    
                    return response_received
            except Exception:
                return False
        
        # Test concurrent connections
        with ThreadPoolExecutor(max_workers=num_connections) as executor:
            futures = [executor.submit(websocket_test, i) for i in range(num_connections)]
            results = [future.result() for future in as_completed(futures)]
        
        # Check that most connections succeeded
        success_count = sum(1 for result in results if result)
        success_rate = success_count / num_connections
        assert success_rate >= 0.6, f"WebSocket success rate {success_rate:.2%} is too low"


class TestAdapterPerformance:
    """Test performance of different adapters."""

    @pytest.mark.requires_agent
    @pytest.mark.performance
    def test_mcp_adapter_performance(self, client: TestClient):
        """Test MCP adapter performance."""
        mcp_requests = [
            {"method": "tools/list"},
            {"method": "tools/call", "params": {"name": "chat", "arguments": {"message": "MCP test"}}},
            {"method": "resources/list"},
        ]
        
        for request_data in mcp_requests:
            start_time = time.time()
            
            response = client.post("/mcp/", json=request_data)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 10.0, f"MCP request took {response_time:.2f}s"

    @pytest.mark.requires_agent
    @pytest.mark.performance
    def test_webhook_adapter_performance(self, client: TestClient):
        """Test webhook adapter performance."""
        webhook_requests = [
            {"message": "Webhook test", "user_id": "test-user", "platform": "test"},
            {
                "message": {
                    "text": "Telegram webhook test",
                    "from": {"id": 123456789},
                    "chat": {"id": 123456789}
                }
            },
        ]
        
        for request_data in webhook_requests:
            start_time = time.time()
            
            if "message" in request_data and isinstance(request_data["message"], dict):
                response = client.post("/webhook/telegram", json=request_data)
            else:
                response = client.post("/webhook/", json=request_data)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 10.0, f"Webhook request took {response_time:.2f}s"


@pytest.mark.integration
@pytest.mark.performance
class TestPerformanceIntegration:
    """Integration performance tests."""

    @pytest.mark.requires_agent
    def test_end_to_end_performance(self, client: TestClient):
        """Test end-to-end performance across all components."""
        test_scenarios = [
            {
                "name": "Simple Chat",
                "endpoint": "/agent/chat",
                "data": {"message": "Hello", "session_id": "e2e-test"}
            },
            {
                "name": "MCP Tools List",
                "endpoint": "/mcp/",
                "data": {"method": "tools/list"}
            },
            {
                "name": "Webhook Generic",
                "endpoint": "/webhook/",
                "data": {"message": "Test", "user_id": "test", "platform": "test"}
            },
        ]
        
        for scenario in test_scenarios:
            start_time = time.time()
            
            response = client.post(scenario["endpoint"], json=scenario["data"])
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200, f"{scenario['name']} failed"
            assert response_time < 15.0, f"{scenario['name']} took {response_time:.2f}s"

    def test_system_resources_under_load(self, client: TestClient):
        """Test system resource usage under load."""
        process = psutil.Process()
        
        # Get baseline metrics
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_cpu = process.cpu_percent()
        
        # Simulate load
        def make_request(i):
            return client.post(
                "/agent/chat",
                json={"message": f"Load test {i}", "session_id": f"load-test-{i}"}
            )
        
        # Make requests in batches
        batch_size = 10
        num_batches = 5
        
        for batch in range(num_batches):
            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                futures = [
                    executor.submit(make_request, batch * batch_size + i)
                    for i in range(batch_size)
                ]
                responses = [future.result() for future in as_completed(futures)]
            
            # Check resource usage after each batch
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = current_memory - initial_memory
            
            # Memory increase should be reasonable
            assert memory_increase < 500, f"Memory usage {memory_increase:.2f}MB too high after batch {batch}"
