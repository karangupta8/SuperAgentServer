"""
Webhook Adapter for receiving messages from various platforms.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from super_agent_server.agent.base_agent import AgentRequest, BaseAgent
from super_agent_server.dependencies import get_agent

router = APIRouter(prefix="/webhook", tags=["Webhook"])


class GenericWebhookPayload(BaseModel):
    message: str
    user_id: str
    platform: str


@router.post("/")
async def generic_webhook(payload: GenericWebhookPayload, agent: BaseAgent = Depends(get_agent)):
    """Generic webhook endpoint."""
    request = AgentRequest(
        message=payload.message,
        session_id=f"{payload.platform}-{payload.user_id}",
        metadata={"source_protocol": "webhook", "user_id": payload.user_id, "platform": payload.platform},
    )
    return await agent.process(request)


@router.post("/telegram")
async def telegram_webhook(request: Request, agent: BaseAgent = Depends(get_agent)):
    """Telegram-specific webhook endpoint."""
    data = await request.json()
    message = data.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")

    if not text or not chat_id:
        raise HTTPException(status_code=400, detail="Invalid Telegram payload")

    agent_request = AgentRequest(
        message=text,
        session_id=f"telegram-{chat_id}",
        metadata={"source_protocol": "webhook", "platform": "telegram", "chat_id": chat_id},
    )
    return await agent.process(agent_request)


async def get_manifest(agent: BaseAgent):
    """Generate the manifest for the webhook adapter."""
    return {
        "name": "Webhook Adapter",
        "description": "Allows the agent to receive messages via HTTP webhooks from various platforms.",
        "endpoints": [
            {"path": "/webhook/", "description": "Generic webhook endpoint."},
            {"path": "/webhook/telegram", "description": "Telegram-specific webhook."},
        ],
    }