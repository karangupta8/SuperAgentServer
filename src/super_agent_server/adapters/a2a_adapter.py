from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from super_agent_server.agent.base_agent import AgentRequest, AgentResponse, BaseAgent
from super_agent_server.dependencies import get_agent


class A2AMessage(BaseModel):
    """Represents a message in the A2A protocol."""
    sender_agent_id: str = Field(..., description="The unique ID of the sending agent.")
    message: str = Field(..., description="The content of the message.")
    session_id: Optional[str] = Field(None, description="The session identifier for the conversation.")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Optional metadata about the message.")


# Create a new router for the A2A adapter
router = APIRouter(
    prefix="/a2a",
    tags=["A2A Adapter"],
)


@router.post("/message", response_model=AgentResponse)
async def receive_a2a_message(
    a2a_message: A2AMessage,
    request: Request,
    agent: BaseAgent = Depends(get_agent)
):
    """
    Receives a message from another agent via the A2A protocol.

    This endpoint is a simplified entry point for testing A2A communication.
    """
    # Convert the A2A message to a standard AgentRequest
    agent_request = AgentRequest(
        message=a2a_message.message,
        session_id=a2a_message.session_id,
        source_protocol="a2a",
        metadata={
            "sender_agent_id": a2a_message.sender_agent_id,
            **(a2a_message.metadata or {})
        }
    )

    # Process the request with the main agent
    try:
        response = await agent.process(agent_request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing error: {str(e)}")