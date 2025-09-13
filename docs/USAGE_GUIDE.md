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

# Call a tool
curl -X POST "http://localhost:8000/mcp/tools/call" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "agent_chat",
       "arguments": {
         "message": "What is the weather like?",
         "session_id": "session123"
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

### MCP Client Integration

```python
import httpx

async def call_agent_via_mcp(message: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/mcp/tools/call",
            json={
                "name": "agent_chat",
                "arguments": {
                    "message": message,
                    "session_id": "my-session"
                }
            }
        )
        return response.json()

# Usage
result = await call_agent_via_mcp("Hello!")
print(result["result"]["content"][0]["text"])
```

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

## Summary of Changes:

### 1. **Updated `env.example`:**
- Added `TELEGRAM_BOT_TOKEN` for Telegram bot authentication
- Added `SLACK_BOT_TOKEN` for Slack bot authentication  
- Added `DISCORD_BOT_TOKEN` for Discord bot authentication
- Added `WEBHOOK_BASE_URL` for configurable webhook URLs

### 2. **Enhanced `adapters/webhook_adapter.py`:**
- Added bot token initialization in constructor
- Added `_send_telegram_message()` method to send responses back to Telegram
- Added `_send_slack_message()` method to send responses back to Slack
- Added `_send_discord_message()` method to send responses back to Discord
- Modified webhook endpoints to automatically send responses back to users
- Updated message parsing to use correct IDs for sending responses

### 3. **Updated `docs/USAGE_GUIDE.md`:**
- Added instructions for getting bot tokens from each platform
- Added `.env` configuration steps for each platform
- Updated webhook setup instructions to use environment variables

## How it works now:

1. **Developer sets up bot tokens** in their `.env` file
2. **Webhook receives message** from platform (Telegram/Slack/Discord)
3. **Agent processes the message** and generates a response
4. **Webhook automatically sends the response back** to the user on the same platform
5. **User receives the response** directly in their chat

The bot will now have full two-way communication with users on all supported platforms!
