"""
Pytest configuration and shared fixtures.
"""

from dotenv import load_dotenv
import pytest
import asyncio
import os
from fastapi.testclient import TestClient

# Load environment variables from .env file before other imports
load_dotenv()

from src.super_agent_server.server import create_app


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
    with TestClient(app) as c:
        yield c


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
