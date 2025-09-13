"""
Simple example of creating and using a custom agent.
"""

import asyncio
import os
from agent.base_agent import BaseAgent, AgentRequest, AgentResponse
from agent.example_agent import ExampleAgent
from server import create_app
from fastapi import FastAPI


class SimpleChatAgent(BaseAgent):
    """A simple chat agent that echoes messages with some processing."""
    
    def __init__(self):
        super().__init__(
            name="simple-chat",
            description="A simple chat agent that processes messages"
        )
    
    async def initialize(self) -> None:
        """Initialize the simple agent."""
        # No special initialization needed for this simple agent
        pass
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process a simple chat request."""
        message = request.message.lower()
        
        # Simple response logic
        if "hello" in message:
            response = f"Hello! How can I help you today? (Session: {request.session_id or 'new'})"
        elif "weather" in message:
            response = "I don't have access to real-time weather data, but I can help you with other questions!"
        elif "time" in message:
            from datetime import datetime
            response = f"The current time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elif "help" in message:
            response = "I'm a simple chat agent. Try asking about the weather, time, or just say hello!"
        else:
            response = f"You said: '{request.message}'. That's interesting! Tell me more."
        
        return AgentResponse(
            message=response,
            session_id=request.session_id,
            metadata={
                "processed_at": "simple_agent",
                "input_length": len(request.message)
            }
        )
    
    def get_schema(self) -> dict:
        """Get the agent's schema."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to send to the agent"
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
                        "description": "Response metadata"
                    }
                },
                "required": ["message"]
            }
        }


async def main():
    """Example usage of the simple agent."""
    # Create the simple agent
    agent = SimpleChatAgent()
    await agent.initialize()
    
    # Test the agent directly
    print("Testing Simple Agent:")
    print("=" * 50)
    
    test_messages = [
        "Hello!",
        "What's the weather like?",
        "What time is it?",
        "Help me understand this",
        "Tell me about yourself"
    ]
    
    for message in test_messages:
        request = AgentRequest(message=message, session_id="test-session")
        response = await agent(request)
        print(f"User: {message}")
        print(f"Agent: {response.message}")
        print(f"Metadata: {response.metadata}")
        print("-" * 30)
    
    # Create FastAPI app with the agent
    app = create_app(agent)
    
    print("\nFastAPI app created with Simple Agent")
    print("Run with: uvicorn examples.simple_agent:app --reload")
    print("Available endpoints:")
    print("- GET / - Server info")
    print("- POST /agent/chat - Chat with agent")
    print("- GET /agent/schema - Agent schema")
    print("- POST /webhook/webhook - Webhook endpoint")
    print("- GET /mcp/manifest - MCP manifest")


if __name__ == "__main__":
    asyncio.run(main())
