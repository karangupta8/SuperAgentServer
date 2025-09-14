# Examples

Real-world examples and implementations of SuperAgentServer.

## Overview

This section provides practical examples of SuperAgentServer in action, from simple use cases to complex integrations.

## Quick Navigation

- **[Basic Agent](basic-agent/README.md)** - Simple agent implementations
- **[Advanced Agent](advanced-agent/README.md)** - Complex agent examples
- **[Integrations](integrations/README.md)** - Platform integrations

## Example Categories

### 1. Basic Examples
- **Echo Agent** - Simple message echoing
- **Calculator Agent** - Mathematical operations
- **Time Agent** - Date and time information
- **Weather Agent** - Weather information (mock)

### 2. Advanced Examples
- **Multi-Tool Agent** - Agent with multiple tools
- **Memory Agent** - Agent with persistent memory
- **Context Agent** - Agent with conversation context
- **Custom Tools Agent** - Agent with custom tools

### 3. Integration Examples
- **Telegram Bot** - Telegram integration
- **Slack Bot** - Slack app integration
- **Discord Bot** - Discord bot integration
- **Web Interface** - Web-based chat interface

## Getting Started with Examples

### 1. Clone the Repository

```bash
git clone https://github.com/superagentserver/super-agent-server.git
cd super-agent-server
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

### 3. Set Up Environment

```bash
cp config/env.example .env
# Edit .env with your API keys
```

### 4. Run an Example

```bash
# Run a basic example
python examples/basic_echo_agent.py

# Run an advanced example
python examples/advanced_multi_tool_agent.py

# Run an integration example
python examples/telegram_bot.py
```

## Example Structure

Each example follows this structure:

```
examples/
├── basic_echo_agent.py          # Simple echo agent
├── calculator_agent.py          # Calculator agent
├── weather_agent.py             # Weather agent
├── advanced_multi_tool_agent.py # Advanced agent
├── memory_agent.py              # Memory-enabled agent
├── telegram_bot.py              # Telegram integration
├── slack_bot.py                 # Slack integration
├── discord_bot.py               # Discord integration
└── web_interface.py             # Web interface
```

## Running Examples

### Basic Examples

```bash
# Echo agent
python examples/basic_echo_agent.py

# Calculator agent
python examples/calculator_agent.py

# Weather agent
python examples/weather_agent.py
```

### Advanced Examples

```bash
# Multi-tool agent
python examples/advanced_multi_tool_agent.py

# Memory agent
python examples/memory_agent.py
```

### Integration Examples

```bash
# Telegram bot
python examples/telegram_bot.py

# Slack bot
python examples/slack_bot.py

# Discord bot
python examples/discord_bot.py
```

## Testing Examples

### Unit Tests

```bash
# Run all example tests
pytest tests/examples/

# Run specific example tests
pytest tests/examples/test_basic_agents.py
```

### Integration Tests

```bash
# Test with SuperAgentServer
python -m pytest tests/examples/test_integration.py
```

## Customizing Examples

### 1. Modify Agent Behavior

```python
# examples/my_custom_agent.py
from super_agent_server.agent import BaseAgent, AgentRequest, AgentResponse

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("my-custom-agent", "My custom agent")
    
    async def initialize(self):
        # Your initialization logic
        pass
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        # Your custom logic
        return AgentResponse(message="Custom response")
    
    def get_schema(self):
        # Your schema
        return {"name": self.name}
```

### 2. Add Custom Tools

```python
from langchain_core.tools import tool

@tool
def my_custom_tool(input: str) -> str:
    """My custom tool description."""
    return f"Processed: {input}"

# Use in your agent
tools = [my_custom_tool]
```

### 3. Configure Adapters

```python
from super_agent_server.adapters import AdapterConfig

# Custom adapter configuration
webhook_config = AdapterConfig(
    name="webhook",
    prefix="webhook",
    enabled=True,
    config={
        "timeout": 30,
        "max_payload_size": 1024 * 1024
    }
)
```

## Example Use Cases

### 1. Customer Support Bot

```python
# Customer support agent
class CustomerSupportAgent(BaseAgent):
    async def process(self, request: AgentRequest) -> AgentResponse:
        # Analyze customer query
        # Route to appropriate handler
        # Provide helpful response
        pass
```

### 2. Code Review Assistant

```python
# Code review agent
class CodeReviewAgent(BaseAgent):
    async def process(self, request: AgentRequest) -> AgentResponse:
        # Analyze code
        # Provide review comments
        # Suggest improvements
        pass
```

### 3. Data Analysis Assistant

```python
# Data analysis agent
class DataAnalysisAgent(BaseAgent):
    async def process(self, request: AgentRequest) -> AgentResponse:
        # Process data query
        # Generate analysis
        # Return insights
        pass
```

## Best Practices

### 1. Error Handling

```python
async def process(self, request: AgentRequest) -> AgentResponse:
    try:
        # Your logic here
        return AgentResponse(message="Success")
    except Exception as e:
        return AgentResponse(
            message=f"Error: {str(e)}",
            metadata={"error": True}
        )
```

### 2. Logging

```python
import logging

logger = logging.getLogger(__name__)

class LoggingAgent(BaseAgent):
    async def process(self, request: AgentRequest) -> AgentResponse:
        logger.info(f"Processing request: {request.message}")
        # Your logic here
        logger.info("Request processed successfully")
        return response
```

### 3. Configuration

```python
import os

class ConfigurableAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name=os.getenv("AGENT_NAME", "default-agent"),
            description=os.getenv("AGENT_DESCRIPTION", "Default agent")
        )
```

## Contributing Examples

### 1. Create a New Example

```python
# examples/my_new_example.py
"""
My New Example

Description of what this example demonstrates.
"""

from super_agent_server.agent import BaseAgent, AgentRequest, AgentResponse

class MyNewExampleAgent(BaseAgent):
    # Implementation here
    pass

if __name__ == "__main__":
    # Example usage
    pass
```

### 2. Add Tests

```python
# tests/examples/test_my_new_example.py
import pytest
from examples.my_new_example import MyNewExampleAgent

@pytest.mark.asyncio
async def test_my_new_example():
    agent = MyNewExampleAgent()
    await agent.initialize()
    # Test logic here
```

### 3. Update Documentation

```markdown
# docs/examples/my-new-example.md
# My New Example

Description and usage instructions.
```

## Troubleshooting

### Common Issues

**Example won't run:**
- Check Python version (3.8+)
- Install dependencies
- Check environment variables

**Agent not responding:**
- Verify initialization
- Check API keys
- Review logs

**Integration not working:**
- Check platform credentials
- Verify webhook URLs
- Test connectivity

### Getting Help

- Check the [Troubleshooting Guide](../reference/troubleshooting.md)
- Review example code comments
- Search GitHub issues
- Ask in community discussions

## Next Steps

- **[Basic Agent Examples](basic-agent/README.md)** - Start with simple examples
- **[Advanced Agent Examples](advanced-agent/README.md)** - Explore complex implementations
- **[Integration Examples](integrations/README.md)** - Learn platform integrations
- **[Creating Your Own Agent](../user-guide/agents/creating-agents.md)** - Build custom agents
