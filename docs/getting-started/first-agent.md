# Your First Agent

Learn how to create and deploy your first custom agent with SuperAgentServer.

## Overview

In this guide, you'll create a simple echo agent that responds to messages. This will teach you the fundamentals of:

- Creating a custom agent class
- Implementing the required methods
- Deploying the agent
- Testing it across different protocols

## Step 1: Create Your Agent

Create a new file called `my_first_agent.py`:

```python
"""
My First Agent - A simple echo agent example.
"""

import asyncio
from typing import Dict, Any
from super_agent_server.agent import BaseAgent, AgentRequest, AgentResponse


class MyFirstAgent(BaseAgent):
    """A simple echo agent that responds to messages."""
    
    def __init__(self):
        super().__init__(
            name="my-first-agent",
            description="A simple echo agent for learning"
        )
    
    async def initialize(self) -> None:
        """Initialize the agent."""
        print("My First Agent initialized!")
        # No special initialization needed for this simple agent
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process a request and return a response."""
        # Simple echo logic
        response_message = f"Echo: {request.message}"
        
        return AgentResponse(
            message=response_message,
            session_id=request.session_id,
            metadata={
                "agent_name": self.name,
                "original_message": request.message
            }
        )
    
    def get_schema(self) -> Dict[str, Any]:
        """Return the agent's schema."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to echo"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Optional session identifier"
                    }
                },
                "required": ["message"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The echoed response"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Session identifier"
                    }
                }
            }
        }
```

## Step 2: Test Your Agent

Run your agent directly to test it:

```bash
python my_first_agent.py
```

Expected output:
```
My First Agent initialized!
Response: Echo: Hello, World!
```

## Step 3: Deploy with SuperAgentServer

Now let's deploy your agent with SuperAgentServer. Create a file called `deploy_my_agent.py`:

```python
"""
Deploy My First Agent with SuperAgentServer.
"""

import asyncio
import uvicorn
from super_agent_server.server import create_app
from my_first_agent import MyFirstAgent


async def main():
    """Deploy the agent with SuperAgentServer."""
    # Create your agent instance
    agent = MyFirstAgent()
    
    # Initialize the agent
    await agent.initialize()
    
    # Create the FastAPI app with your agent
    app = create_app(agent)
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    asyncio.run(main())
```

## Step 4: Run Your Deployed Agent

```bash
python deploy_my_agent.py
```

You should see output like:
```
INFO:     Started server process
INFO:     Waiting for application startup.
My First Agent initialized!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 5: Test Your Deployed Agent

### Test via REST API

```bash
curl -X POST "http://localhost:8000/agent/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello from REST API!"}'
```

Expected response:
```json
{
  "message": "Echo: Hello from REST API!",
  "session_id": null,
  "metadata": {
    "agent_name": "my-first-agent",
    "original_message": "Hello from REST API!"
  }
}
```

### Test via MCP Protocol

```bash
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

## Step 6: Explore the API Documentation

1. **Open the interactive docs:** http://localhost:8000/docs
2. **Try the endpoints** using the Swagger UI
3. **View the agent schema:** http://localhost:8000/agent/schema

## Step 7: Add More Features

Let's enhance your agent with more functionality:

```python
"""
Enhanced My First Agent with more features.
"""

import asyncio
import random
from typing import Dict, Any, List
from super_agent_server.agent import BaseAgent, AgentRequest, AgentResponse


class EnhancedMyFirstAgent(BaseAgent):
    """An enhanced echo agent with additional features."""
    
    def __init__(self):
        super().__init__(
            name="enhanced-first-agent",
            description="An enhanced echo agent with features"
        )
        self.conversation_history = []
    
    async def initialize(self) -> None:
        """Initialize the agent."""
        print("Enhanced My First Agent initialized!")
        self.conversation_history = []
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process a request and return a response."""
        # Store conversation history
        self.conversation_history.append({
            "user": request.message,
            "session": request.session_id
        })
        
        # Enhanced response logic
        if "hello" in request.message.lower():
            response_message = f"Hello! I'm your enhanced agent. You said: {request.message}"
        elif "history" in request.message.lower():
            response_message = f"I've had {len(self.conversation_history)} conversations with you!"
        elif "random" in request.message.lower():
            random_number = random.randint(1, 100)
            response_message = f"Here's a random number: {random_number}"
        else:
            response_message = f"Enhanced Echo: {request.message}"
        
        return AgentResponse(
            message=response_message,
            session_id=request.session_id,
            metadata={
                "agent_name": self.name,
                "original_message": request.message,
                "conversation_count": len(self.conversation_history),
                "features_used": ["echo", "greeting", "history", "random"]
            }
        )
    
    def get_schema(self) -> Dict[str, Any]:
        """Return the agent's schema."""
        return {
            "name": self.name,
            "description": self.description,
            "features": [
                "Echo messages",
                "Greeting responses",
                "Conversation history",
                "Random number generation"
            ],
            "input_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to process"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Optional session identifier"
                    }
                },
                "required": ["message"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The agent's response"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Session identifier"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional response metadata"
                    }
                }
            }
        }
```

## What You've Learned

Congratulations! You've successfully:

1. ✅ **Created a custom agent** that inherits from `BaseAgent`
2. ✅ **Implemented required methods** (`initialize`, `process`, `get_schema`)
3. ✅ **Deployed the agent** with SuperAgentServer
4. ✅ **Tested across multiple protocols** (REST, MCP, Webhook)
5. ✅ **Enhanced the agent** with additional features

## Next Steps

Now that you understand the basics, you can:

1. **[Learn about LangChain Integration](../user-guide/agents/creating-agents.md)** - Connect real LangChain agents
2. **[Explore Adapters](../user-guide/adapters/README.md)** - Understand different protocol adapters
3. **[Check out Advanced Examples](../examples/advanced-agent/README.md)** - See complex implementations
4. **[Read the Full API Reference](../api/README.md)** - Master all available features

## Common Patterns

### Session Management
```python
# Store session-specific data
if not hasattr(self, 'sessions'):
    self.sessions = {}

session_data = self.sessions.get(request.session_id, {})
# ... process with session data
self.sessions[request.session_id] = session_data
```

### Error Handling
```python
async def process(self, request: AgentRequest) -> AgentResponse:
    try:
        # Your agent logic here
        return AgentResponse(message="Success")
    except Exception as e:
        return AgentResponse(
            message=f"Error: {str(e)}",
            metadata={"error": True, "error_type": type(e).__name__}
        )
```

### Tool Integration
```python
def get_schema(self) -> Dict[str, Any]:
    return {
        "tools": [
            {
                "name": "my_tool",
                "description": "A custom tool",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string"}
                    }
                }
            }
        ]
    }
```

## Troubleshooting

### Agent not responding
- Check that `initialize()` is called
- Verify the agent is properly registered
- Check server logs for errors

### Schema issues
- Ensure `get_schema()` returns a valid dictionary
- Check that required fields are included
- Validate JSON schema format

### Session problems
- Verify session_id is being passed correctly
- Check session storage implementation
- Ensure session cleanup logic

Ready to build more complex agents? Check out the [Creating Agents Guide](../user-guide/agents/creating-agents.md)!
