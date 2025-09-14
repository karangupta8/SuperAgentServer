# Quick Start Guide

Get SuperAgentServer running in 5 minutes!

## Prerequisites

- SuperAgentServer installed (see [Installation Guide](installation.md))
- OpenAI API key

## Step 1: Set Up Environment

1. **Copy the environment template:**
   ```bash
   cp config/env.example .env
   ```

2. **Add your OpenAI API key:**
   ```bash
   # Edit .env file
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Step 2: Start the Server

**Option A: Using the development runner:**
```bash
python scripts/dev_runner.py
```

**Option B: Using uvicorn directly:**
```bash
uvicorn src.super_agent_server.server:app --host 0.0.0.0 --port 8000 --reload
```

**Option C: Using the module:**
```bash
python -m super_agent_server.server
```

## Step 3: Verify the Server

1. **Check server status:**
   ```bash
   curl http://localhost:8000/
   ```

   Expected response:
   ```json
   {
     "name": "SuperAgentServer",
     "version": "0.1.0",
     "description": "Universal Agent Adapter Layer for LangChain agents",
     "status": "running",
     "adapters": ["mcp", "webhook", "a2a", "acp"]
   }
   ```

2. **Check health:**
   ```bash
   curl http://localhost:8000/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "agent_initialized": true,
     "adapters": 4
   }
   ```

## Step 4: Test the Agent

### Test via REST API

```bash
curl -X POST "http://localhost:8000/agent/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, how are you?"}'
```

**PowerShell (Windows):**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/agent/chat" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"message": "Hello, how are you?"}'
```

### Test via MCP Protocol

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
         "arguments": {"message": "Hello from MCP!"}
       }
     }'
```

### Test via Webhook

```bash
curl -X POST "http://localhost:8000/webhook/webhook" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Hello from webhook!",
       "user_id": "test-user",
       "platform": "test"
     }'
```

## Step 5: Explore the API

1. **Open the interactive API docs:**
   - Navigate to: http://localhost:8000/docs
   - This is an interactive Swagger UI where you can test all endpoints

2. **View alternative docs:**
   - Navigate to: http://localhost:8000/redoc
   - This provides a different view of the API documentation

## Step 6: Test WebSocket (Optional)

If you want to test real-time streaming:

```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/chat/stream"
    async with websockets.connect(uri) as websocket:
        # Send a message
        message = [{"input": {"input": "Hello, stream!", "chat_history": []}}]
        await websocket.send(json.dumps(message))
        
        # Receive response
        response = await websocket.recv()
        print(f"Received: {response}")

# Run the test
asyncio.run(test_websocket())
```

## What's Next?

Congratulations! You now have SuperAgentServer running. Here's what you can do next:

1. **[Create Your First Agent](first-agent.md)** - Learn to build custom agents
2. **[Explore the User Guide](../user-guide/README.md)** - Deep dive into features
3. **[Check out Examples](../examples/README.md)** - See real-world implementations
4. **[Read the API Reference](../api/README.md)** - Understand all available endpoints

## Troubleshooting

### Server won't start

**Check if port 8000 is available:**
```bash
# On Linux/macOS:
lsof -i :8000

# On Windows:
netstat -an | findstr :8000
```

**Solution:** Change the port in your `.env` file:
```bash
PORT=8001
```

### Agent not responding

**Check if OpenAI API key is set:**
```bash
echo $OPENAI_API_KEY
```

**Check server logs for errors:**
```bash
# Look for error messages in the console output
```

### Connection refused

**Ensure the server is running:**
```bash
# Check if the process is running
ps aux | grep uvicorn
```

**Check firewall settings:**
```bash
# On Linux, check if port is open
sudo ufw status
```

## Need Help?

- Check the [Troubleshooting Guide](../reference/troubleshooting.md)
- Visit our [GitHub Issues](https://github.com/superagentserver/super-agent-server/issues)
- Join our community discussions
