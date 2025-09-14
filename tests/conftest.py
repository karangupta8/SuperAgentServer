"""
Pytest configuration and shared fixtures.
"""

from dotenv import load_dotenv
import pytest
import asyncio
import os
import time
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
    config.addinivalue_line("markers", "requires_agent: mark test as requiring an initialized agent")
    config.addinivalue_line("markers", "requires_broker: mark test as requiring a running message broker")


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
                    if response.status_code == 200 and response.json().get("agent_initialized"):
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


def _is_broker_running():
    """Check if the message broker is running and accessible."""
    acp_enabled = os.getenv("ACP_ENABLED", "True").lower() == "true"
    broker_url = os.getenv("ACP_BROKER_URL", "amqp://guest:guest@localhost:5672/")

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
