# Configuration Guide

Learn how to configure SuperAgentServer for your specific needs.

## Overview

SuperAgentServer can be configured through environment variables, configuration files, and programmatic settings. This guide covers all configuration options and best practices.

## Environment Variables

### Core Server Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `HOST` | Server host address | `0.0.0.0` | No |
| `PORT` | Server port number | `8000` | No |
| `DEBUG` | Enable debug mode | `True` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

### OpenAI Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | - | Yes* |
| `MODEL_NAME` | OpenAI model name | `gpt-3.5-turbo` | No |
| `TEMPERATURE` | Model temperature | `0.7` | No |

*Required for the example agent, optional for custom agents

### CORS Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ALLOWED_ORIGINS` | Comma-separated list of allowed origins | `http://localhost:3000,http://127.0.0.1:3000` | No |

### Adapter Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MCP_ENABLED` | Enable MCP adapter | `True` | No |
| `WEBHOOK_ENABLED` | Enable webhook adapter | `True` | No |
| `A2A_ENABLED` | Enable A2A adapter | `True` | No |
| `ACP_ENABLED` | Enable ACP adapter | `True` | No |

### A2A (Agent-to-Agent) Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `A2A_AGENT_ID` | Unique agent identifier | Auto-generated | No |
| `A2A_DISCOVERY_URL` | Discovery service URL | `https://discovery.a2a-protocol.org` | No |
| `A2A_MESSAGE_ROUTING` | Enable message routing | `True` | No |

### ACP (Agent Communication Protocol) Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ACP_AGENT_ID` | Unique agent identifier | Auto-generated | No |
| `ACP_BROKER_URL` | Message broker URL | `amqp://localhost:5672` | No |
| `ACP_SESSION_PERSISTENCE` | Enable session persistence | `True` | No |

### Webhook Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `WEBHOOK_BASE_URL` | Base URL for webhook endpoints | - | No |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | - | No |
| `SLACK_BOT_TOKEN` | Slack bot token | - | No |
| `DISCORD_BOT_TOKEN` | Discord bot token | - | No |

## Configuration Files

### Environment File (.env)

Create a `.env` file in your project root:

```bash
# Core settings
HOST=0.0.0.0
PORT=8000
DEBUG=True
LOG_LEVEL=INFO

# OpenAI settings
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-3.5-turbo
TEMPERATURE=0.7

# CORS settings
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.com

# Adapter settings
MCP_ENABLED=True
WEBHOOK_ENABLED=True
A2A_ENABLED=True
ACP_ENABLED=True

# A2A settings
A2A_AGENT_ID=my-unique-agent-id
A2A_DISCOVERY_URL=https://discovery.a2a-protocol.org
A2A_MESSAGE_ROUTING=True

# ACP settings
ACP_AGENT_ID=my-acp-agent-id
ACP_BROKER_URL=amqp://localhost:5672
ACP_SESSION_PERSISTENCE=True

# Webhook settings
WEBHOOK_BASE_URL=https://your-domain.com
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
DISCORD_BOT_TOKEN=your_discord_bot_token
```

### Logging Configuration (config/logging.yaml)

```yaml
version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
  detailed:
    format: "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
    stream: ext://sys.stdout

  file:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: detailed
    filename: logs/super_agent_server.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

loggers:
  super_agent_server:
    level: DEBUG
    handlers: [console, file]
    propagate: false

  uvicorn:
    level: INFO
    handlers: [console]
    propagate: false

  fastapi:
    level: INFO
    handlers: [console]
    propagate: false

root:
  level: WARNING
  handlers: [console]
```

## Programmatic Configuration

### Using the Settings Class

```python
from super_agent_server.config import Settings

# Create settings instance
settings = Settings()

# Access configuration values
print(f"Server running on {settings.host}:{settings.port}")
print(f"Debug mode: {settings.debug}")
print(f"OpenAI model: {settings.model_name}")
```

### Custom Configuration

```python
from super_agent_server.config import Settings

# Override specific settings
settings = Settings(
    host="127.0.0.1",
    port=9000,
    debug=False,
    log_level="WARNING"
)
```

### Environment-Specific Configuration

```python
import os
from super_agent_server.config import Settings

# Load different configs based on environment
env = os.getenv("ENVIRONMENT", "development")

if env == "production":
    settings = Settings(
        debug=False,
        log_level="WARNING",
        allowed_origins=["https://your-production-domain.com"]
    )
elif env == "staging":
    settings = Settings(
        debug=True,
        log_level="INFO",
        allowed_origins=["https://staging.your-domain.com"]
    )
else:  # development
    settings = Settings(
        debug=True,
        log_level="DEBUG",
        allowed_origins=["http://localhost:3000"]
    )
```

## Adapter Configuration

### MCP Adapter

```python
from super_agent_server.adapters import AdapterConfig

mcp_config = AdapterConfig(
    name="mcp",
    prefix="mcp",
    enabled=True,
    config={
        "timeout": 30,
        "max_retries": 3,
        "enable_tools": True,
        "enable_resources": True
    }
)
```

### Webhook Adapter

```python
webhook_config = AdapterConfig(
    name="webhook",
    prefix="webhook",
    enabled=True,
    config={
        "verify_signatures": True,
        "timeout": 10,
        "max_payload_size": 1024 * 1024,  # 1MB
        "platforms": ["telegram", "slack", "discord"]
    }
)
```

### A2A Adapter

```python
a2a_config = AdapterConfig(
    name="a2a",
    prefix="a2a",
    enabled=True,
    config={
        "agent_id": "my-agent-123",
        "discovery_url": "https://discovery.a2a-protocol.org",
        "message_routing": True,
        "heartbeat_interval": 30
    }
)
```

### ACP Adapter

```python
acp_config = AdapterConfig(
    name="acp",
    prefix="acp",
    enabled=True,
    config={
        "agent_id": "my-acp-agent-123",
        "broker_url": "amqp://localhost:5672",
        "session_persistence": True,
        "queue_name": "agent_messages"
    }
)
```

## Security Configuration

### CORS Settings

```python
# Allow specific origins
ALLOWED_ORIGINS="https://your-frontend.com,https://admin.your-domain.com"

# Allow all origins (NOT recommended for production)
ALLOWED_ORIGINS="*"
```

### API Key Management

```python
# Use environment variables for API keys
import os

openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Never hardcode API keys
# BAD: openai_key = "sk-..."
# GOOD: openai_key = os.getenv("OPENAI_API_KEY")
```

### Rate Limiting

```python
# Configure rate limiting in your adapter
webhook_config = AdapterConfig(
    name="webhook",
    prefix="webhook",
    enabled=True,
    config={
        "rate_limit": {
            "requests_per_minute": 60,
            "burst_size": 10
        }
    }
)
```

## Production Configuration

### Recommended Production Settings

```bash
# Production environment variables
HOST=0.0.0.0
PORT=8000
DEBUG=False
LOG_LEVEL=WARNING

# Security
ALLOWED_ORIGINS=https://your-production-domain.com

# Performance
MCP_ENABLED=True
WEBHOOK_ENABLED=True
A2A_ENABLED=False  # Disable if not needed
ACP_ENABLED=False  # Disable if not needed

# Monitoring
LOG_LEVEL=INFO  # For production monitoring
```

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.9-slim

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DEBUG=False
ENV LOG_LEVEL=INFO

# Copy configuration
COPY config/ /app/config/

# Run the application
CMD ["uvicorn", "super_agent_server.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Configuration

```yaml
# k8s-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: super-agent-server-config
data:
  HOST: "0.0.0.0"
  PORT: "8000"
  DEBUG: "False"
  LOG_LEVEL: "INFO"
  MCP_ENABLED: "True"
  WEBHOOK_ENABLED: "True"
```

## Configuration Validation

### Validate Settings

```python
from super_agent_server.config import Settings
from pydantic import ValidationError

try:
    settings = Settings()
    print("Configuration is valid!")
except ValidationError as e:
    print(f"Configuration error: {e}")
```

### Check Required Variables

```python
import os

required_vars = ["OPENAI_API_KEY"]
missing_vars = []

for var in required_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    raise ValueError(f"Missing required environment variables: {missing_vars}")
```

## Troubleshooting

### Common Configuration Issues

**Issue: Server won't start**
```bash
# Check if port is available
lsof -i :8000

# Check environment variables
env | grep SUPER_AGENT
```

**Issue: CORS errors**
```bash
# Check ALLOWED_ORIGINS setting
echo $ALLOWED_ORIGINS

# Test with curl
curl -H "Origin: http://localhost:3000" http://localhost:8000/
```

**Issue: Adapter not working**
```bash
# Check adapter status
curl http://localhost:8000/adapters

# Check adapter configuration
curl http://localhost:8000/manifests
```

### Debug Configuration

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Print all configuration
from super_agent_server.config import Settings
settings = Settings()
print(settings.dict())
```

## Best Practices

1. **Use environment variables** for sensitive data
2. **Validate configuration** at startup
3. **Use different configs** for different environments
4. **Document your configuration** for your team
5. **Monitor configuration changes** in production
6. **Use configuration management** tools for complex deployments

## Next Steps

- **[Creating Agents](agents/creating-agents.md)** - Learn to build custom agents
- **[Adapter Configuration](adapters/README.md)** - Configure specific adapters
- **[Deployment Guide](../deployment/README.md)** - Deploy your configured server
