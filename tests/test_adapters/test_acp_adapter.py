"""
Tests for the ACP (Agent Communication Protocol) adapter.

Note: These tests require a running message broker (e.g., RabbitMQ)
and the `pika` library to be installed.
"""

import os
import pytest
import json
import uuid
import time

# Attempt to import pika, but don't fail if it's not installed.
# The tests will be skipped anyway.
try:
    import pika  # type: ignore
except ImportError:
    pika = None

ACP_BROKER_URL = os.getenv("ACP_BROKER_URL", "amqp://guest:guest@localhost:5672/")
agent_queue = os.getenv("ACP_AGENT_QUEUE", "super_agent_acp")


@pytest.mark.requires_agent
@pytest.mark.requires_broker
def test_acp_message_e2e():
    """
    End-to-end test for the ACP adapter.
    Sends a message via RabbitMQ and waits for a reply.
    """
    connection = pika.BlockingConnection(pika.URLParameters(ACP_BROKER_URL))
    channel = connection.channel()

    # Declare a temporary, exclusive queue for the reply
    result = channel.queue_declare(queue="", exclusive=True)
    reply_queue_name = result.method.queue

    correlation_id = str(uuid.uuid4())
    message_body = {
        "sender_agent_id": "pytest-acp-sender",
        "message": "Hello from ACP test",
        "session_id": "acp-test-session-123",
    }

    channel.basic_publish(
        exchange="",
        routing_key=agent_queue,
        properties=pika.BasicProperties(reply_to=reply_queue_name, correlation_id=correlation_id),
        body=json.dumps(message_body),
    )

    # Wait for and retrieve the reply
    method_frame, properties, body = channel.basic_get(queue=reply_queue_name, auto_ack=True)

    assert body is not None, "Did not receive a response from the agent via ACP"
    assert properties.correlation_id == correlation_id, "Correlation ID of response does not match"
    response_data = json.loads(body)
    assert "message" in response_data
    assert isinstance(response_data["message"], str)
    assert response_data["session_id"] == "acp-test-session-123"

    connection.close()