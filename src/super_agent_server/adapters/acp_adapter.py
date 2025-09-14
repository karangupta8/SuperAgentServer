"""
ACP (Agent Communication Protocol) Adapter

This adapter allows the agent to communicate over a message broker
like RabbitMQ using a simple RPC (Request-Reply) pattern.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from super_agent_server.agent.base_agent import AgentRequest, BaseAgent
from super_agent_server.dependencies import get_agent


class AcpMessage(BaseModel):
    sender_agent_id: str = Field(..., description="The unique ID of the sending agent.")
    message: str = Field(..., description="The content of the message.")
    session_id: str | None = Field(None, description="An optional session ID for the conversation.")


router = APIRouter(prefix="/acp", tags=["ACP"])


@router.post("/message")
async def acp_message(message: AcpMessage, agent: BaseAgent = Depends(get_agent)):
    """Test endpoint to simulate an incoming ACP message."""
    agent_request = AgentRequest(
        message=message.message,
        session_id=message.session_id,
        metadata={"source_protocol": "acp", "sender_agent_id": message.sender_agent_id},
    )
    response = await agent.process(agent_request)
    return response


async def get_manifest(agent: BaseAgent):
    """Generate the manifest for the ACP adapter."""
    return {
        "name": "ACP Adapter",
        "description": "Allows the agent to communicate over a message broker (e.g., RabbitMQ).",
        "type": "rpc_over_message_broker",
        "broker_type": "AMQP (e.g., RabbitMQ)",
    }