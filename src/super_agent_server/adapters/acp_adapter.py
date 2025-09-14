from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from super_agent_server.agent.base_agent import AgentRequest, AgentResponse
from super_agent_server.dependencies import get_agent


class ACPMessage(BaseModel):
    """Represents a message in the ACP protocol for testing purposes."""
    sender_agent_id: str = Field(..., description="The unique ID of the sending agent.")
    message: str = Field(..., description="The content of the message.")
    session_id: Optional[str] = Field(None, description="The session identifier for the conversation.")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Optional metadata about the message.")


# Create a new router for the ACP adapter
router = APIRouter(
    prefix="/acp",
    tags=["ACP Adapter"],
)


@router.post("/message", response_model=AgentResponse)
async def receive_acp_message(
    acp_message: ACPMessage,
    request: Request,
    agent=Depends(get_agent)
):
    """
    Receives a message via the ACP protocol for testing.

    NOTE: This is a simplified HTTP endpoint for testing. A full ACP
    implementation would listen to a message broker (e.g., RabbitMQ).
    """
    # Convert the ACP message to a standard AgentRequest
    agent_request = AgentRequest(
        message=acp_message.message,
        session_id=acp_message.session_id,
        source_protocol="acp",
        metadata={
            "sender_agent_id": acp_message.sender_agent_id,
            **(acp_message.metadata or {})
        }
    )

    # Process the request with the main agent
    try:
        response = await agent.process(agent_request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing error: {str(e)}")