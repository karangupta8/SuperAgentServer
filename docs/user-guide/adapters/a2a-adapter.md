# A2A (Agent-to-Agent) Adapter

This guide explains how to use the Agent-to-Agent (A2A) adapter to enable direct communication between your SuperAgentServer agent and other A2A-compatible agents.

## Overview

The A2A adapter allows your agent to join a decentralized network of agents, discover other agents, and exchange messages securely. It follows the principles of the A2A protocol for interoperability.

## How It Works

1.  **Discovery**: Your agent registers with a discovery service, making it visible to other agents on the network.
2.  **Handshake**: When another agent wants to communicate, it performs a secure handshake.
3.  **Messaging**: Once connected, agents can exchange messages through a standardized format.

SuperAgentServer handles the protocol complexities, allowing you to focus on your agent's logic. Incoming A2A messages are converted into `AgentRequest` objects and processed by your agent. The `AgentResponse` is then sent back to the originating agent.

## Configuration

Enable and configure the A2A adapter using these environment variables in your `.env` file.

| Variable              | Description                               | Default                                | Required |
|-----------------------|-------------------------------------------|----------------------------------------|----------|
| `A2A_ENABLED`         | Enable the A2A adapter                    | `True`                                 | No       |
| `A2A_AGENT_ID`        | A unique identifier for your agent        | Auto-generated UUID                    | No       |
| `A2A_DISCOVERY_URL`   | The URL of the A2A discovery service      | `https://discovery.a2a-protocol.org`   | No       |
| `A2A_MESSAGE_ROUTING` | Enable message routing through the network| `True`                                 | No       |

### Example `.env` configuration:

```env
# .env
A2A_ENABLED=True
A2A_AGENT_ID=my-awesome-chat-agent
```
## Agent Protocol Card
The A2A adapter exposes a "protocol card" that describes your agent's capabilities to other agents on the network. This card is automatically generated based on your agent's schema.

You can retrieve the card by fetching the server's global manifests endpoint
```bash
curl http://localhost:8000/manifests
```
The response will be a JSON object containing manifests for all active adapters. The A2A card can be found under the a2a key.


## Testing the A2A Adapter

You can simulate an incoming A2A message by sending a POST request to the `/a2a/message` endpoint. This endpoint is designed for testing and allows you to bypass the discovery and handshake process.

### Send a Test Message

Use `curl` or a similar tool to send a message to your agent.

```bash
curl -X POST "http://localhost:8000/a2a/message" \
     -H "Content-Type: application/json" \
     -d '{
       "sender_agent_id": "test-sender-agent",
       "message": "Hello from another agent!",
       "session_id": "a2a-session-123"
     }'
```

### Expected Response

Your agent will process the message and return a standard response. The exact message will depend on the agent you are running. If you are running the `SimpleChatAgent`, the response will be:

```json
{
  "message": "Hello! How can I help you today? (Session: a2a-session-123)",
  "session_id": "a2a-session-123",
  "metadata": {
    "processed_at": "simple_agent",
    "input_length": 25,
    "source_protocol": "a2a"
  }
}
```

## Next Steps

- Explore the Agent Communication Protocol (ACP) Adapter for brokered messaging.
- Learn how to create custom agents to handle more complex A2A interactions.