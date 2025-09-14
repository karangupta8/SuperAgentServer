# 🚀 SuperAgentServer

**Universal Agent Adapter Layer for LangChain agents**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)


> **Solve the fragmentation in today's agentic ecosystem** by making one agent definition **universally accessible** through standardized adapters.

## 🎯 What is SuperAgentServer?

SuperAgentServer is a **single package/framework** that takes any **LangChain agent** and automatically exposes it across multiple integration surfaces (APIs, protocols, platforms). Instead of building separate integrations for each platform, you define your agent once and get universal access through:

- 🌐 **REST APIs** (via LangServe)
- 🔌 **MCP** (Model Context Protocol)
- 🔗 **Webhooks** (Telegram, Slack, Discord, etc.)
- 🤖 **A2A** (Agent-to-Agent)
- 📡 **ACP** (Agent Communication Protocol)

## ✨ Key Features

- **🔄 Universal Adapters**: One agent, multiple protocols
- **⚡ Auto-Schema Generation**: Automatically generates manifests for all adapters
- **🛠️ Easy Integration**: Simple LangChain agent → Universal access
- **🔧 Extensible**: Add new adapters easily
- **📚 Well Documented**: Comprehensive docs and examples
- **🚀 Production Ready**: Built with FastAPI and async support

## 🏗️ Architecture

```
Agent Logic (LangChain, base_agent)
        │
        ▼
 Adapter Registry
        │
  ┌─────┼─────────────┬────────────┬─────────────┐─────────────┐
  ▼     ▼             ▼            ▼             ▼             ▼
LangServe   MCP Adapter   A2A Adapter   ACP Adapter   Webhook Adapter
(REST/WS)   (/mcp/*)      (/a2a/*)      (/acp/*)      (/webhook/*)
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/superagentserver/super-agent-server.git
cd super-agent-server

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

1. **Set up environment:**
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key
   ```

2. **Run the server:**
   ```bash
   python run.py
   ```

3. **Test the agent:**
   ```bash
   curl -X POST "http://localhost:8000/agent/chat" \
        -H "Content-Type: application/json" \
        -d '{"message": "Hello, how are you?"}'
   ```

> **Note for Windows Users:** If you are using PowerShell, `curl` is an alias for `Invoke-WebRequest` which has a different syntax. Use this command instead:
> ```powershell
> Invoke-WebRequest -Uri "http://localhost:8000/agent/chat" `
>   -Method POST `
>   -Headers @{"Content-Type"="application/json"} `
>   -Body '{"message": "Hello, how are you?"}'
> ```

## 📖 Usage Examples

### Direct Agent Chat

```bash
curl -X POST "http://localhost:8000/agent/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What is the weather like?",
       "session_id": "user123"
     }'
```

> **PowerShell:**
> ```powershell
> Invoke-WebRequest -Uri "http://localhost:8000/agent/chat" `
>   -Method POST `
>   -Headers @{"Content-Type"="application/json"} `
>   -Body '{"message": "What is the weather like?", "session_id": "user123"}'
```

### MCP Integration

```bash
# List available tools
curl -X POST "http://localhost:8000/mcp/tools/list"

# Call a tool
curl -X POST "http://localhost:8000/mcp/tools/call" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "agent_chat",
       "arguments": {
         "message": "Hello from MCP!",
         "session_id": "mcp-session"
       }
     }'
```

> **PowerShell:**
> ```powershell
> # List available tools
> Invoke-WebRequest -Uri "http://localhost:8000/mcp/tools/list" -Method POST
>
> # Call a tool
> $body = @{
>   name = "agent_chat"
>   arguments = @{ message = "Hello from MCP!"; session_id = "mcp-session" }
> } | ConvertTo-Json
> Invoke-WebRequest -Uri "http://localhost:8000/mcp/tools/call" -Method POST -Headers @{"Content-Type"="application/json"} -Body $body
> ```

### Webhook Integration

```bash
# Generic webhook
curl -X POST "http://localhost:8000/webhook/webhook" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Hello from webhook!",
       "user_id": "user123",
       "platform": "custom"
     }'

# Telegram webhook
curl -X POST "http://localhost:8000/webhook/telegram" \
     -H "Content-Type: application/json" \
     -d '{
       "message": {
         "text": "Hello from Telegram!",
         "from": {"id": 123456789},
         "chat": {"id": 123456789}
       }
     }'
```

> **PowerShell:**
> ```powershell
> # Generic webhook
> $body1 = @{ message = "Hello from webhook!"; user_id = "user123"; platform = "custom" } | ConvertTo-Json
> Invoke-WebRequest -Uri "http://localhost:8000/webhook/webhook" -Method POST -Headers @{"Content-Type"="application/json"} -Body $body1
>
> # Telegram webhook
> $body2 = @{
>   message = @{
>     text = "Hello from Telegram!"
>     from = @{ id = 123456789 }
>     chat = @{ id = 123456789 }
>   }
> } | ConvertTo-Json
> Invoke-WebRequest -Uri "http://localhost:8000/webhook/telegram" -Method POST -Headers @{"Content-Type"="application/json"} -Body $body2
```

## 🛠️ Creating Custom Agents

```python
from agent.base_agent import BaseAgent, AgentRequest, AgentResponse

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("my-agent", "My custom agent")
    
    async def initialize(self):
        # Initialize your LangChain agent
        pass
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        # Your agent logic here
        response = f"Echo: {request.message}"
        return AgentResponse(message=response)
    
    def get_schema(self):
        # Define your agent's schema
        return {...}

# Use with FastAPI
from server import create_app
app = create_app(MyCustomAgent())
```

## 📚 Documentation

- **[📖 Usage Guide](docs/USAGE_GUIDE.md)** - Complete usage instructions
- **[🔧 API Reference](docs/API_REFERENCE.md)** - Detailed API documentation
- **[📋 Examples](examples/)** - Code examples and configurations

## 🌐 Available Adapters

### ✅ Implemented

- **🌐 REST API** - Direct HTTP access via LangServe
- **🔌 MCP** - Model Context Protocol integration
- **🔗 Webhooks** - Generic webhook for external platforms

### 🚧 Coming Soon

- **🤖 A2A** - Agent-to-Agent communication protocol
- **📡 ACP** - Agent Communication Protocol


## 🔧 Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS="http://localhost:3000,https://your-frontend.com"
DEBUG=True
LOG_LEVEL=INFO
```

### Adapter Configuration

```python
from adapters.base_adapter import AdapterConfig

# MCP Adapter
mcp_config = AdapterConfig(
    name="mcp",
    prefix="mcp",
    enabled=True,
    config={"timeout": 30}
)

# Webhook Adapter
webhook_config = AdapterConfig(
    name="webhook",
    prefix="webhook",
    enabled=True,
    config={"verify_signatures": True}
)
```

## 🚀 Deployment

### Development

```bash
python server.py
```

### Production

```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) for the amazing agent framework
- [FastAPI](https://github.com/tiangolo/fastapi) for the excellent web framework
- [LangServe](https://github.com/langchain-ai/langserve) for the REST API foundation
