# Usage Guide

## Getting Started

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/superagentserver/super-agent-server.git
cd super-agent-server

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
# Copy the example environment file
cp env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the Server

```bash
# Start the server
python server.py

# Or with uvicorn directly
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`

## Basic Usage

### Testing the Agent

```bash
# Test the agent directly
curl -X POST "http://localhost:8000/agent/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, how are you?"}'
```

### Using MCP

```bash
# List available tools
curl -X POST "http://localhost:8000/mcp/tools/list" \
     -H "Content-Type: application/json" \
     -d '{}'

> **PowerShell:**
> ```powershell
> # List available tools
> Invoke-RestMethod -Uri "http://localhost:8000/mcp/tools/list" -Method Post -ContentType "application/json" -Body '{}'
> ```

# Call a tool
curl -X POST "http://localhost:8000/mcp/tools/call" \
     -H "Content-Type: application/json" \
     -d '{
       "method": "tools/call",
       "params": {
         "name": "chat",
         "arguments": {
           "message": "What is the weather like?",
           "session_id": "session123"
         }
       }
     }'
```

### Using Webhooks

```bash
# Generic webhook
curl -X POST "http://localhost:8000/webhook/webhook" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Hello from webhook!",
       "user_id": "user123",
       "platform": "custom"
     }'
```

## Creating Custom Agents

### 1. Define Your Agent

```python
from agent.base_agent import BaseAgent, AgentRequest, AgentResponse
from typing import Dict, Any

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="my-custom-agent",
            description="A custom agent for specific tasks"
        )
    
    async def initialize(self):
        # Initialize your LangChain agent here
        # This could include loading models, setting up tools, etc.
        pass
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        # Process the request and return a response
        # This is where your agent logic goes
        response_message = f"Processed: {request.message}"
        
        return AgentResponse(
            message=response_message,
            session_id=request.session_id,
            metadata={"processed_by": "my-custom-agent"}
        )
    
    def get_schema(self) -> Dict[str, Any]:
        # Define your agent's input/output schema
        return {
            "name": self.name,
            "description": self.description,
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

### 2. Use Your Agent

```python
from server import create_app
from my_agent import MyCustomAgent

# Create your agent
agent = MyCustomAgent()
await agent.initialize()

# Create FastAPI app
app = create_app(agent)

# Run with uvicorn
# uvicorn my_app:app --reload
```

## Integration Examples

### Telegram Bot Integration

1. **Get your bot token from @BotFather on Telegram**

2. **Set up webhook in Telegram:**
   ```bash
   curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
        -d "url=${WEBHOOK_BASE_URL}/webhook/telegram"
   ```
   > **PowerShell:**
   > ```powershell
   > # Replace <YOUR_BOT_TOKEN> and ${WEBHOOK_BASE_URL} with your values
   > $botToken = "<YOUR_BOT_TOKEN>"
   > $webhookBaseUrl = "${WEBHOOK_BASE_URL}"
   > Invoke-WebRequest -Uri "https://api.telegram.org/bot$botToken/setWebhook" `
   >   -Method POST `
   >   -Body @{url = "$webhookBaseUrl/webhook/telegram"}
   ```

3. **Configure your bot token in .env:**
   ```bash
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   ```

4. **Your bot will now receive messages and respond automatically at:**
   ```
   POST ${WEBHOOK_BASE_URL}/webhook/telegram
   ```

### Slack Integration

1. **Create a Slack app and get your bot token from the OAuth & Permissions page**

2. **Set webhook URL in your Slack app:**
   ```
   ${WEBHOOK_BASE_URL}/webhook/slack
   ```

3. **Configure your bot token in .env:**
   ```bash
   SLACK_BOT_TOKEN=xoxb-your-slack-bot-token-here
   ```

4. **Configure your Slack app to send messages to this endpoint**

### Discord Integration

1. **Create a Discord application and get your bot token from the Bot section**

2. **Set up webhook in Discord:**
   ```
   ${WEBHOOK_BASE_URL}/webhook/discord
   ```

3. **Configure your bot token in .env:**
   ```bash
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   ```

4. **Configure your Discord bot to send messages to this endpoint**



# Testing the MCP (Model Context Protocol) Adapter

The MCP adapter makes your agent universally accessible by exposing it through a standard protocol.
This guide walks you through testing the MCP adapter step by step.

---

## Step 1: Run the Server

First, start the server:

```bash
python server.py
```

You should see output similar to:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## Step 2: Check the MCP Manifest

The **manifest** describes your agent's capabilities to any MCP client.

Run:

```bash
curl http://localhost:8000/mcp/manifest
```

Example response:

```json
{
  "protocolVersion": "2024-11-05",
  "capabilities": { "tools": {}, "resources": {} },
  "serverInfo": {
    "name": "example-agent-mcp",
    "version": "0.1.0",
    "description": "MCP adapter for example-agent agent"
  },
  "tools": [
    {
      "name": "chat",
      "description": "Chat with the example-agent agent. A simple example agent using OpenAI and LangChain",
      "inputSchema": {
        "type": "object",
        "properties": {
          "message": {
            "type": "string",
            "description": "The input message to the agent",
            "example": "What time is it?"
          },
          "session_id": {
            "type": "string",
            "description": "Session identifier for conversation continuity",
            "example": "user123_session456"
          }
        },
        "required": ["message"]
      }
    }
  ],
  "resources": [
    {
      "uri": "agent://schema",
      "name": "example-agent Schema",
      "description": "Complete schema for example-agent agent including input/output formats and available tools",
      "mimeType": "application/json"
    },
    {
      "uri": "agent://capabilities",
      "name": "example-agent Capabilities",
      "description": "Available capabilities and tools for example-agent agent",
      "mimeType": "application/json"
    }
  ]
}
```

---

## Step 3: List Available Tools

Use the `/mcp/tools/list` endpoint:

```bash
curl -X POST "http://localhost:8000/mcp/tools/list" \
     -H "Content-Type: application/json" \
     -d '{}'
```

This should return a JSON object listing available tools (e.g., `chat`).

---

## Step 4: Call the Agent via MCP

Interact with your agent by calling the `chat` tool:

```bash
curl -X POST "http://localhost:8000/mcp/tools/call" \
     -H "Content-Type: application/json" \
     -d '{
       "method": "tools/call",
       "params": {
         "name": "chat",
         "arguments": {
           "message": "Hello from an MCP client!",
           "session_id": "mcp-test-session-123"
         }
       }
     }'
```

> **PowerShell:**
> ```powershell
> $body = @{
>   method = "tools/call"
>   params = @{
>     name = "chat"
>     arguments = @{
>       message = "Hello from an MCP client!"
>       session_id = "mcp-test-session-123"
>     }
>   }
> } | ConvertTo-Json -Depth 3
> 
> Invoke-RestMethod -Uri "http://localhost:8000/mcp/tools/call" -Method Post -ContentType "application/json" -Body $body
> ```

Example response:

```json
{
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Hello! I'm an AI assistant. How can I help you today?"
      }
    ],
    "metadata": {
      "session_id": "mcp-test-session-123",
      "tools_used": [],
      "timestamp": "..."
    }
  }
}
```

---

## Step 5: Read Resources

You can query resources exposed by the agent. For example, reading the schema:

```bash
curl -X POST "http://localhost:8000/mcp/resources/read" \
     -H "Content-Type: application/json" \
     -d '{
       "method": "resources/read",
       "params": {
         "uri": "agent://schema"
       }
     }'
```

This returns the agent's complete schema in JSON format.

You can also read the capabilities resource:

```bash
curl -X POST "http://localhost:8000/mcp/resources/read" \
     -H "Content-Type: application/json" \
     -d '{
       "method": "resources/read",
       "params": {
         "uri": "agent://capabilities"
       }
     }'
```

This returns information about the agent's available tools and capabilities.

---

## Understanding the MCP Adapter

The MCP adapter properly exposes your agent's API:

1. **Single `chat` tool**: Uses your agent's actual input schema from `agent.get_schema()["input_schema"]`
2. **No artificial tools**: The agent's internal tools (like `get_weather`, `get_time`) are handled internally by the agent, not exposed as separate MCP tools
3. **Two resources**:
   - `agent://schema`: Complete agent schema
   - `agent://capabilities`: Agent capabilities and available tools

### Benefits

- **Proper MCP compliance**: Follows MCP best practices by exposing actual capabilities
- **Schema accuracy**: Uses the agent's real input/output schemas
- **Cleaner interface**: Single tool that represents the agent's main capability
- **Better resource access**: Provides both schema and capabilities information

---

## ✅ Summary

By following these steps, you have successfully:

1. Started the MCP server
2. Checked the manifest
3. Listed available tools
4. Called the agent via MCP
5. Read exposed resources

This verifies the core functionality of the MCP adapter and ensures your agent is MCP-compliant.



## Advanced Configuration

### Custom Adapter Configuration

```python
from adapters.base_adapter import AdapterConfig
from adapters.mcp_adapter import MCPAdapter
from adapters.webhook_adapter import WebhookAdapter

# Create custom adapter configurations
mcp_config = AdapterConfig(
    name="custom-mcp",
    prefix="custom-mcp",
    enabled=True,
    config={
        "timeout": 60,
        "max_requests_per_minute": 100
    }
)

webhook_config = AdapterConfig(
    name="custom-webhook",
    prefix="custom-webhook",
    enabled=True,
    config={
        "verify_signatures": True,
        "max_payload_size": "10MB"
    }
)
```

### Environment-Specific Configuration

```python
import os
from examples.config_example import DEVELOPMENT_CONFIG, PRODUCTION_CONFIG

# Choose configuration based on environment
if os.getenv("ENVIRONMENT") == "production":
    config = PRODUCTION_CONFIG
else:
    config = DEVELOPMENT_CONFIG

# Use configuration to create agent and adapters
agent = create_agent_from_config(config)
adapter_configs = create_adapter_configs(config)
```

## Monitoring and Debugging

### Health Checks

```bash
# Check server health
curl http://localhost:8000/health

# Check webhook health
curl http://localhost:8000/webhook/health
```

### Logging

The server uses Python's logging module. Set the log level via environment variable:

```bash
export LOG_LEVEL=DEBUG
python server.py
```

### Schema Inspection

```bash
# Get agent schema
curl http://localhost:8000/agent/schema

# Get all manifests
curl http://localhost:8000/manifests
```

## Troubleshooting

### Common Issues

1. **Agent not initialized:**
   - Check that your OpenAI API key is set
   - Verify the agent's `initialize()` method is working

2. **Adapter not responding:**
   - Check that the adapter is enabled in configuration
   - Verify the adapter's routes are properly registered

3. **Webhook not receiving messages:**
   - Check that the webhook URL is correctly configured
   - Verify the platform-specific message format

### Debug Mode

Enable debug mode for more detailed logging:

```bash
export DEBUG=True
export LOG_LEVEL=DEBUG
python server.py
```

## Performance Optimization

### Production Settings

```python
# Use production configuration
config = PRODUCTION_CONFIG

# Run with multiple workers
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Caching

Consider implementing caching for frequently used responses:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_response(message: str) -> str:
    # Your caching logic here
    pass
```

## Security Considerations

1. **API Keys:** Store sensitive keys in environment variables
2. **Webhook Verification:** Enable signature verification for webhooks
3. **Rate Limiting:** Implement rate limiting for production use
4. **Input Validation:** Validate all inputs to prevent injection attacks
5. **HTTPS:** Use HTTPS in production environments
