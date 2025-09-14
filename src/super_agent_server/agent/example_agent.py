"""
Example LangChain agent implementation.
"""
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from .base_agent import AgentRequest, AgentResponse, BaseAgent

# Load the OpenAI API key from environment variables.
# This is a better practice than passing it in the constructor.
if os.getenv("OPENAI_API_KEY", None) is None:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

class ExampleAgent(BaseAgent):
    """
    Example implementation of a LangChain agent.

    This demonstrates how to wrap a LangChain agent in the BaseAgent interface.
    """

    def __init__(self):
        super().__init__(
            name="example-agent",
            description="A simple example agent using OpenAI and LangChain",
        )
        self.agent_executor: Optional[AgentExecutor] = None
        self.chat_history: Dict[str, List[HumanMessage | AIMessage]] = {}

    async def initialize(self) -> None:
        """Initialize the LangChain agent."""
        try:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

            @tool
            def get_weather(location: str) -> str:
                """Get the current weather for a location."""
                return f"The weather in {location} is sunny and 72°F"

            @tool
            def get_time() -> str:
                """Get the current time."""
                return f"The current time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            tools = [get_weather, get_time]

            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are a helpful assistant. You have access to the following tools.",
                    ),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("user", "{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )

            agent = create_openai_tools_agent(llm, tools, prompt)
            self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            print("ExampleAgent initialized successfully.")
        except Exception as e:
            print(f"Error initializing ExampleAgent: {e!s}")
            self.agent_executor = None

    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process a request using the LangChain agent."""
        if not self.agent_executor:
            return AgentResponse(
                message="Error: Agent not initialized. Please check server logs.",
            )

        session_id = request.session_id or "default_session"
        chat_history = self.chat_history.get(session_id, [])

        try:
            response = await self.agent_executor.ainvoke(
                {"input": request.message, "chat_history": chat_history},
            )
            output_message = response.get("output", "Sorry, I had trouble processing that.")

            # Update chat history
            self.chat_history.setdefault(session_id, []).extend(
                [
                    HumanMessage(content=request.message),
                    AIMessage(content=output_message),
                ]
            )

            return AgentResponse(
                message=output_message,
                session_id=request.session_id,
            )
        except Exception as e:
            print(f"Error processing request for session {session_id}: {e!s}")
            return AgentResponse(
                message=f"Error processing request: {e!s}",
                session_id=request.session_id,
            )

    def get_schema(self) -> Dict[str, Any]:
        """Get the agent's schema for adapter generation."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "The input message to the agent", "example": "What time is it?"},
                    "session_id": {"type": "string", "description": "Session identifier for conversation continuity", "example": "user123_session456"},
                },
                "required": ["message"],
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "The agent's response message", "example": "The current time is 2025-09-13 19:15:30"},
                    "session_id": {"type": "string", "description": "Session identifier", "example": "user123_session456"},
                },
                "required": ["message"],
            },
            "tools": [
                {
                    "name": "get_weather",
                    "description": "Get the current weather for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {"location": {"type": "string", "description": "The location to get weather for"}},
                        "required": ["location"],
                    }
                },
                {
                    "name": "get_time",
                    "description": "Get the current time",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                },
            ],
        }
