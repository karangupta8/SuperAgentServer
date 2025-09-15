"""
Pytest configuration and shared fixtures.
"""

import asyncio
import os
import time

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

# Load environment variables from .env file before other imports
load_dotenv()

from src.super_agent_server.server import create_app

# Attempt to import pika for broker checks, but don't fail if it's not installed.
try:
    import pika  # type: ignore
except ImportError:
    pika = None


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "requires_agent: mark test as requiring an initialized agent"
    )
    config.addinivalue_line(
        "markers", "requires_broker: mark test as requiring a running message broker"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def client():
    """Create a TestClient instance for the FastAPI app."""
    app = create_app()
    agent_should_be_initialized = os.getenv("OPENAI_API_KEY") is not None

    with TestClient(app) as c:
        # If we expect the agent to be initialized, wait for it to become ready.
        # This prevents race conditions in tests that run immediately after startup.
        if agent_should_be_initialized:
            for _ in range(10):  # Try for a few seconds
                try:
                    response = c.get("/health")
                    if (response.status_code == 200 and
                            response.json().get("agent_initialized")):
                        break
                except Exception:
                    pass
                time.sleep(0.5)
        yield c


@pytest.fixture(scope="module")
def uninitialized_client():
    """Create a TestClient instance for an app without an initialized agent."""
    # Temporarily unset the API key to prevent agent initialization
    original_key = os.environ.pop("OPENAI_API_KEY", None)
    app = create_app()
    with TestClient(app) as c:
        yield c
    # Restore the key if it was originally set
    if original_key:
        os.environ["OPENAI_API_KEY"] = original_key


@pytest.fixture
def sample_agent_request():
    """Sample agent request for testing."""
    return {
        "message": "Hello, test!",
        "session_id": "test-session",
        "metadata": {"test": True}
    }


@pytest.fixture
def mock_openai_key():
    """Mock OpenAI API key for testing."""
    return "test-key-12345"


@pytest.fixture
def performance_test_data():
    """Sample data for performance testing."""
    return {
        "small_message": "Performance test",
        "medium_message": "A" * 1000,  # 1KB message
        "large_message": "A" * 10000,  # 10KB message
        "concurrent_requests": 10,
        "batch_size": 5,
    }


@pytest.fixture
def security_test_data():
    """Sample data for security testing."""
    return {
        "malicious_inputs": [
            "__import__('os').system('echo hacked')",
            "exec('import os; os.system(\"echo hacked\")')",
            "open('/etc/passwd').read()",
            "eval('print(1)')",
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
        ],
        "valid_inputs": [
            "Hello, world!",
            "What time is it?",
            "2 + 3",
            "Calculate 10 * 5",
        ]
    }


@pytest.fixture
def integration_test_scenarios():
    """Sample scenarios for integration testing."""
    return {
        "chat_workflow": {
            "steps": [
                {"endpoint": "/health", "method": "GET"},
                {"endpoint": "/agent/schema", "method": "GET"},
                {"endpoint": "/agent/chat", "method": "POST", "data": {"message": "Test", "session_id": "integration-test"}},
            ]
        },
        "adapter_workflows": [
            {"name": "mcp", "endpoint": "/mcp/", "data": {"method": "tools/list"}},
            {"name": "webhook", "endpoint": "/webhook/", "data": {"message": "Test", "user_id": "test", "platform": "test"}},
            {"name": "a2a", "endpoint": "/a2a/message", "data": {"sender_agent_id": "test", "message": "Test"}},
            {"name": "acp", "endpoint": "/acp/message", "data": {"sender_agent_id": "test", "message": "Test"}},
        ]
    }


def _is_broker_running():
    """Check if the message broker is running and accessible."""
    acp_enabled = os.getenv("ACP_ENABLED", "True").lower() == "true"
    broker_url = os.getenv(
        "ACP_BROKER_URL", "amqp://guest:guest@localhost:5672/"
    )

    if not acp_enabled or pika is None:
        return False
    try:
        connection = pika.BlockingConnection(pika.URLParameters(broker_url))
        connection.close()
        return True
    except pika.exceptions.AMQPConnectionError:
        return False


@pytest.fixture(autouse=True)
def _skip_by_marker(request):
    """Skip tests based on custom markers."""
    if request.node.get_closest_marker("requires_agent"):
        if os.getenv("OPENAI_API_KEY") is None:
            pytest.skip("OPENAI_API_KEY not set, agent not initialized")

    if request.node.get_closest_marker("requires_broker"):
        if not _is_broker_running():
            pytest.skip("ACP message broker is not running or not configured")
    
    # Skip performance tests in CI or when explicitly disabled
    if request.node.get_closest_marker("performance"):
        if os.getenv("SKIP_PERFORMANCE_TESTS", "false").lower() == "true":
            pytest.skip("Performance tests disabled")
    
    # Skip integration tests when explicitly disabled
    if request.node.get_closest_marker("integration"):
        if os.getenv("SKIP_INTEGRATION_TESTS", "false").lower() == "true":
            pytest.skip("Integration tests disabled")
    
    # Skip slow tests in fast test runs
    if request.node.get_closest_marker("slow"):
        if os.getenv("SKIP_SLOW_TESTS", "false").lower() == "true":
            pytest.skip("Slow tests disabled")
