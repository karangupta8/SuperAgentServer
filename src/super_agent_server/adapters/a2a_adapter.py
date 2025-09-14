"""
A2A (Agent-to-Agent) Communication Adapter

This adapter allows the agent to communicate with other agents
using the A2A protocol.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from super_agent_server.agent.base_agent import AgentRequest, BaseAgent
from super_agent_server.dependencies import get_agent


class A2AMessage(BaseModel):
    sender_agent_id: str = Field(..., description="The unique ID of the sending agent.")
    message: str = Field(..., description="The content of the message.")
    session_id: str | None = Field(None, description="An optional session ID for the conversation.")


router = APIRouter(prefix="/a2a", tags=["A2A"])


@router.post("/message")
async def a2a_message(message: A2AMessage, agent: BaseAgent = Depends(get_agent)):
    """Test endpoint to simulate an incoming A2A message."""
    agent_request = AgentRequest(
        message=message.message,
        session_id=message.session_id,
        metadata={"source_protocol": "a2a", "sender_agent_id": message.sender_agent_id},
    )
    response = await agent.process(agent_request)
    return response


async def get_manifest(agent: BaseAgent):
    """Generate the A2A protocol card for the agent."""
    agent_schema = agent.get_schema()
    return {
        "version": "1.0",
        "type": "agent_card",
        "agent": {
            "name": agent_schema.get("name"),
            "description": agent_schema.get("description"),
            "version": agent_schema.get("version", "0.1.0"),
            "capabilities": {
                "chat": True,
                "tools": len(agent_schema.get("tools", [])),
                "memory": True,  # Assuming memory is supported
            },
            "endpoints": {"chat": {"url": "/agent/chat", "method": "POST", "schema": agent_schema.get("input_schema")}},
            "tools": agent_schema.get("tools", []),
            "metadata": {"framework": "langchain", "adapter": "super-agent-server"},
        },
    }