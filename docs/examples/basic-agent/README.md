# Basic Agent Examples

Simple agent implementations to get you started with SuperAgentServer.

## Overview

These examples demonstrate basic agent patterns and are perfect for learning how to create agents with SuperAgentServer.

## Examples

### 1. Echo Agent

A simple agent that echoes back whatever message it receives.

```python
# examples/basic_echo_agent.py
from super_agent_server.agent import BaseAgent, AgentRequest, AgentResponse

class EchoAgent(BaseAgent):
    def __init__(self):
        super().__init__("echo-agent", "A simple echo agent")
    
    async def initialize(self):
        print("Echo Agent initialized!")
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        return AgentResponse(
            message=f"Echo: {request.message}",
            session_id=request.session_id
        )
    
    def get_schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                },
                "required": ["message"]
            }
        }
```

### 2. Calculator Agent

An agent that performs basic mathematical calculations.

```python
# examples/calculator_agent.py
import re
from super_agent_server.agent import BaseAgent, AgentRequest, AgentResponse

class CalculatorAgent(BaseAgent):
    def __init__(self):
        super().__init__("calculator-agent", "A calculator agent")
    
    async def initialize(self):
        print("Calculator Agent initialized!")
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        try:
            # Simple calculation (in production, use a proper math parser)
            result = eval(request.message)
            response = f"Result: {result}"
        except Exception as e:
            response = f"Error: {str(e)}"
        
        return AgentResponse(
            message=response,
            session_id=request.session_id
        )
    
    def get_schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": ["Basic arithmetic", "Mathematical expressions"],
            "input_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate"
                    }
                },
                "required": ["message"]
            }
        }
```

### 3. Time Agent

An agent that provides current time and date information.

```python
# examples/time_agent.py
from datetime import datetime
from super_agent_server.agent import BaseAgent, AgentRequest, AgentResponse

class TimeAgent(BaseAgent):
    def __init__(self):
        super().__init__("time-agent", "A time and date agent")
    
    async def initialize(self):
        print("Time Agent initialized!")
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        now = datetime.now()
        
        if "time" in request.message.lower():
            response = f"Current time: {now.strftime('%H:%M:%S')}"
        elif "date" in request.message.lower():
            response = f"Current date: {now.strftime('%Y-%m-%d')}"
        else:
            response = f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
        
        return AgentResponse(
            message=response,
            session_id=request.session_id,
            metadata={
                "timestamp": now.isoformat(),
                "timezone": "UTC"
            }
        )
    
    def get_schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": ["Current time", "Current date", "Timezone information"],
            "input_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Time-related query"
                    }
                },
                "required": ["message"]
            }
        }
```

### 4. Weather Agent (Mock)

An agent that provides mock weather information.

```python
# examples/weather_agent.py
import random
from super_agent_server.agent import BaseAgent, AgentRequest, AgentResponse

class WeatherAgent(BaseAgent):
    def __init__(self):
        super().__init__("weather-agent", "A weather information agent")
        self.weather_data = {
            "New York": {"temp": 72, "condition": "Sunny"},
            "London": {"temp": 65, "condition": "Cloudy"},
            "Tokyo": {"temp": 68, "condition": "Rainy"},
            "Paris": {"temp": 70, "condition": "Partly Cloudy"}
        }
    
    async def initialize(self):
        print("Weather Agent initialized!")
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        message = request.message.lower()
        
        # Extract city from message
        city = None
        for city_name in self.weather_data.keys():
            if city_name.lower() in message:
                city = city_name
                break
        
        if city:
            weather = self.weather_data[city]
            response = f"Weather in {city}: {weather['temp']}°F, {weather['condition']}"
        else:
            # Random weather for unknown cities
            temp = random.randint(60, 80)
            conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy"]
            condition = random.choice(conditions)
            response = f"Weather: {temp}°F, {condition}"
        
        return AgentResponse(
            message=response,
            session_id=request.session_id,
            metadata={
                "city": city,
                "temperature": weather.get('temp') if city else temp,
                "condition": weather.get('condition') if city else condition
            }
        )
    
    def get_schema(self):
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": ["Weather information", "Temperature", "Conditions"],
            "supported_cities": list(self.weather_data.keys()),
            "input_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Weather query for a city"
                    }
                },
                "required": ["message"]
            }
        }
```

## Running the Examples

### 1. Run Individual Examples

```bash
# Echo agent
python examples/basic_echo_agent.py

# Calculator agent
python examples/calculator_agent.py

# Time agent
python examples/time_agent.py

# Weather agent
python examples/weather_agent.py
```

### 2. Deploy with SuperAgentServer

```python
# examples/deploy_basic_agent.py
import asyncio
import uvicorn
from super_agent_server.server import create_app
from basic_echo_agent import EchoAgent

async def main():
    agent = EchoAgent()
    await agent.initialize()
    
    app = create_app(agent)
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Test the Deployed Agent

```bash
# Test echo agent
curl -X POST "http://localhost:8000/agent/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, World!"}'

# Test calculator agent
curl -X POST "http://localhost:8000/agent/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "2 + 2"}'

# Test time agent
curl -X POST "http://localhost:8000/agent/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What time is it?"}'

# Test weather agent
curl -X POST "http://localhost:8000/agent/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What is the weather in New York?"}'
```

## Testing the Examples

### Unit Tests

```python
# tests/examples/test_basic_agents.py
import pytest
from examples.basic_echo_agent import EchoAgent
from examples.calculator_agent import CalculatorAgent
from super_agent_server.agent import AgentRequest

@pytest.mark.asyncio
async def test_echo_agent():
    agent = EchoAgent()
    await agent.initialize()
    
    request = AgentRequest(message="Hello!")
    response = await agent.process(request)
    
    assert response.message == "Echo: Hello!"

@pytest.mark.asyncio
async def test_calculator_agent():
    agent = CalculatorAgent()
    await agent.initialize()
    
    request = AgentRequest(message="2 + 2")
    response = await agent.process(request)
    
    assert "4" in response.message
```

### Integration Tests

```python
# tests/examples/test_integration.py
import pytest
from fastapi.testclient import TestClient
from super_agent_server.server import create_app
from examples.basic_echo_agent import EchoAgent

@pytest.fixture
def client():
    agent = EchoAgent()
    app = create_app(agent)
    with TestClient(app) as client:
        yield client

def test_echo_endpoint(client):
    response = client.post(
        "/agent/chat",
        json={"message": "Hello!"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Echo: Hello!"
```

## Customizing Examples

### 1. Add New Capabilities

```python
class EnhancedEchoAgent(BaseAgent):
    def __init__(self):
        super().__init__("enhanced-echo-agent", "An enhanced echo agent")
        self.conversation_count = 0
    
    async def process(self, request: AgentRequest) -> AgentRequest:
        self.conversation_count += 1
        
        if "count" in request.message.lower():
            response = f"Conversation count: {self.conversation_count}"
        else:
            response = f"Echo: {request.message}"
        
        return AgentResponse(
            message=response,
            session_id=request.session_id,
            metadata={"conversation_count": self.conversation_count}
        )
```

### 2. Add Error Handling

```python
class RobustCalculatorAgent(BaseAgent):
    async def process(self, request: AgentRequest) -> AgentResponse:
        try:
            # Validate input
            if not request.message.strip():
                return AgentResponse(
                    message="Error: Empty expression",
                    session_id=request.session_id
                )
            
            # Perform calculation
            result = eval(request.message)
            response = f"Result: {result}"
            
        except ZeroDivisionError:
            response = "Error: Division by zero"
        except SyntaxError:
            response = "Error: Invalid expression"
        except Exception as e:
            response = f"Error: {str(e)}"
        
        return AgentResponse(
            message=response,
            session_id=request.session_id
        )
```

### 3. Add Session Management

```python
class SessionAwareAgent(BaseAgent):
    def __init__(self):
        super().__init__("session-aware-agent", "A session-aware agent")
        self.sessions = {}
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        session_id = request.session_id or "default"
        
        # Initialize session if new
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "message_count": 0,
                "last_message": None
            }
        
        # Update session
        self.sessions[session_id]["message_count"] += 1
        self.sessions[session_id]["last_message"] = request.message
        
        # Generate response
        session_data = self.sessions[session_id]
        response = f"Session {session_id}: Message #{session_data['message_count']} - {request.message}"
        
        return AgentResponse(
            message=response,
            session_id=session_id,
            metadata=session_data
        )
```

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

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

### 2. Input Validation

Validate inputs before processing:

```python
async def process(self, request: AgentRequest) -> AgentResponse:
    if not request.message or not request.message.strip():
        return AgentResponse(
            message="Error: Empty message",
            session_id=request.session_id
        )
    
    # Process valid input
    # ...
```

### 3. Logging

Add logging for debugging:

```python
import logging

logger = logging.getLogger(__name__)

class LoggingAgent(BaseAgent):
    async def process(self, request: AgentRequest) -> AgentResponse:
        logger.info(f"Processing message: {request.message[:50]}...")
        
        try:
            # Your logic here
            response = AgentResponse(message="Success")
            logger.info("Message processed successfully")
            return response
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise
```

## Next Steps

- **[Advanced Agent Examples](advanced-agent/README.md)** - More complex implementations
- **[Integration Examples](integrations/README.md)** - Platform integrations
- **[Creating Custom Agents](../user-guide/agents/creating-agents.md)** - Build your own agents
