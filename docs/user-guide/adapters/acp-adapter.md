# ACP (Agent Communication Protocol) Adapter

This guide explains how to use the Agent Communication Protocol (ACP) adapter for asynchronous, brokered communication between agents.

## Overview

Unlike the direct peer-to-peer communication of A2A, the ACP adapter uses a message broker (like RabbitMQ) for more robust, decoupled, and persistent messaging. This is ideal for scenarios where agents may not be online simultaneously or when you need guaranteed message delivery.

## How It Works

1.  **Connection**: The ACP adapter connects to a message broker specified by `ACP_BROKER_URL`.
2.  **Queues**: It listens for incoming messages on a dedicated queue.
3.  **Processing**: When a message arrives, it's converted to an `AgentRequest` and processed by your agent.
4.  **Replying**: The `AgentResponse` is sent back to a reply-to queue specified in the original message.

## Configuration

Enable and configure the ACP adapter using these environment variables in your `.env` file.

| Variable                  | Description                               | Default                   | Required |
|---------------------------|-------------------------------------------|---------------------------|----------|
| `ACP_ENABLED`             | Enable the ACP adapter                    | `True`                    | No       |
| `ACP_AGENT_ID`            | A unique identifier for your agent        | Auto-generated UUID       | No       |
| `ACP_BROKER_URL`          | The connection URL for the message broker | `amqp://localhost:5672`   | No       |
| `ACP_SESSION_PERSISTENCE` | Enable session persistence in the broker  | `True`                    | No       |

### Example `.env` configuration:

```env
# .env
ACP_ENABLED=True
ACP_AGENT_ID=my-reliable-agent
ACP_BROKER_URL=amqp://guest:guest@localhost:5672/
```

## Testing the ACP Adapter

Testing ACP requires a running message broker (e.g., RabbitMQ). You can use a Python script with a library like `pika` to send a test message.

### Example Test Script (`test_acp.py`)

```python
import pika
import json
import uuid

# Connection parameters
BROKER_URL = 'amqp://guest:guest@localhost:5672/'
AGENT_QUEUE = 'agent_messages' # This should match your agent's listening queue

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.URLParameters(BROKER_URL))
channel = connection.channel()

# Create a temporary queue for the reply
result = channel.queue_declare(queue='', exclusive=True)
reply_queue_name = result.method.queue

# Message payload
message_body = {
    "sender_agent_id": "test-script-sender",
    "message": "Hello from an ACP client!",
    "session_id": "acp-session-456"
}

# Publish the message
channel.basic_publish(
    exchange='',
    routing_key=AGENT_QUEUE,
    properties=pika.BasicProperties(
        reply_to=reply_queue_name,
        correlation_id=str(uuid.uuid4()),
    ),
    body=json.dumps(message_body)
)

print(f" [x] Sent message to queue '{AGENT_QUEUE}'")

# TODO: Implement logic to wait for and receive the reply
# from `reply_queue_name`.

connection.close()
```

This script sends a message but does not wait for a reply. A full client would listen on the `reply_to` queue for the agent's response.

## Next Steps

- Set up a message broker like RabbitMQ to use this adapter.
- Explore the A2A Adapter for direct, real-time communication.