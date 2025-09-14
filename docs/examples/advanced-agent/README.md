# Advanced Agent Examples

Complex agent implementations demonstrating advanced patterns and integrations.

## Overview

These examples showcase advanced agent patterns, including LangChain integration, custom tools, memory management, and complex workflows.

## Examples

### 1. LangChain Integration Agent

A comprehensive example showing how to integrate LangChain agents with SuperAgentServer.

```python
# examples/advanced_langchain_agent.py
"""
Advanced LangChain Agent Integration
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from super_agent_server.agent import BaseAgent, AgentRequest, AgentResponse

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI


class AdvancedLangChainAgent(BaseAgent):
    """An advanced LangChain agent with multiple tools and capabilities."""
    
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
            self._create_memory_tool(),
            self._create_file_tool(),
            self._create_web_search_tool()
        ]
        
        # Create the prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an advanced AI assistant with access to multiple tools. 
            You can perform calculations, tell time, check weather, remember information,
            work with files, and search the web.
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
            from datetime import datetime
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
    
    def _create_file_tool(self):
        """Create a file operations tool."""
        @tool
        def read_file(filename: str) -> str:
            """Read contents of a file."""
            try:
                with open(filename, 'r') as f:
                    return f"File contents:\n{f.read()}"
            except FileNotFoundError:
                return f"File not found: {filename}"
            except Exception as e:
                return f"Error reading file: {str(e)}"
        
        @tool
        def write_file(filename: str, content: str) -> str:
            """Write content to a file."""
            try:
                with open(filename, 'w') as f:
                    f.write(content)
                return f"Successfully wrote to {filename}"
            except Exception as e:
                return f"Error writing file: {str(e)}"
        
        return [read_file, write_file]
    
    def _create_web_search_tool(self):
        """Create a web search tool (mock implementation)."""
        @tool
        def web_search(query: str) -> str:
            """Search the web for information (mock implementation)."""
            # In a real implementation, you would use a search API
            mock_results = {
                "python": "Python is a programming language...",
                "ai": "Artificial Intelligence is...",
                "weather": "Weather is the state of the atmosphere..."
            }
            return mock_results.get(query.lower(), f"No results found for: {query}")
        
        return web_search
    
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
                "retrieve_memory",
                "read_file",
                "write_file",
                "web_search"
            ],
            "capabilities": [
                "Mathematical calculations",
                "Time and date information",
                "Weather information (mock)",
                "Memory storage and retrieval",
                "File operations",
                "Web search (mock)",
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


# Example usage
async def main():
    """Example of using the advanced agent."""
    agent = AdvancedLangChainAgent()
    await agent.initialize()
    
    # Test the agent
    request = AgentRequest(
        message="What's 2 + 2, and what time is it?",
        session_id="test-session"
    )
    
    response = await agent.process(request)
    print(f"Response: {response.message}")
    print(f"Tools used: {response.metadata.get('tools_used', [])}")


if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Memory-Enabled Agent

An agent with persistent memory and context awareness.

```python
# examples/memory_agent.py
"""
Memory-Enabled Agent
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from super_agent_server.agent import BaseAgent, AgentRequest, AgentResponse


class MemoryAgent(BaseAgent):
    """An agent with persistent memory and context awareness."""
    
    def __init__(self, memory_file: str = "agent_memory.json"):
        super().__init__(
            name="memory-agent",
            description="An agent with persistent memory and context"
        )
        self.memory_file = memory_file
        self.memory = {}
        self.conversation_contexts = {}
    
    async def initialize(self) -> None:
        """Initialize the agent and load memory."""
        print("Initializing Memory Agent...")
        await self._load_memory()
        print("Memory Agent initialized!")
    
    async def _load_memory(self) -> None:
        """Load memory from file."""
        try:
            with open(self.memory_file, 'r') as f:
                self.memory = json.load(f)
        except FileNotFoundError:
            self.memory = {}
        except Exception as e:
            print(f"Error loading memory: {e}")
            self.memory = {}
    
    async def _save_memory(self) -> None:
        """Save memory to file."""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process request with memory context."""
        session_id = request.session_id or "default"
        
        # Load session context
        if session_id not in self.conversation_contexts:
            self.conversation_contexts[session_id] = {
                "message_count": 0,
                "topics_discussed": [],
                "user_preferences": {}
            }
        
        context = self.conversation_contexts[session_id]
        context["message_count"] += 1
        
        # Process the message
        response_message = await self._process_with_memory(request, context)
        
        # Update context
        context["last_message"] = request.message
        context["last_response"] = response_message
        
        # Save memory
        await self._save_memory()
        
        return AgentResponse(
            message=response_message,
            session_id=session_id,
            metadata={
                "agent_name": self.name,
                "message_count": context["message_count"],
                "topics_discussed": context["topics_discussed"],
                "memory_entries": len(self.memory)
            }
        )
    
    async def _process_with_memory(self, request: AgentRequest, context: Dict[str, Any]) -> str:
        """Process the request using memory context."""
        message = request.message.lower()
        
        # Check for memory-related commands
        if "remember" in message:
            return await self._handle_remember_command(request.message, context)
        elif "recall" in message or "remember" in message:
            return await self._handle_recall_command(request.message, context)
        elif "forget" in message:
            return await self._handle_forget_command(request.message, context)
        elif "what do you know" in message:
            return await self._handle_knowledge_query(context)
        else:
            # Regular conversation with context
            return await self._handle_regular_conversation(request.message, context)
    
    async def _handle_remember_command(self, message: str, context: Dict[str, Any]) -> str:
        """Handle remember commands."""
        # Simple parsing - in production, use NLP
        if "remember that" in message.lower():
            key = f"fact_{len(self.memory)}"
            value = message.replace("remember that", "").strip()
            self.memory[key] = value
            context["topics_discussed"].append("memory_storage")
            return f"I'll remember that: {value}"
        else:
            return "I can remember things if you say 'remember that [information]'"
    
    async def _handle_recall_command(self, message: str, context: Dict[str, Any]) -> str:
        """Handle recall commands."""
        if "recall" in message.lower():
            if self.memory:
                # Return a random memory
                import random
                key, value = random.choice(list(self.memory.items()))
                return f"I remember: {value}"
            else:
                return "I don't have any memories stored yet."
        return "I can recall memories if you ask me to."
    
    async def _handle_forget_command(self, message: str, context: Dict[str, Any]) -> str:
        """Handle forget commands."""
        if "forget everything" in message.lower():
            self.memory.clear()
            context["topics_discussed"].append("memory_clear")
            return "I've forgotten everything."
        else:
            return "I can forget everything if you say 'forget everything'"
    
    async def _handle_knowledge_query(self, context: Dict[str, Any]) -> str:
        """Handle knowledge queries."""
        if self.memory:
            memories = list(self.memory.values())
            return f"I know {len(memories)} things: {', '.join(memories[:3])}{'...' if len(memories) > 3 else ''}"
        else:
            return "I don't have any knowledge stored yet."
    
    async def _handle_regular_conversation(self, message: str, context: Dict[str, Any]) -> str:
        """Handle regular conversation with context."""
        # Simple response based on context
        if context["message_count"] == 1:
            return f"Hello! This is our first conversation. I'll remember our chat."
        elif "hello" in message.lower():
            return f"Hello again! This is message #{context['message_count']} in our conversation."
        elif "how are you" in message.lower():
            return f"I'm doing well! We've exchanged {context['message_count']} messages so far."
        else:
            return f"I understand. This is message #{context['message_count']} in our conversation."
    
    def get_schema(self) -> Dict[str, Any]:
        """Return the agent's schema."""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": [
                "Persistent memory storage",
                "Conversation context",
                "Memory recall",
                "Knowledge management"
            ],
            "memory_features": [
                "Remember facts",
                "Recall information",
                "Forget data",
                "Query knowledge"
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
                        "description": "Session identifier for conversation context"
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
                            "message_count": {
                                "type": "integer",
                                "description": "Number of messages in conversation"
                            },
                            "memory_entries": {
                                "type": "integer",
                                "description": "Number of stored memories"
                            }
                        }
                    }
                }
            }
        }


# Example usage
async def main():
    """Example of using the memory agent."""
    agent = MemoryAgent()
    await agent.initialize()
    
    # Test the agent
    requests = [
        AgentRequest(message="Hello!", session_id="test-session"),
        AgentRequest(message="Remember that I like pizza", session_id="test-session"),
        AgentRequest(message="What do you know about me?", session_id="test-session"),
        AgentRequest(message="Recall something", session_id="test-session")
    ]
    
    for request in requests:
        response = await agent.process(request)
        print(f"User: {request.message}")
        print(f"Agent: {response.message}")
        print(f"Context: {response.metadata}")
        print("---")


if __name__ == "__main__":
    asyncio.run(main())
```

## Running the Examples

### 1. Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
pip install -e .

# Set up environment
cp config/env.example .env
# Edit .env with your OpenAI API key
```

### 2. Run Individual Examples

```bash
# Advanced LangChain agent
python examples/advanced_langchain_agent.py

# Memory agent
python examples/memory_agent.py
```

### 3. Deploy with SuperAgentServer

```python
# examples/deploy_advanced_agent.py
import asyncio
import uvicorn
from super_agent_server.server import create_app
from advanced_langchain_agent import AdvancedLangChainAgent

async def main():
    agent = AdvancedLangChainAgent()
    await agent.initialize()
    
    app = create_app(agent)
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    asyncio.run(main())
```

### 4. Test the Deployed Agent

```bash
# Test advanced agent
curl -X POST "http://localhost:8000/agent/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What is 15 * 23 and what time is it?", "session_id": "test-session"}'

# Test memory agent
curl -X POST "http://localhost:8000/agent/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Remember that I am a software developer", "session_id": "test-session"}'
```

## Testing the Examples

### Unit Tests

```python
# tests/examples/test_advanced_agents.py
import pytest
from examples.advanced_langchain_agent import AdvancedLangChainAgent
from examples.memory_agent import MemoryAgent
from super_agent_server.agent import AgentRequest

@pytest.mark.asyncio
async def test_advanced_langchain_agent():
    agent = AdvancedLangChainAgent()
    await agent.initialize()
    
    request = AgentRequest(message="What is 2 + 2?")
    response = await agent.process(request)
    
    assert "4" in response.message
    assert "calculator" in response.metadata.get("tools_used", [])

@pytest.mark.asyncio
async def test_memory_agent():
    agent = MemoryAgent()
    await agent.initialize()
    
    # Test memory storage
    request = AgentRequest(message="Remember that I like pizza", session_id="test")
    response = await agent.process(request)
    
    assert "remember" in response.message.lower()
    assert response.metadata["message_count"] == 1
```

## Best Practices

### 1. Error Handling

```python
async def process(self, request: AgentRequest) -> AgentResponse:
    try:
        # Your agent logic here
        return AgentResponse(message="Success")
    except Exception as e:
        # Log the error
        logger.error(f"Agent error: {e}")
        
        # Return user-friendly error
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

## Next Steps

- **[Integration Examples](integrations/README.md)** - Platform integrations
- **[Creating Custom Agents](../user-guide/agents/creating-agents.md)** - Build your own agents
- **[API Reference](../api/README.md)** - Master all available features
