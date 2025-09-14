"""
Webhook adapter for external integrations (Telegram, Slack, etc.).
"""

import os
import httpx
import logging
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, Request, APIRouter, Depends
from pydantic import BaseModel
import json
from dotenv import load_dotenv

from ..dependencies import get_agent

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

from ..agent.base_agent import AgentRequest, AgentResponse, BaseAgent


class WebhookRequest(BaseModel):
    """Generic webhook request format."""
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    platform: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class WebhookResponse(BaseModel):
    """Generic webhook response format."""
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    platform: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


router = APIRouter(prefix="/webhook", tags=["Webhook Adapter"])

telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
slack_token = os.getenv("SLACK_BOT_TOKEN")
discord_token = os.getenv("DISCORD_BOT_TOKEN")


async def _process_request(request_data: Dict[str, Any], agent: BaseAgent) -> Dict[str, Any]:
    """Process webhook requests."""
    try:
        agent_request = AgentRequest(
            message=request_data.get("message", ""),
            session_id=request_data.get("session_id"),
            metadata={
                **(request_data.get("metadata", {})),
                "user_id": request_data.get("user_id"),
                "platform": request_data.get("platform")
            }
        )
        response = await agent.process(agent_request)
        return {
            "message": response.message,
            "user_id": request_data.get("user_id"),
            "session_id": response.session_id,
            "platform": request_data.get("platform"),
            "metadata": {
                **(response.metadata or {}),
                "tools_used": response.tools_used,
                "timestamp": response.timestamp.isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error processing webhook request: {e}", exc_info=True)
        return {
            "message": f"Error processing request: {str(e)}",
            "user_id": request_data.get("user_id"),
            "session_id": request_data.get("session_id"),
            "platform": request_data.get("platform"),
            "metadata": {"error": str(e)}
        }


def _parse_telegram_message(data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse Telegram webhook message."""
    message = data.get("message", {})
    text = message.get("text", "")
    user_id = str(message.get("from", {}).get("id", ""))
    chat_id = str(message.get("chat", {}).get("id", ""))
    return {
        "message": text, "user_id": chat_id, "session_id": chat_id, "platform": "telegram",
        "metadata": {
            "message_id": message.get("message_id"), "chat_type": message.get("chat", {}).get("type"),
            "username": message.get("from", {}).get("username"), "user_id": user_id
        }
    }


async def _send_telegram_message(chat_id: str, text: str) -> None:
    """Send message back to Telegram."""
    if not telegram_token:
        logger.warning("Cannot send Telegram message: TELEGRAM_BOT_TOKEN is not configured.")
        return
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            logger.info(f"Successfully sent message to Telegram chat_id: {chat_id}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to send Telegram message to chat_id {chat_id}. Status: {e.response.status_code}, Response: {e.response.text}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while sending Telegram message: {e}", exc_info=True)


@router.post("/")
async def webhook_endpoint(request: WebhookRequest, agent: BaseAgent = Depends(get_agent)):
    """Main webhook endpoint for receiving messages."""
    return await _process_request({
        "message": request.message, "user_id": request.user_id, "session_id": request.session_id,
        "platform": request.platform, "metadata": request.metadata or {}
    }, agent)


@router.post("/telegram")
async def telegram_webhook(request: Request, agent: BaseAgent = Depends(get_agent)):
    """Telegram-specific webhook endpoint."""
    try:
        data = await request.json()
        logger.info(f"Received Telegram webhook: {json.dumps(data, indent=2)}")
        message_data = _parse_telegram_message(data)
        logger.info(f"Parsed Telegram message: {message_data}")
        response = await _process_request(message_data, agent)
        logger.info(f"Agent generated response: {response}")
        if telegram_token and message_data.get("user_id"):
            logger.info(f"Attempting to send reply to Telegram chat_id: {message_data['user_id']}")
            await _send_telegram_message(chat_id=message_data["user_id"], text=response["message"])
        else:
            logger.warning("TELEGRAM_BOT_TOKEN not set or no chat_id found. Cannot send reply.")
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Telegram webhook: {str(e)}")


# Placeholder routes for Slack and Discord for completeness
@router.post("/slack")
async def slack_webhook(request: Request, agent: BaseAgent = Depends(get_agent)):
    """Slack-specific webhook endpoint."""
    raise HTTPException(status_code=501, detail="Slack adapter not fully implemented.")


@router.post("/discord")
async def discord_webhook(request: Request, agent: BaseAgent = Depends(get_agent)):
    """Discord-specific webhook endpoint."""
    raise HTTPException(status_code=501, detail="Discord adapter not fully implemented.")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "adapter": "webhook"}
