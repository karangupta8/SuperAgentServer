# REST API Reference

Complete REST API documentation for SuperAgentServer.

## Overview

SuperAgentServer exposes a comprehensive REST API that allows you to interact with your agents through standard HTTP endpoints.

## Base URL

All API endpoints are relative to the base URL:

```
http://localhost:8000
```

## Authentication

Currently, SuperAgentServer does not require authentication. In production deployments, you should implement appropriate authentication mechanisms.

## Response Format

All API responses follow a consistent format:

### Success Response

```json
{
  "message": "Hello! I'm doing well, thank you for asking.",
  "session_id": "optional-session-id",
  "metadata": {
    "agent_name": "agent-name",
    "timestamp": "2024-01-15T10:30:00.000000",
    "tools_used": ["tool1", "tool2"]
  }
}
```

### Error Response

```json
{
  "detail": "Error message",
  "status_code": 400,
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

## Core Endpoints

### Server Information

#### GET /

Get server information and status.

**Response:**
```json
{
  "name": "SuperAgentServer",
  "version": "0.1.0",
  "description": "Universal Agent Adapter Layer for LangChain agents",
  "status": "running",
  "adapters": ["mcp", "webhook", "a2a", "acp"]
}
```

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "adapters": 4
}
```

### Agent Endpoints

#### POST /agent/chat

Chat directly with the agent.

**Request Body:**
```json
{
  "message": "Hello, how are you?",
  "session_id": "optional-session-id",
  "metadata": {
    "user_id": "user123"
  },
  "tools": ["tool1", "tool2"]
}
```

**Response:**
```json
{
  "message": "Hello! I'm doing well, thank you for asking.",
  "session_id": "optional-session-id",
  "metadata": {
    "tools_used": ["tool1"],
    "timestamp": "2024-01-01T12:00:00Z"
  },
  "tools_used": ["tool1"],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### GET /agent/schema

Get the agent's schema.

**Response:**
```json
{
  "name": "example-agent",
  "description": "A simple example agent",
  "input_schema": {
    "type": "object",
    "properties": {
      "message": {
        "type": "string",
        "description": "The input message"
      }
    },
    "required": ["message"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "message": {
        "type": "string",
        "description": "The response message"
      }
    }
  }
}
```

### Adapter Endpoints

#### GET /adapters

List all available adapters.

**Response:**
```json
{
  "adapters": [
    {
      "name": "mcp",
      "type": "MCPAdapter",
      "config": {
        "name": "mcp",
        "prefix": "mcp",
        "enabled": true
      },
      "manifest": {
        "protocolVersion": "2024-11-05",
        "capabilities": {
          "tools": {}
        }
      }
    }
  ]
}
```

#### GET /manifests

Get manifests for all adapters.

**Response:**
```json
{
  "mcp": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {}
    }
  },
  "webhook": {
    "endpoints": [
      "/webhook/webhook",
      "/webhook/telegram",
      "/webhook/slack",
      "/webhook/discord"
    ]
  }
}
```

## MCP Endpoints

### Tools

#### POST /mcp/tools/list

List available MCP tools.

**Request Body:**
```json
{
  "method": "tools/list",
  "params": {}
}
```

**Response:**
```json
{
  "result": {
    "tools": [
      {
        "name": "agent_chat",
        "description": "Chat with the agent",
        "inputSchema": {
          "type": "object",
          "properties": {
            "message": {
              "type": "string",
              "description": "The message to send to the agent"
            }
          },
          "required": ["message"]
        }
      }
    ]
  }
}
```

#### POST /mcp/tools/call

Call an MCP tool.

**Request Body:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "agent_chat",
    "arguments": {
      "message": "Hello from MCP!"
    }
  }
}
```

**Response:**
```json
{
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Hello! How can I help you today?"
      }
    ]
  }
}
```

### Resources

#### POST /mcp/resources/list

List available MCP resources.

**Request Body:**
```json
{
  "method": "resources/list",
  "params": {}
}
```

**Response:**
```json
{
  "result": {
    "resources": [
      {
        "uri": "agent://schema",
        "name": "Agent Schema",
        "description": "The agent's input/output schema",
        "mimeType": "application/json"
      }
    ]
  }
}
```

#### POST /mcp/resources/read

Read an MCP resource.

**Request Body:**
```json
{
  "method": "resources/read",
  "params": {
    "uri": "agent://schema"
  }
}
```

**Response:**
```json
{
  "result": {
    "contents": [
      {
        "uri": "agent://schema",
        "mimeType": "application/json",
        "text": "{\"name\": \"example-agent\", \"description\": \"A simple example agent\"}"
      }
    ]
  }
}
```

#### GET /mcp/manifest

Get the MCP manifest.

**Response:**
```json
{
  "protocolVersion": "2024-11-05",
  "capabilities": {
    "tools": {}
  },
  "serverInfo": {
    "name": "SuperAgentServer",
    "version": "0.1.0"
  }
}
```

## Webhook Endpoints

### Generic Webhook

#### POST /webhook/webhook

Generic webhook endpoint for external platforms.

**Request Body:**
```json
{
  "message": "Hello from webhook!",
  "user_id": "user123",
  "platform": "custom",
  "metadata": {
    "source": "external_app"
  }
}
```

**Response:**
```json
{
  "message": "Hello! I received your message via webhook.",
  "user_id": "user123",
  "platform": "custom",
  "metadata": {
    "processed_at": "2024-01-15T10:30:00.000000"
  }
}
```

### Platform-Specific Webhooks

#### POST /webhook/telegram

Telegram bot webhook.

**Request Body:**
```json
{
  "message": {
    "text": "Hello from Telegram!",
    "from": {
      "id": 123456789,
      "first_name": "John",
      "username": "john_doe"
    },
    "chat": {
      "id": 123456789,
      "type": "private"
    }
  }
}
```

**Response:**
```json
{
  "message": "Hello John! I received your message from Telegram.",
  "user_id": "123456789",
  "platform": "telegram",
  "metadata": {
    "telegram_user": {
      "id": 123456789,
      "first_name": "John",
      "username": "john_doe"
    }
  }
}
```

#### POST /webhook/slack

Slack app webhook.

**Request Body:**
```json
{
  "message": {
    "text": "Hello from Slack!",
    "user": "U1234567890",
    "channel": "C1234567890",
    "team": "T1234567890"
  }
}
```

**Response:**
```json
{
  "message": "Hello! I received your message from Slack.",
  "user_id": "U1234567890",
  "platform": "slack",
  "metadata": {
    "slack_channel": "C1234567890",
    "slack_team": "T1234567890"
  }
}
```

#### POST /webhook/discord

Discord bot webhook.

**Request Body:**
```json
{
  "message": {
    "content": "Hello from Discord!",
    "author": {
      "id": "123456789012345678",
      "username": "john_doe",
      "discriminator": "1234"
    },
    "channel_id": "987654321098765432",
    "guild_id": "111111111111111111"
  }
}
```

**Response:**
```json
{
  "message": "Hello john_doe! I received your message from Discord.",
  "user_id": "123456789012345678",
  "platform": "discord",
  "metadata": {
    "discord_channel": "987654321098765432",
    "discord_guild": "111111111111111111"
  }
}
```

#### GET /webhook/health

Webhook health check.

**Response:**
```json
{
  "status": "healthy",
  "webhooks": {
    "generic": true,
    "telegram": true,
    "slack": true,
    "discord": true
  }
}
```

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

## Error Handling

### Validation Errors

```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ],
  "status_code": 422
}
```

### Server Errors

```json
{
  "detail": "Internal server error",
  "status_code": 500
}
```

## Rate Limiting

Rate limiting is not currently implemented but should be added for production deployments.

## CORS

CORS is enabled by default with the following origins:

- `http://localhost:3000`
- `http://127.0.0.1:3000`

Configure additional origins using the `ALLOWED_ORIGINS` environment variable.

## Examples

### cURL Examples

```bash
# Basic agent chat
curl -X POST "http://localhost:8000/agent/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello!"}'

# MCP tools list
curl -X POST "http://localhost:8000/mcp/tools/list"

# Webhook message
curl -X POST "http://localhost:8000/webhook/webhook" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello from webhook!", "user_id": "user123"}'
```

### Python Examples

```python
import requests

# Basic agent chat
response = requests.post(
    "http://localhost:8000/agent/chat",
    json={"message": "Hello!"}
)
print(response.json())

# MCP tools list
response = requests.post("http://localhost:8000/mcp/tools/list")
print(response.json())
```

### JavaScript Examples

```javascript
// Basic agent chat
const response = await fetch('http://localhost:8000/agent/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ message: 'Hello!' })
});

const data = await response.json();
console.log(data);
```

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Next Steps

- **[WebSocket API](websocket-api.md)** - Real-time streaming documentation
- **[MCP API](mcp-api.md)** - Model Context Protocol documentation
- **[Webhook API](webhook-api.md)** - Webhook integration documentation
