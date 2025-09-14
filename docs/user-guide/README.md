# User Guide

Welcome to the SuperAgentServer User Guide! This section provides comprehensive documentation for using SuperAgentServer effectively.

## Overview

SuperAgentServer is designed to make your LangChain agents universally accessible across multiple protocols and platforms. This guide will help you understand and use all the features effectively.

## Quick Navigation

### 🎯 Getting Started
- **[Configuration](configuration.md)** - Set up and configure SuperAgentServer
- **[Creating Agents](agents/creating-agents.md)** - Build custom agents from scratch
- **[Base Agent](agents/base-agent.md)** - Understand the base agent class
- **[Example Agent](agents/example-agent.md)** - Learn from the example implementation

### 📚 Usage Examples
- **[Basic Usage](../getting-started/quick-start.md)** - Get running in 5 minutes
- **[Your First Agent](../getting-started/first-agent.md)** - Create your first agent
- **[Examples](../examples/README.md)** - See real-world implementations

### 🔌 Adapters
- **[MCP Adapter](adapters/mcp-adapter.md)** - Model Context Protocol integration
- **[Webhook Adapter](adapters/webhook-adapter.md)** - Generic webhook support
- **[A2A Adapter](adapters/a2a-adapter.md)** - Agent-to-Agent communication
- **[ACP Adapter](adapters/acp-adapter.md)** - Agent Communication Protocol

### 🔗 Integrations
- **[Telegram](integrations/telegram.md)** - Telegram bot integration
- **[Slack](integrations/slack.md)** - Slack app integration
- **[Discord](integrations/discord.md)** - Discord bot integration

## Key Concepts

### Agent Architecture

SuperAgentServer follows a simple but powerful architecture:

```
Your LangChain Agent
        ↓
   BaseAgent Wrapper
        ↓
   Adapter Registry
        ↓
┌───────┬─────────┬─────────┬─────────┐
│ REST  │   MCP   │ Webhook │   A2A   │
│  API  │Adapter  │Adapter  │Adapter  │
└───────┴─────────┴─────────┴─────────┘
```

### Core Components

1. **Agents** - Your LangChain agent wrapped in a BaseAgent
2. **Adapters** - Protocol-specific interfaces (REST, MCP, Webhooks, etc.)
3. **Registry** - Manages and routes requests to appropriate adapters
4. **Server** - FastAPI application that serves everything

### Request Flow

1. **Request arrives** at any adapter endpoint
2. **Adapter processes** the request and converts it to standard format
3. **Agent processes** the request using your LangChain logic
4. **Response flows back** through the same adapter
5. **Client receives** response in the expected format

## Common Use Cases

### 1. Multi-Platform Bot

Deploy a single agent across multiple messaging platforms:

```python
# One agent, multiple platforms
agent = MyLangChainAgent()

# Automatically available via:
# - REST API: POST /agent/chat
# - Telegram: POST /webhook/telegram
# - Slack: POST /webhook/slack
# - Discord: POST /webhook/discord
```

### 2. MCP Integration

Expose your agent as an MCP server:

```python
# Your agent becomes an MCP server
# Tools are automatically generated from your agent's schema
# Compatible with MCP clients like Claude Desktop
```

### 3. API-First Development

Build APIs around your agents:

```python
# REST API with automatic OpenAPI docs
# WebSocket support for streaming
# Standardized request/response format
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | - | Yes* |
| `HOST` | Server host | 0.0.0.0 | No |
| `PORT` | Server port | 8000 | No |
| `DEBUG` | Debug mode | True | No |
| `LOG_LEVEL` | Logging level | INFO | No |
| `ALLOWED_ORIGINS` | CORS origins | localhost:3000 | No |

*Required for the example agent, optional for custom agents

### Adapter Configuration

```python
# Enable/disable specific adapters
MCP_ENABLED=True
WEBHOOK_ENABLED=True
A2A_ENABLED=True
ACP_ENABLED=True
```

## Best Practices

### 1. Agent Design

- **Keep agents focused** - One agent, one primary purpose
- **Handle errors gracefully** - Always return valid responses
- **Use sessions** - Maintain conversation context
- **Document your schema** - Help users understand your agent

### 2. Performance

- **Initialize once** - Use the `initialize()` method for setup
- **Cache expensive operations** - Store computed values
- **Use async/await** - Leverage Python's async capabilities
- **Monitor resource usage** - Track memory and CPU usage

### 3. Security

- **Validate inputs** - Always validate incoming data
- **Use environment variables** - Never hardcode secrets
- **Implement rate limiting** - Prevent abuse
- **Log security events** - Monitor for suspicious activity

### 4. Testing

- **Test all adapters** - Ensure each protocol works
- **Mock external services** - Don't rely on external APIs in tests
- **Test error conditions** - Verify error handling
- **Use fixtures** - Reuse test data and setup

## Troubleshooting

### Common Issues

**Agent not responding:**
- Check if `initialize()` was called
- Verify the agent is properly registered
- Check server logs for errors

**Adapter not working:**
- Ensure the adapter is enabled
- Check adapter-specific configuration
- Verify request format matches adapter expectations

**Performance issues:**
- Monitor resource usage
- Check for memory leaks
- Optimize agent logic
- Consider caching strategies

### Debug Mode

Enable debug mode for detailed logging:

```bash
export DEBUG=True
export LOG_LEVEL=DEBUG
python scripts/dev_runner.py
```

### Health Checks

Monitor your deployment:

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/


## Getting Help

- **Documentation** - Check the relevant section in this guide
- **Examples** - See [Examples](../examples/README.md) for working code
- **API Reference** - Consult [API docs](../api/README.md) for technical details
- **GitHub Issues** - Report bugs and request features
- **Community** - Join discussions and get help

## What's Next?

Ready to dive deeper? Here are the next steps:

1. **[Configure your setup](configuration.md)** - Set up your environment
2. **[Create your first agent](agents/creating-agents.md)** - Build a custom agent
3. **[Explore adapters](adapters/README.md)** - Understand different protocols
4. **[Check out examples](../examples/README.md)** - See real implementations
