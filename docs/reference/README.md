# Reference Documentation

Complete reference documentation for SuperAgentServer.

## Overview

This section provides comprehensive reference documentation for all aspects of SuperAgentServer, including API references, troubleshooting guides, and migration information.

## Quick Navigation

- **[Changelog](changelog.md)** - Version history and changes
- **[Migration Guide](migration-guide.md)** - Upgrade instructions
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## API Reference

### Core Classes

#### BaseAgent

```python
class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, name: str, description: str = ""):
        """Initialize the agent."""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent."""
    
    @abstractmethod
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process a request."""
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get the agent's schema."""
```

#### AgentRequest

```python
class AgentRequest(BaseModel):
    """Standard request format for all agents."""
    
    message: str                    # The input message
    session_id: Optional[str]       # Session identifier
    metadata: Optional[Dict[str, Any]]  # Additional metadata
    tools: Optional[List[str]]      # Available tools
```

#### AgentResponse

```python
class AgentResponse(BaseModel):
    """Standard response format for all agents."""
    
    message: str                    # The agent's response
    session_id: Optional[str]       # Session identifier
    metadata: Optional[Dict[str, Any]]  # Additional metadata
    timestamp: datetime             # Response timestamp (within metadata)
```

### Adapter Classes

#### BaseAdapter

```python
class BaseAdapter(ABC):
    """Abstract base class for all adapters."""
    
    def __init__(self, agent: BaseAgent, config: AdapterConfig):
        """Initialize the adapter."""
    
    @abstractmethod
    def register_with_app(self, app: FastAPI) -> None:
        """Register the adapter with FastAPI app."""
    
    @abstractmethod
    def get_manifest(self) -> Dict[str, Any]:
        """Get the adapter's manifest."""
```

#### AdapterConfig

```python
class AdapterConfig(BaseModel):
    """Configuration for an adapter."""
    
    name: str                       # Adapter name
    prefix: str                     # URL prefix
    enabled: bool = True            # Whether adapter is enabled
    config: Dict[str, Any] = {}     # Adapter-specific config
```

### Server Functions

#### create_app

```python
def create_app(agent_instance: Optional[BaseAgent] = None) -> FastAPI:
    """Create and configure a FastAPI app instance."""
```

#### get_agent

```python
async def get_agent() -> BaseAgent:
    """Dependency to get the initialized agent instance."""
```

## Configuration Reference

### Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `HOST` | str | `0.0.0.0` | Server host address |
| `PORT` | int | `8000` | Server port number |
| `DEBUG` | bool | `True` | Enable debug mode |
| `LOG_LEVEL` | str | `INFO` | Logging level |
| `OPENAI_API_KEY` | str | - | OpenAI API key |
| `MODEL_NAME` | str | `gpt-3.5-turbo` | OpenAI model name |
| `TEMPERATURE` | float | `0.7` | Model temperature |
| `ALLOWED_ORIGINS` | str | `localhost:3000` | CORS allowed origins |
| `MCP_ENABLED` | bool | `True` | Enable MCP adapter |
| `WEBHOOK_ENABLED` | bool | `True` | Enable webhook adapter |
| `A2A_ENABLED` | bool | `True` | Enable A2A adapter |
| `ACP_ENABLED` | bool | `True` | Enable ACP adapter |

### Configuration Classes

#### Settings
```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings."""
    
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    # ... other settings
```

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Server information |
| `GET` | `/health` | Health check |

### Agent Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/agent/chat` | Direct agent chat |
| `GET` | `/agent/schema` | Agent schema |

### MCP Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/mcp/tools/list` | List MCP tools |
| `POST` | `/mcp/tools/call` | Call MCP tool |
| `POST` | `/mcp/resources/list` | List MCP resources |
| `POST` | `/mcp/resources/read` | Read MCP resource |
| `GET` | `/mcp/manifest` | MCP manifest |

### Webhook Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/webhook/` | Generic webhook |
| `POST` | `/webhook/telegram` | Telegram webhook |
| `POST` | `/webhook/slack` | Slack webhook |
| `POST` | `/webhook/discord` | Discord webhook |
| `GET` | `/webhook/health` | Webhook health check |

### WebSocket Endpoints

| Endpoint | Description |
|----------|-------------|
| `/chat/stream` | Streaming chat with agent |

## Error Codes

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

### Error Response Format

```json
{
  "detail": "Error message",
  "status_code": 400,
  "timestamp": "2024-01-15T10:30:00.000000",
  "path": "/api/endpoint"
}
```

## Data Models

### Request Models

#### AgentRequest

```json
{
  "message": "string",
  "session_id": "string (optional)",
  "metadata": {
    "key": "value"
  },
  "tools": ["tool1", "tool2"]
}
```

#### MCPRequest

```json
{
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {
      "param1": "value1"
    }
  }
}
```

#### WebhookRequest

```json
{
  "message": "string",
  "user_id": "string",
  "platform": "string",
  "metadata": {
    "key": "value"
  }
}
```

### Response Models

#### AgentResponse

```json
{
  "message": "string",
  "session_id": "string",
  "metadata": {
    "agent_name": "string",
    "tools_used": ["tool1", "tool2"]
  },
  "tools_used": ["tool1", "tool2"],
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

#### MCPResponse

```json
{
  "result": {
    "content": [
      {
        "type": "text",
        "text": "response text"
      }
    ]
  }
}
```

## WebSocket Protocol

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/chat/stream');
```

### Message Format

#### Client to Server

```json
[{
  "input": {
    "input": "message text",
    "chat_history": []
  }
}]
```

#### Server to Client

```json
{
  "event": "on_chat_model_stream",
  "data": {
    "chunk": {
      "content": "response text"
    }
  }
}
```

### Event Types

- `on_chat_model_start`: Chat model started
- `on_chat_model_stream`: Streaming content
- `on_chat_model_end`: Chat model finished
- `error`: Error occurred

## Logging

### Log Levels

- `DEBUG`: Detailed information
- `INFO`: General information
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

### Log Format

```
2024-01-15 10:30:00 [INFO] super_agent_server: Message
```

### Log Files

- `logs/super_agent_server.log`: Main application log
- `logs/access.log`: HTTP access log
- `logs/error.log`: Error log

## Performance

### Benchmarks

| Metric | Value |
|--------|-------|
| Response Time | < 100ms |
| Throughput | 1000+ req/s |
| Memory Usage | < 512MB |
| CPU Usage | < 50% |

### Optimization Tips

1. **Use async/await** for I/O operations
2. **Cache expensive operations** when possible
3. **Monitor resource usage** regularly
4. **Use connection pooling** for external services
5. **Implement rate limiting** for production

## Security

### Best Practices

1. **Use HTTPS** in production
2. **Validate all inputs** thoroughly
3. **Implement authentication** and authorization
4. **Use environment variables** for secrets
5. **Regular security updates** for dependencies

### Security Headers

```python
# Recommended security headers
{
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000"
}
```

## Monitoring

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/


### Metrics

Key metrics to monitor:

- **Response time**: Average response time
- **Throughput**: Requests per second
- **Error rate**: Percentage of failed requests
- **Memory usage**: RAM consumption
- **CPU usage**: CPU utilization

### Alerting

Set up alerts for:

- High error rates (> 5%)
- Slow response times (> 1s)
- High memory usage (> 80%)
- Service unavailability

## Troubleshooting

### Common Issues

1. **Server won't start**
   - Check port availability
   - Verify Python version
   - Check dependencies

2. **Agent not responding**
   - Verify initialization
   - Check API keys
   - Review logs

3. **Performance issues**
   - Monitor resource usage
   - Check for memory leaks
   - Optimize code

### Debug Commands

```bash
# Check server status
curl http://localhost:8000/health

# View logs
tail -f logs/super_agent_server.log

# Check processes
ps aux | grep super_agent_server

# Check port usage
lsof -i :8000
```

## Migration Guide

### Upgrading Between Versions

1. **Check changelog** for breaking changes
2. **Update dependencies** as needed
3. **Test thoroughly** in staging
4. **Backup data** before upgrading
5. **Deploy to production** during maintenance window

### Version Compatibility

| SuperAgentServer | Python | FastAPI | LangChain |
|------------------|--------|---------|-----------|
| 0.1.0 | 3.8+ | 0.104+ | 0.3+ |
| 0.2.0 | 3.9+ | 0.110+ | 0.4+ |

## Next Steps

- **[Changelog](changelog.md)** - Version history
- **[Migration Guide](migration-guide.md)** - Upgrade instructions
- **[Troubleshooting](troubleshooting.md)** - Common issues
