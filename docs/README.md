# SuperAgentServer Documentation

## Overview

SuperAgentServer is a universal adapter layer that exposes LangChain agents across multiple integration surfaces (APIs, protocols, platforms). It solves the fragmentation in today's agentic ecosystem by making one agent definition universally accessible through standardized adapters.

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/superagentserver/super-agent-server.git
cd super-agent-server

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Basic Usage

1. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key
   ```

2. **Run the server:**
   ```bash
   python server.py
   ```

3. **Test the agent:**
   ```bash
   curl -X POST "http://localhost:8000/agent/chat" \
        -H "Content-Type: application/json" \
        -d '{"message": "Hello, how are you?"}'
   ```

## Architecture

```
Agent Logic (LangChain, base_agent)
        │
        ▼
 Adapter Registry
        │
  ┌─────┼─────────────┬────────────┬─────────────┐
  ▼     ▼             ▼            ▼             ▼
LangServe   MCP Adapter   A2A Adapter   ACP Adapter   Webhook Adapter
(REST/WS)   (/mcp/*)      (/a2a/*)      (/acp/*)      (/webhook/*)
```

## Core Components

### 1. Base Agent (`agent/base_agent.py`)

The `BaseAgent` class provides a standardized interface for all agents:

```python
from agent.base_agent import BaseAgent, AgentRequest, AgentResponse

class MyAgent(BaseAgent):
    async def initialize(self):
        # Initialize your agent
        pass
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        # Process the request
        return AgentResponse(message="Hello!")
    
    def get_schema(self):
        # Return agent schema for auto-generation
        return {...}
```

### 2. Adapter System (`adapters/`)

Adapters expose agents through different protocols:

- **MCP Adapter**: Model Context Protocol integration
- **Webhook Adapter**: Generic webhook for external platforms
- **A2A Adapter**: Agent-to-Agent communication (planned)
- **ACP Adapter**: Agent Communication Protocol (planned)

### 3. Schema Auto-Generation (`adapters/schema_generator.py`)

Automatically generates manifests and schemas for all adapters based on the agent's definition.

## API Endpoints

### Core Endpoints

- `GET /` - Server information
- `GET /health` - Health check
- `POST /agent/chat` - Direct agent chat
- `GET /agent/schema` - Agent schema
- `GET /manifests` - All adapter manifests

### MCP Endpoints

- `POST /mcp/tools/list` - List MCP tools
- `POST /mcp/tools/call` - Call MCP tool
- `POST /mcp/resources/list` - List MCP resources
- `POST /mcp/resources/read` - Read MCP resource
- `GET /mcp/manifest` - MCP manifest

### Webhook Endpoints

- `POST /webhook/webhook` - Generic webhook
- `POST /webhook/telegram` - Telegram webhook
- `POST /webhook/slack` - Slack webhook
- `POST /webhook/discord` - Discord webhook
- `GET /webhook/health` - Webhook health check

## Examples

### Custom Agent

```python
from agent.base_agent import BaseAgent, AgentRequest, AgentResponse

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("custom-agent", "My custom agent")
    
    async def initialize(self):
        # Initialize your LangChain agent here
        pass
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        # Process the request
        response_message = f"Echo: {request.message}"
        return AgentResponse(message=response_message)
    
    def get_schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {...},
            "output_schema": {...}
        }
```

### Using with FastAPI

```python
from server import create_app
from my_agent import CustomAgent

# Create your agent
agent = CustomAgent()
await agent.initialize()

# Create FastAPI app
app = create_app(agent)

# Run with uvicorn
# uvicorn my_app:app --reload
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Required for ExampleAgent
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (default: True)
- `LOG_LEVEL`: Logging level (default: INFO)

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

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

### Type Checking

```bash
mypy .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
