# Creating Custom Agents

Learn how to create custom agents and integrate them with LangChain in SuperAgentServer.

## Overview

This guide covers everything you need to know about creating custom agents that work with SuperAgentServer, including:

- Understanding the BaseAgent class
- Integrating with LangChain
- Implementing required methods
- Best practices for agent design
- Advanced patterns and examples

## Table of Contents

1. [Understanding BaseAgent](#understanding-baseagent)
2. [Basic Agent Structure](#basic-agent-structure)
3. [LangChain Integration](#langchain-integration)
4. [Advanced Patterns](#advanced-patterns)
5. [Testing Your Agent](#testing-your-agent)
6. [Deployment](#deployment)
7. [Best Practices](#best-practices)

## Understanding BaseAgent

The `BaseAgent` class is the foundation for all agents in SuperAgentServer. It provides a standardized interface that all adapters can use, regardless of the underlying implementation.

### Key Methods

```python
class BaseAgent(ABC):
    def __init__(self, name: str, description: str = ""):
        # Initialize the agent with a name and description
    
    @abstractmethod
    async def initialize(self) -> None:
        # Initialize the agent (called once before first use)
    
    @abstractmethod
    async def process(self, request: AgentRequest) -> AgentResponse:
        # Process a request and return a response
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        # Return the agent's schema for auto-generation
```

### Request and Response Models

```python
class AgentRequest(BaseModel):
    message: str                    # The input message
    session_id: Optional[str]       # Session identifier
    metadata: Optional[Dict[str, Any]]  # Additional metadata
    tools: Optional[List[str]]      # Available tools

class AgentResponse(BaseModel):
    message: str                    # The agent's response
    session_id: Optional[str]       # Session identifier
    metadata: Optional[Dict[str, Any]]  # Additional metadata
    tools_used: Optional[List[str]] # Tools used in response
    timestamp: datetime             # Response timestamp
```

## Basic Agent Structure

Here's a minimal agent implementation:

```python
"""
Basic Agent Example
"""

import asyncio
from typing import Dict, Any
from super_agent_server.agent import BaseAgent, AgentRequest, AgentResponse


class BasicAgent(BaseAgent):
    """A basic agent that echoes messages."""
    
    def __init__(self):
        super().__init__(
            name="basic-agent",
            description="A simple echo agent"
        )
    
    async def initialize(self) -> None:
        """Initialize the agent."""
        print("Basic Agent initialized!")
        # Add any initialization logic here
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process a request and return a response."""
        # Simple echo logic
        response_message = f"Echo: {request.message}"
        
        return AgentResponse(
            message=response_message,
            session_id=request.session_id,
            metadata={"agent_name": self.name}
        )
    
    def get_schema(self) -> Dict[str, Any]:
        """Return the agent's schema."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Input message"}
                },
                "required": ["message"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Response message"}
                }
            }
        }
```

## LangChain Integration

### Simple LangChain Agent

Here's how to integrate a basic LangChain agent:

```python
"""
LangChain Agent Integration
"""

import os
import asyncio
from typing import Dict, Any, List
from super_agent_server.agent import BaseAgent, AgentRequest, AgentResponse

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI


class LangChainAgent(BaseAgent):
    """A LangChain-powered agent."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        super().__init__(
            name="langchain-agent",
            description="A LangChain-powered conversational agent"
        )
        self.model_name = model_name
        self.temperature = temperature
        self.agent_executor = None
    
    async def initialize(self) -> None:
        """Initialize the LangChain agent."""
        print("Initializing LangChain agent...")
        
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Create the LLM
        llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Define tools
        tools = [self._create_echo_tool()]
        
        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant. Use the available tools when appropriate."),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent
        agent = create_openai_tools_agent(llm, tools, prompt)
        
        # Create the agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True
        )
        
        print("LangChain agent initialized successfully!")
    
    def _create_echo_tool(self):
        """Create a simple echo tool."""
        @tool
        def echo_tool(message: str) -> str:
            """Echo back the input message."""
            return f"Echo: {message}"
        
        return echo_tool
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process a request using the LangChain agent."""
        if not self.agent_executor:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        try:
            # Prepare input for LangChain
            input_data = {
                "input": request.message,
                "chat_history": []  # You can implement chat history here
            }
            
            # Run the agent
            result = await self.agent_executor.ainvoke(input_data)
            
            # Extract the response
            response_message = result.get("output", "I'm sorry, I couldn't process that request.")
            
            return AgentResponse(
                message=response_message,
                session_id=request.session_id,
                metadata={
                    "agent_name": self.name,
                    "model": self.model_name,
                    "tools_used": result.get("intermediate_steps", [])
                }
            )
            
        except Exception as e:
            return AgentResponse(
                message=f"I encountered an error: {str(e)}",
                session_id=request.session_id,
                metadata={
                    "agent_name": self.name,
                    "error": True,
                    "error_message": str(e)
                }
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Return the agent's schema."""
        return {
            "name": self.name,
            "description": self.description,
            "model": self.model_name,
            "tools": ["echo_tool"],
            "input_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The user's message"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Session identifier"
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

### Advanced LangChain Agent with Tools

Here's a more sophisticated example with multiple tools:

```python
"""
Advanced LangChain Agent with Multiple Tools
"""

import os
import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime
from super_agent_server.agent import BaseAgent, AgentRequest, AgentResponse

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI


class AdvancedLangChainAgent(BaseAgent):
    """An advanced LangChain agent with multiple tools."""
    
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.7):
        super().__init__(
            name="advanced-langchain-agent",
            description="An advanced LangChain agent with multiple tools and capabilities"
        )
        self.model_name = model_name
        self.temperature = temperature
        self.agent_executor = None
        self.conversation_history = {}
    
    async def initialize(self) -> None:
        """Initialize the advanced LangChain agent."""
        print("Initializing Advanced LangChain agent...")
        
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Create the LLM
        llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Define tools
        tools = [
            self._create_calculator_tool(),
            self._create_time_tool(),
            self._create_weather_tool(),
            self._create_memory_tool()
        ]
        
        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an advanced AI assistant with access to multiple tools. 
            You can perform calculations, tell time, check weather, and remember information.
            Always use the appropriate tool when needed and provide helpful responses."""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent
        agent = create_openai_tools_agent(llm, tools, prompt)
        
        # Create the agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
        
        print("Advanced LangChain agent initialized successfully!")
    
    def _create_calculator_tool(self):
        """Create a calculator tool."""
        @tool
        def calculator(expression: str) -> str:
            """Evaluate a mathematical expression safely."""
            try:
                # Simple safe evaluation (in production, use a proper math parser)
                allowed_chars = set('0123456789+-*/.() ')
                if not all(c in allowed_chars for c in expression):
                    return "Error: Invalid characters in expression"
                
                result = eval(expression)
                return f"Result: {result}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        return calculator
    
    def _create_time_tool(self):
        """Create a time tool."""
        @tool
        def get_current_time() -> str:
            """Get the current date and time."""
            now = datetime.now()
            return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
        
        return get_current_time
    
    def _create_weather_tool(self):
        """Create a weather tool (mock implementation)."""
        @tool
        def get_weather(city: str) -> str:
            """Get weather information for a city (mock data)."""
            # In a real implementation, you would call a weather API
            mock_weather = {
                "New York": "Sunny, 72°F",
                "London": "Cloudy, 65°F",
                "Tokyo": "Rainy, 68°F",
                "Paris": "Partly cloudy, 70°F"
            }
            return mock_weather.get(city, f"Weather data not available for {city}")
        
        return get_weather
    
    def _create_memory_tool(self):
        """Create a memory tool for storing information."""
        @tool
        def store_memory(key: str, value: str) -> str:
            """Store information in memory."""
            # In a real implementation, you would use a proper database
            self.memory = getattr(self, 'memory', {})
            self.memory[key] = value
            return f"Stored: {key} = {value}"
        
        @tool
        def retrieve_memory(key: str) -> str:
            """Retrieve information from memory."""
            self.memory = getattr(self, 'memory', {})
            return self.memory.get(key, f"No memory found for key: {key}")
        
        return [store_memory, retrieve_memory]
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process a request using the advanced LangChain agent."""
        if not self.agent_executor:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        try:
            # Get conversation history for this session
            session_id = request.session_id or "default"
            chat_history = self.conversation_history.get(session_id, [])
            
            # Prepare input for LangChain
            input_data = {
                "input": request.message,
                "chat_history": chat_history
            }
            
            # Run the agent
            result = await self.agent_executor.ainvoke(input_data)
            
            # Extract the response
            response_message = result.get("output", "I'm sorry, I couldn't process that request.")
            
            # Update conversation history
            chat_history.extend([
                {"role": "user", "content": request.message},
                {"role": "assistant", "content": response_message}
            ])
            self.conversation_history[session_id] = chat_history[-10:]  # Keep last 10 exchanges
            
            # Extract tools used
            tools_used = []
            if "intermediate_steps" in result:
                for step in result["intermediate_steps"]:
                    if step and len(step) > 0:
                        tools_used.append(step[0].tool)
            
            return AgentResponse(
                message=response_message,
                session_id=request.session_id,
                metadata={
                    "agent_name": self.name,
                    "model": self.model_name,
                    "tools_used": tools_used,
                    "conversation_length": len(chat_history)
                }
            )
            
        except Exception as e:
            return AgentResponse(
                message=f"I encountered an error: {str(e)}",
                session_id=request.session_id,
                metadata={
                    "agent_name": self.name,
                    "error": True,
                    "error_message": str(e)
                }
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Return the agent's schema."""
        return {
            "name": self.name,
            "description": self.description,
            "model": self.model_name,
            "tools": [
                "calculator",
                "get_current_time",
                "get_weather",
                "store_memory",
                "retrieve_memory"
            ],
            "capabilities": [
                "Mathematical calculations",
                "Time and date information",
                "Weather information (mock)",
                "Memory storage and retrieval",
                "Conversation history"
            ],
            "input_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The user's message"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Session identifier for conversation history"
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
                        "properties": {
                            "tools_used": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tools used in generating the response"
                            },
                            "conversation_length": {
                                "type": "integer",
                                "description": "Number of exchanges in conversation"
                            }
                        }
                    }
                }
            }
        }
```

## Advanced Patterns

### Agent with Custom Tools

```python
"""
Agent with Custom Tools
"""

from typing import Dict, Any, List
from super_agent_server.agent import BaseAgent, AgentRequest, AgentResponse
from langchain_core.tools import tool


class CustomToolsAgent(BaseAgent):
    """An agent with custom tools for specific use cases."""
    
    def __init__(self):
        super().__init__(
            name="custom-tools-agent",
            description="An agent with custom tools for specific tasks"
        )
        self.agent_executor = None
    
    async def initialize(self) -> None:
        """Initialize the agent with custom tools."""
        # ... initialization code ...
        pass
    
    def _create_database_tool(self):
        """Create a database query tool."""
        @tool
        def query_database(query: str) -> str:
            """Query the database with a SQL query."""
            # In a real implementation, you would connect to a database
            return f"Database query result for: {query}"
        
        return query_database
    
    def _create_api_tool(self):
        """Create an API call tool."""
        @tool
        def call_api(endpoint: str, method: str = "GET") -> str:
            """Call an external API endpoint."""
            # In a real implementation, you would make HTTP requests
            return f"API call to {endpoint} using {method}"
        
        return call_api
    
    # ... rest of the implementation ...
```

### Agent with Memory and Context

```python
"""
Agent with Memory and Context
"""

import json
from typing import Dict, Any, List
from super_agent_server.agent import BaseAgent, AgentRequest, AgentResponse


class MemoryAgent(BaseAgent):
    """An agent with persistent memory and context awareness."""
    
    def __init__(self):
        super().__init__(
            name="memory-agent",
            description="An agent with persistent memory and context"
        )
        self.memory_file = "agent_memory.json"
        self.memory = {}
        self.agent_executor = None
    
    async def initialize(self) -> None:
        """Initialize the agent and load memory."""
        await self._load_memory()
        # ... rest of initialization ...
    
    async def _load_memory(self) -> None:
        """Load memory from file."""
        try:
            with open(self.memory_file, 'r') as f:
                self.memory = json.load(f)
        except FileNotFoundError:
            self.memory = {}
    
    async def _save_memory(self) -> None:
        """Save memory to file."""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process request with memory context."""
        # Add memory context to the request
        memory_context = self.memory.get(request.session_id, {})
        
        # Process with context
        # ... processing logic ...
        
        # Update memory
        if request.session_id:
            self.memory[request.session_id] = {
                **memory_context,
                "last_message": request.message,
                "last_response": response_message
            }
            await self._save_memory()
        
        # ... return response ...
```

## Testing Your Agent

### Unit Tests

```python
"""
Test your custom agent
"""

import pytest
import asyncio
from your_agent import YourCustomAgent
from super_agent_server.agent import AgentRequest


@pytest.mark.asyncio
async def test_agent_initialization():
    """Test agent initialization."""
    agent = YourCustomAgent()
    await agent.initialize()
    assert agent is not None


@pytest.mark.asyncio
async def test_agent_processing():
    """Test agent processing."""
    agent = YourCustomAgent()
    await agent.initialize()
    
    request = AgentRequest(
        message="Hello, test!",
        session_id="test-session"
    )
    
    response = await agent.process(request)
    
    assert response.message is not None
    assert response.session_id == "test-session"


@pytest.mark.asyncio
async def test_agent_schema():
    """Test agent schema."""
    agent = YourCustomAgent()
    schema = agent.get_schema()
    
    assert "name" in schema
    assert "description" in schema
    assert "input_schema" in schema
    assert "output_schema" in schema
```

### Integration Tests

```python
"""
Integration tests with SuperAgentServer
"""

import pytest
from fastapi.testclient import TestClient
from super_agent_server.server import create_app
from your_agent import YourCustomAgent


@pytest.fixture
def client():
    """Create test client with your agent."""
    agent = YourCustomAgent()
    app = create_app(agent)
    with TestClient(app) as client:
        yield client


def test_agent_endpoint(client):
    """Test agent endpoint."""
    response = client.post(
        "/agent/chat",
        json={"message": "Hello, test!"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_agent_schema_endpoint(client):
    """Test agent schema endpoint."""
    response = client.get("/agent/schema")
    
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
```

## Deployment

### Deploy with SuperAgentServer

```python
"""
Deploy your custom agent
"""

import asyncio
import uvicorn
from super_agent_server.server import create_app
from your_agent import YourCustomAgent


async def main():
    """Deploy your custom agent."""
    # Create your agent
    agent = YourCustomAgent()
    
    # Initialize the agent
    await agent.initialize()
    
    # Create the FastAPI app
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

### Docker Deployment

```dockerfile
# Dockerfile for your custom agent
FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your agent code
COPY your_agent.py .
COPY deploy_agent.py .

# Set environment variables
ENV OPENAI_API_KEY=your_key_here

# Run the agent
CMD ["python", "deploy_agent.py"]
```

## Best Practices

### 1. Error Handling

```python
async def process(self, request: AgentRequest) -> AgentResponse:
    """Process request with proper error handling."""
    try:
        # Your agent logic here
        return AgentResponse(message="Success")
    except Exception as e:
        # Log the error
        logger.error(f"Agent error: {e}")
        
        # Return a user-friendly error message
        return AgentResponse(
            message="I'm sorry, I encountered an error processing your request.",
            metadata={"error": True, "error_type": type(e).__name__}
        )
```

### 2. Resource Management

```python
async def initialize(self) -> None:
    """Initialize with proper resource management."""
    try:
        # Initialize resources
        self.llm = ChatOpenAI(...)
        self.tools = self._create_tools()
        # ...
    except Exception as e:
        # Clean up on failure
        await self._cleanup()
        raise e

async def _cleanup(self) -> None:
    """Clean up resources."""
    if hasattr(self, 'llm'):
        # Close connections, etc.
        pass
```

### 3. Configuration

```python
class ConfigurableAgent(BaseAgent):
    """An agent with configuration options."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            name=config.get("name", "configurable-agent"),
            description=config.get("description", "A configurable agent")
        )
        self.config = config
    
    async def initialize(self) -> None:
        """Initialize with configuration."""
        model_name = self.config.get("model_name", "gpt-3.5-turbo")
        temperature = self.config.get("temperature", 0.7)
        # ... use configuration ...
```

### 4. Logging

```python
import logging

logger = logging.getLogger(__name__)

class LoggingAgent(BaseAgent):
    """An agent with proper logging."""
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process with logging."""
        logger.info(f"Processing request: {request.message[:50]}...")
        
        try:
            # Process request
            response = await self._process_internal(request)
            logger.info("Request processed successfully")
            return response
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            raise
```

## Next Steps

Now that you understand how to create custom agents:

1. **[Explore the Example Agent](example-agent.md)** - See a complete implementation
2. **[Learn about Adapters](adapters/README.md)** - Understand how agents are exposed
3. **[Check out Examples](../examples/README.md)** - See real-world implementations
4. **[Read the API Reference](../api/README.md)** - Master all available features

## Troubleshooting

### Common Issues

**Agent not initializing:**
- Check that all required environment variables are set
- Verify that external services (like OpenAI) are accessible
- Check the logs for initialization errors

**Agent not responding:**
- Ensure `initialize()` is called before processing
- Check that the agent is properly registered with the server
- Verify that the request format matches expectations

**Performance issues:**
- Monitor resource usage during processing
- Consider caching expensive operations
- Optimize the agent logic for your use case

**Memory issues:**
- Implement proper cleanup in the `initialize()` method
- Monitor memory usage over time
- Consider using connection pooling for external services

Ready to build your own agent? Start with the [Example Agent](example-agent.md) to see a complete implementation!
