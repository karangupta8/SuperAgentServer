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

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/superagentserver/super-agent-server.git
cd super-agent-server

# Configure environment
cp config/env.example .env
# Edit .env and add your OpenAI API key

# Build and run with Docker
docker-compose -f docker/docker-compose.yml up --build
```

### Option 2: Local Installation

```bash
# Clone the repository
git clone https://github.com/superagentserver/super-agent-server.git
cd super-agent-server

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

# Set up environment
cp config/env.example .env
# Edit .env and add your OpenAI API key

# Run the server
python scripts/dev_runner.py
```

### Test the Agent

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
       "method": "tools/call",
       "params": {
         "name": "agent_chat",
         "arguments": {
           "message": "Hello from MCP!",
           "session_id": "mcp-session"
         }
       }
     }'
```

> **PowerShell:**
> ```powershell
> # List available tools
> Invoke-WebRequest -Uri "http://localhost:8000/mcp/tools/list" -Method POST -Body "{}" -Headers @{"Content-Type"="application/json"}
>
> # Call a tool
> $body = @{
>   method = "tools/call"
>   params = @{
>     name = "agent_chat"
>     arguments = @{ message = "Hello from MCP!"; session_id = "mcp-session" }
>   }
> } | ConvertTo-Json -Depth 4
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
from super_agent_server.agent import BaseAgent, AgentRequest, AgentResponse

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
from super_agent_server.server import create_app
app = create_app(MyCustomAgent())
```

## 📚 Documentation

- **[📖 Usage Guide](docs/USAGE_GUIDE.md)** - Complete usage instructions
- **[📖 User Guide](docs/user-guide/README.md)** - Complete usage instructions
- **[🔧 API Reference](docs/api/README.md)** - Detailed API documentation
- **[📋 Examples](docs/examples/README.md)** - Code examples and configurations

## 🌐 Available Adapters

### ✅ Implemented

- **🌐 REST API** - Direct HTTP access
- **🔌 MCP** - Model Context Protocol integration
- **🔗 Webhooks** - Generic webhook for external platforms
- **🤖 A2A** - Agent-to-Agent communication protocol
- **📡 ACP** - Agent Communication Protocol
- **🌐 WebSocket** - Real-time streaming chat


## 🔮 Future Improvements

The current implementation provides a solid foundation with basic HTTP endpoints for testing and development. Future enhancements will focus on building out full protocol specifications and adding enterprise-grade features:

### Protocol Implementation
- **A2A Protocol**: Implement complete discovery mechanisms and secure handshake protocols for agent-to-agent communication
- **ACP Integration**: Integrate with real message brokers like RabbitMQ as outlined in the ACP adapter documentation for robust agent communication
- **Enhanced MCP**: Expand Model Context Protocol support with advanced tool discovery and context management

### Security & Authorization
- **Endpoint Authentication**: Add comprehensive authorization mechanisms for all adapter endpoints
- **API Key Management**: Implement secure API key generation and validation
- **Rate Limiting**: Add configurable rate limiting for production deployments



## 🔍 Comparable Projects

While SuperAgentServer provides a unique universal adapter approach, several projects in the ecosystem offer related functionality:

### **Pydantic AI**
- Provides out-of-the-box A2A and MCP adapters for AI agent integration
- Focuses on type-safe AI development with Pydantic models

### **FuseBase**
- A B2B SaaS platform supporting **Model Context Protocol (MCP)** for AI agent tool integration
- Specializes in data source connectivity rather than multi-protocol agent deployment
- [Wikipedia](https://en.wikipedia.org/wiki/FuseBase)

### **Inference Gateway**
- Open-source middleware unifying multiple LLM providers with **MCP** and **A2A** processing layers
- Supports protocol bypassing via headers but lacks comprehensive platform integrations
- [GitHub](https://github.com/inference-gateway/inference-gateway)

### **AgentMaster**
- Research framework combining **A2A** and **MCP** for multi-agent coordination in complex multimodal tasks
- Focuses on agent coordination and data retrieval rather than developer tooling
- [arXiv](https://arxiv.org/abs/2507.21105)

**SuperAgentServer** distinguishes itself by providing a comprehensive, production-ready solution that unifies multiple protocols and platforms in a single, easy-to-use package for LangChain agents.


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

### Docker (Recommended)

```bash
# Quick start with Makefile
make quickstart

# Or manually:
# Development
docker-compose up --build

# Production
docker-compose -f docker-compose.prod.yml up -d
```

### Local Development

```bash
python scripts/dev_runner.py
```

### Production (Local)

```bash
uvicorn super_agent_server.server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Build

```bash
# Build the image
docker build -t super-agent-server .

# Run the container
docker run -p 8000:8000 --env-file .env super-agent-server
```

For detailed deployment instructions, see the [Deployment Guide](docs/deployment/README.md).

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/development/contributing.md) for details.

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
