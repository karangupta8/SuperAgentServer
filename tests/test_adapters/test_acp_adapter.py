"""
Tests for the ACP (Agent Communication Protocol) adapter.

Note: These tests require a running message broker (e.g., RabbitMQ)
and the `pika` library to be installed.
"""

import json
import os
import time
import uuid

import pytest

# Attempt to import pika, but don't fail if it's not installed.
# The tests will be skipped anyway.
try:
    import pika  # type: ignore
except ImportError:
    pika = None

ACP_BROKER_URL = os.getenv(
    "ACP_BROKER_URL", "amqp://guest:guest@localhost:5672/"
)
agent_queue = os.getenv("ACP_AGENT_QUEUE", "super_agent_acp")


@pytest.mark.requires_agent
@pytest.mark.requires_broker
def test_acp_message_e2e():
    """
    End-to-end test for the ACP adapter.

    This test simulates a complete ACP message flow:
    1. Send a message to the agent queue
    2. Wait for a response
    3. Verify the response format and content
    """
    if pika is None:
        pytest.skip("pika library not installed")

    # Create a unique correlation ID for this test
    correlation_id = str(uuid.uuid4())
    response_queue = f"response_{correlation_id}"

    # Connect to the broker
    connection = pika.BlockingConnection(pika.URLParameters(ACP_BROKER_URL))
    channel = connection.channel()

    # Declare the response queue
    channel.queue_declare(queue=response_queue, exclusive=True)

    # Prepare the message
    message = {
        "sender_agent_id": "test-sender-agent",
        "message": "Hello from ACP test!",
        "session_id": f"acp-test-{correlation_id}",
    }

    # Send the message
    channel.basic_publish(
        exchange="",
        routing_key=agent_queue,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            reply_to=response_queue,
            correlation_id=correlation_id,
        ),
    )

    # Wait for response
    response_received = False
    response_data = None

    def callback(ch, method, properties, body):
        nonlocal response_received, response_data
        if properties.correlation_id == correlation_id:
            response_data = json.loads(body)
            response_received = True
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=response_queue, on_message_callback=callback, auto_ack=False
    )

    # Wait for response with timeout
    start_time = time.time()
    while not response_received and (time.time() - start_time) < 10:
        connection.process_data_events(time_limit=0.1)

    connection.close()

    # Verify response
    assert response_received, "No response received within timeout"
    assert response_data is not None
    assert "message" in response_data
    assert isinstance(response_data["message"], str)
    assert response_data["session_id"] == f"acp-test-{correlation_id}"
    assert "metadata" in response_data
    assert response_data["metadata"]["source_protocol"] == "acp"