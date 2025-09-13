# API Reference

## Core API

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
    },
    "required": ["message"]
  }
}
```

### Server Endpoints

#### GET /

Get server information.

**Response:**
```json
{
  "name": "SuperAgentServer",
  "version": "0.1.0",
  "description": "Universal Agent Adapter Layer",
  "status": "running",
  "adapters": ["mcp", "webhook"]
}
```

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "adapters": 2
}
```

#### GET /manifests

Get manifests for all adapters.

**Response:**
```json
{
  "mcp": {
    "protocolVersion": "2024-11-05",
    "capabilities": {...},
    "tools": [...],
    "resources": [...]
  },
  "webhook": {
    "name": "example-agent-webhook",
    "version": "0.1.0",
    "endpoints": {...}
  }
}
```

## MCP API

### POST /mcp/tools/list

List available MCP tools.

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
              "description": "The message to send"
            }
          },
          "required": ["message"]
        }
      }
    ]
  }
}
```

### POST /mcp/tools/call

Call an MCP tool.

**Request Body:**
```json
{
  "name": "agent_chat",
  "arguments": {
    "message": "Hello!",
    "session_id": "session123"
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
    ],
    "metadata": {
      "session_id": "session123",
      "tools_used": [],
      "timestamp": "2024-01-01T12:00:00Z"
    }
  }
}
```

### POST /mcp/resources/list

List available MCP resources.

**Response:**
```json
{
  "result": {
    "resources": [
      {
        "uri": "agent://schema",
        "name": "Agent Schema",
        "description": "Schema for the agent",
        "mimeType": "application/json"
      }
    ]
  }
}
```

### POST /mcp/resources/read

Read an MCP resource.

**Request Body:**
```json
{
  "uri": "agent://schema"
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
        "text": "{\"name\": \"example-agent\", ...}"
      }
    ]
  }
}
```

### GET /mcp/manifest

Get the MCP manifest.

**Response:**
```json
{
  "protocolVersion": "2024-11-05",
  "capabilities": {
    "tools": {},
    "resources": {}
  },
  "serverInfo": {
    "name": "example-agent-mcp",
    "version": "0.1.0",
    "description": "MCP adapter for example agent"
  },
  "tools": [...],
  "resources": [...]
}
```

## Webhook API

### POST /webhook/webhook

Generic webhook endpoint.

**Request Body:**
```json
{
  "message": "Hello!",
  "user_id": "user123",
  "session_id": "session123",
  "platform": "custom",
  "metadata": {
    "source": "api"
  }
}
```

**Response:**
```json
{
  "message": "Hello! How can I help you?",
  "user_id": "user123",
  "session_id": "session123",
  "platform": "custom",
  "metadata": {
    "tools_used": [],
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### POST /webhook/telegram

Telegram webhook endpoint.

**Request Body:** (Telegram webhook format)
```json
{
  "message": {
    "message_id": 123,
    "from": {
      "id": 123456789,
      "username": "user"
    },
    "chat": {
      "id": 123456789,
      "type": "private"
    },
    "text": "Hello!"
  }
}
```

**Response:**
```json
{
  "message": "Hello! How can I help you?",
  "user_id": "123456789",
  "session_id": "123456789",
  "platform": "telegram",
  "metadata": {
    "message_id": 123,
    "chat_type": "private",
    "username": "user"
  }
}
```

### POST /webhook/slack

Slack webhook endpoint.

**Request Body:** (Slack webhook format)
```json
{
  "text": "Hello!",
  "user": "U1234567890",
  "channel": "C1234567890",
  "team": "T1234567890"
}
```

**Response:**
```json
{
  "message": "Hello! How can I help you?",
  "user_id": "U1234567890",
  "session_id": "C1234567890",
  "platform": "slack",
  "metadata": {
    "team": "T1234567890",
    "channel_name": "general"
  }
}
```

### POST /webhook/discord

Discord webhook endpoint.

**Request Body:** (Discord webhook format)
```json
{
  "content": "Hello!",
  "author": {
    "id": "123456789012345678",
    "username": "user"
  },
  "channel_id": "123456789012345678",
  "guild_id": "123456789012345678"
}
```

**Response:**
```json
{
  "message": "Hello! How can I help you?",
  "user_id": "123456789012345678",
  "session_id": "123456789012345678",
  "platform": "discord",
  "metadata": {
    "username": "user",
    "guild_id": "123456789012345678",
    "message_id": "123456789012345678"
  }
}
```

### GET /webhook/health

Webhook health check.

**Response:**
```json
{
  "status": "healthy",
  "adapter": "webhook"
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `400 Bad Request`: Invalid request format
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Agent not initialized
