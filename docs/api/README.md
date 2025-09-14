# API Reference

Complete API reference for SuperAgentServer endpoints and protocols.

## Overview

SuperAgentServer exposes your agents through multiple API interfaces:

- **REST API** - Standard HTTP endpoints
- **WebSocket API** - Real-time streaming communication
- **MCP API** - Model Context Protocol integration
- **Webhook API** - Platform-specific webhook endpoints

## Quick Navigation

- **[REST API](rest-api.md)** - HTTP endpoints and request/response formats
- **[WebSocket API](websocket-api.md)** - Real-time streaming endpoints
- **[MCP API](mcp-api.md)** - Model Context Protocol specification
- **[Webhook API](webhook-api.md)** - Webhook endpoints for external platforms

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

## Rate Limiting

Rate limiting is not currently implemented but should be added for production deployments.

## CORS

CORS is enabled by default with the following origins:

- `http://localhost:3000`
- `http://127.0.0.1:3000`

Configure additional origins using the `ALLOWED_ORIGINS` environment variable.

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

## Common Headers

### Request Headers

```
Content-Type: application/json
Accept: application/json
```

### Response Headers

```
Content-Type: application/json
X-Request-ID: unique-request-id
```

## Error Handling

All errors are returned in a consistent format:

```json
{
  "detail": "Human-readable error message",
  "status_code": 400,
  "timestamp": "2024-01-15T10:30:00.000000",
  "path": "/api/endpoint"
}
```

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

## WebSocket Examples

```javascript
// WebSocket connection
const ws = new WebSocket('ws://localhost:8000/chat/stream');

ws.onopen = function() {
  // Send a message
  ws.send(JSON.stringify([{
    input: {
      input: "Hello, stream!",
      chat_history: []
    }
  }]));
};

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

## Testing

### Health Check

```bash
curl http://localhost:8000/health
```

### Server Info

```bash
curl http://localhost:8000/
```

### Adapter Status

```bash
curl http://localhost:8000/adapters
```

## SDKs and Libraries

### Python SDK

```python
from super_agent_server import SuperAgentClient

client = SuperAgentClient("http://localhost:8000")

# Chat with agent
response = await client.chat("Hello!")
print(response.message)

# List MCP tools
tools = await client.list_mcp_tools()
print(tools)
```

### JavaScript SDK

```javascript
import { SuperAgentClient } from 'super-agent-server-js';

const client = new SuperAgentClient('http://localhost:8000');

// Chat with agent
const response = await client.chat('Hello!');
console.log(response.message);

// List MCP tools
const tools = await client.listMCPTools();
console.log(tools);
```

## Next Steps

- **[REST API](rest-api.md)** - Detailed REST endpoint documentation
- **[WebSocket API](websocket-api.md)** - Real-time streaming documentation
- **[MCP API](mcp-api.md)** - Model Context Protocol documentation
- **[Webhook API](webhook-api.md)** - Webhook integration documentation
