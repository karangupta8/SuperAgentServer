"""
Example LangChain agent implementation.
"""
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
import numexpr

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from .base_agent import AgentRequest, AgentResponse, BaseAgent


class ExampleAgent(BaseAgent):
    """
    Example implementation of a LangChain agent.

    This demonstrates how to wrap a LangChain agent in the BaseAgent interface.
    """

    def __init__(self):
        super().__init__(
            name="example-agent",
            description="An example LangChain agent with OpenAI integration"
        )
        self.llm = None
        self.agent_executor = None

    async def initialize(self) -> None:
        """Initialize the LangChain agent."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")

        # Initialize the LLM
        self.llm = ChatOpenAI(
            model=os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            api_key=api_key
        )

        # Define tools
        @tool
        def get_current_time() -> str:
            """Get the current time."""
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        @tool
        def calculate(expression: str) -> str:
            """Calculate a mathematical expression safely."""
            try:
                # Use numexpr for safe evaluation. It protects against security risks.
                result = numexpr.evaluate(expression).item()
                return str(result)
            except Exception as e:
                return f"Error: {str(e)}"

        tools = [get_current_time, calculate]

        # Create the agent
        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are a helpful assistant. "
                "You have access to the following tools."
            )),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_tools_agent(self.llm, tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True
        )

    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process a request using the LangChain agent."""
        if not self.agent_executor:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        try:
            # Convert our request to LangChain format
            input_data = {
                "input": request.message,
                "chat_history": []  # Could be enhanced with session memory
            }

            # Run the agent
            result = await self.agent_executor.ainvoke(input_data)

            # Extract the response
            output_message = result.get(
                "output", "Sorry, I had trouble processing that."
            )

            return AgentResponse(
                message=output_message,
                session_id=request.session_id,
                metadata={
                    "agent_type": "langchain",
                    "model": os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
                    "tools_available": len(self.agent_executor.tools),
                    "processing_time": datetime.now().isoformat()
                }
            )

        except Exception as e:
            return AgentResponse(
                message=f"Error processing request: {str(e)}",
                session_id=request.session_id,
                metadata={
                    "error": True,
                    "error_type": type(e).__name__,
                    "agent_type": "langchain"
                }
            )

    def get_schema(self) -> Dict[str, Any]:
        """Get the agent's schema definition."""
        return {
            "name": self.name,
            "description": self.description,
            "version": "0.1.0",
            "type": "langchain_agent",
            "input_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The input message to the agent",
                        "example": "What time is it?"
                    },
                    "session_id": {
                        "type": "string",
                        "description": (
                            "Session identifier for conversation continuity"
                        ),
                        "example": "user123_session456"
                    }
                },
                "required": ["message"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The agent's response message",
                        "example": "The current time is 2025-09-13 19:15:30"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Session identifier",
                        "example": "user123_session456"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Response metadata"
                    }
                },
                "required": ["message"]
            },
            "tools": [
                {
                    "name": "get_current_time",
                    "description": "Get the current time",
                    "input_schema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "calculate",
                    "description": "Calculate a mathematical expression safely",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "Mathematical expression to evaluate"
                            }
                        },
                        "required": ["expression"]
                    }
                }
            ]
        }
