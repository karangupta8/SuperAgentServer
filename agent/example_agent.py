"""
Example LangChain agent implementation.
"""

from typing import Any, Dict, List, Optional
from langchain.llms import OpenAI
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage

from .base_agent import BaseAgent, AgentRequest, AgentResponse


class ExampleAgent(BaseAgent):
    """
    Example implementation of a LangChain agent.
    
    This demonstrates how to wrap a LangChain agent in the BaseAgent interface.
    """
    
    def __init__(self, openai_api_key: str, model_name: str = "gpt-3.5-turbo"):
        super().__init__(
            name="example-agent",
            description="A simple example agent using OpenAI and LangChain"
        )
        self.openai_api_key = openai_api_key
        self.model_name = model_name
        self.llm = None
        self.agent = None
        self.memory = None
    
    async def initialize(self) -> None:
        """Initialize the LangChain agent."""
        # Initialize the LLM
        self.llm = OpenAI(
            openai_api_key=self.openai_api_key,
            model_name=self.model_name,
            temperature=0.7
        )
        
        # Create memory for conversation continuity
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Define some example tools
        def get_weather(location: str) -> str:
            """Get the current weather for a location."""
            return f"The weather in {location} is sunny and 72°F"
        
        def get_time() -> str:
            """Get the current time."""
            from datetime import datetime
            return f"The current time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        tools = [
            Tool(
                name="get_weather",
                description="Get the current weather for a location",
                func=get_weather
            ),
            Tool(
                name="get_time",
                description="Get the current time",
                func=get_time
            )
        ]
        
        # Initialize the agent
        self.agent = initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True
        )
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process a request using the LangChain agent."""
        try:
            # Run the agent
            result = self.agent.run(input=request.message)
            
            # Extract tools used (simplified - in practice you'd parse the agent's execution)
            tools_used = []
            if "get_weather" in request.message.lower():
                tools_used.append("get_weather")
            if "time" in request.message.lower():
                tools_used.append("get_time")
            
            return AgentResponse(
                message=str(result),
                session_id=request.session_id,
                metadata=request.metadata,
                tools_used=tools_used
            )
        except Exception as e:
            return AgentResponse(
                message=f"Error processing request: {str(e)}",
                session_id=request.session_id,
                metadata={"error": str(e)},
                tools_used=[]
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the agent's schema for adapter generation."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The input message to the agent"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Session identifier for conversation continuity"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional metadata"
                    },
                    "tools": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Available tools for the agent to use"
                    }
                },
                "required": ["message"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The agent's response message"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Session identifier"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional response metadata"
                    },
                    "tools_used": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tools used in generating the response"
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Response timestamp"
                    }
                },
                "required": ["message", "timestamp"]
            },
            "tools": [
                {
                    "name": "get_weather",
                    "description": "Get the current weather for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The location to get weather for"
                            }
                        },
                        "required": ["location"]
                    }
                },
                {
                    "name": "get_time",
                    "description": "Get the current time",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }
