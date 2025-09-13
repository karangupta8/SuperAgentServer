"""
Webhook adapter for external integrations (Telegram, Slack, etc.).
"""

from typing import Any, Dict, List, Optional
from fastapi import HTTPException, Request
from pydantic import BaseModel
import json

from .base_adapter import BaseAdapter, AdapterConfig
from agent.base_agent import AgentRequest, AgentResponse


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


class WebhookAdapter(BaseAdapter):
    """
    Webhook adapter for external integrations.
    
    This adapter provides a generic webhook interface that can be used
    with various platforms like Telegram, Slack, Discord, etc.
    """
    
    def _setup_routes(self) -> None:
        """Set up webhook-specific routes."""
        
        @self.router.post("/webhook")
        async def webhook_endpoint(request: WebhookRequest):
            """Main webhook endpoint for receiving messages."""
            return await self._process_request({
                "message": request.message,
                "user_id": request.user_id,
                "session_id": request.session_id,
                "platform": request.platform,
                "metadata": request.metadata or {}
            })
        
        @self.router.post("/webhook/telegram")
        async def telegram_webhook(request: Request):
            """Telegram-specific webhook endpoint."""
            try:
                data = await request.json()
                message_data = self._parse_telegram_message(data)
                return await self._process_request(message_data)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid Telegram webhook: {str(e)}")
        
        @self.router.post("/webhook/slack")
        async def slack_webhook(request: Request):
            """Slack-specific webhook endpoint."""
            try:
                data = await request.json()
                message_data = self._parse_slack_message(data)
                return await self._process_request(message_data)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid Slack webhook: {str(e)}")
        
        @self.router.post("/webhook/discord")
        async def discord_webhook(request: Request):
            """Discord-specific webhook endpoint."""
            try:
                data = await request.json()
                message_data = self._parse_discord_message(data)
                return await self._process_request(message_data)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid Discord webhook: {str(e)}")
        
        @self.router.get("/webhook/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "adapter": "webhook"}
    
    async def _process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook requests."""
        try:
            # Convert to agent request
            agent_request = AgentRequest(
                message=request_data.get("message", ""),
                session_id=request_data.get("session_id"),
                metadata={
                    **(request_data.get("metadata", {})),
                    "user_id": request_data.get("user_id"),
                    "platform": request_data.get("platform")
                }
            )
            
            # Process with agent
            response = await self.agent(agent_request)
            
            # Convert to webhook response
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
            return {
                "message": f"Error processing request: {str(e)}",
                "user_id": request_data.get("user_id"),
                "session_id": request_data.get("session_id"),
                "platform": request_data.get("platform"),
                "metadata": {"error": str(e)}
            }
    
    def _parse_telegram_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Telegram webhook message."""
        message = data.get("message", {})
        text = message.get("text", "")
        user_id = str(message.get("from", {}).get("id", ""))
        chat_id = str(message.get("chat", {}).get("id", ""))
        
        return {
            "message": text,
            "user_id": user_id,
            "session_id": chat_id,
            "platform": "telegram",
            "metadata": {
                "message_id": message.get("message_id"),
                "chat_type": message.get("chat", {}).get("type"),
                "username": message.get("from", {}).get("username")
            }
        }
    
    def _parse_slack_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Slack webhook message."""
        text = data.get("text", "")
        user_id = data.get("user", "")
        channel = data.get("channel", "")
        
        return {
            "message": text,
            "user_id": user_id,
            "session_id": channel,
            "platform": "slack",
            "metadata": {
                "team": data.get("team"),
                "channel_name": data.get("channel_name"),
                "timestamp": data.get("ts")
            }
        }
    
    def _parse_discord_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Discord webhook message."""
        content = data.get("content", "")
        author = data.get("author", {})
        channel_id = data.get("channel_id", "")
        
        return {
            "message": content,
            "user_id": str(author.get("id", "")),
            "session_id": channel_id,
            "platform": "discord",
            "metadata": {
                "username": author.get("username"),
                "guild_id": data.get("guild_id"),
                "message_id": data.get("id")
            }
        }
    
    def get_manifest(self) -> Dict[str, Any]:
        """Get the webhook adapter manifest."""
        schema = self.agent.get_schema()
        
        return {
            "name": f"{self.agent.name}-webhook",
            "version": "0.1.0",
            "description": f"Webhook adapter for {self.agent.name} agent",
            "endpoints": {
                "webhook": {
                    "method": "POST",
                    "path": f"/{self.config.prefix}/webhook",
                    "description": "Generic webhook endpoint"
                },
                "telegram": {
                    "method": "POST",
                    "path": f"/{self.config.prefix}/webhook/telegram",
                    "description": "Telegram webhook endpoint"
                },
                "slack": {
                    "method": "POST",
                    "path": f"/{self.config.prefix}/webhook/slack",
                    "description": "Slack webhook endpoint"
                },
                "discord": {
                    "method": "POST",
                    "path": f"/{self.config.prefix}/webhook/discord",
                    "description": "Discord webhook endpoint"
                },
                "health": {
                    "method": "GET",
                    "path": f"/{self.config.prefix}/webhook/health",
                    "description": "Health check endpoint"
                }
            },
            "request_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to send to the agent"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User identifier"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Session identifier"
                    },
                    "platform": {
                        "type": "string",
                        "description": "Platform identifier"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional metadata"
                    }
                },
                "required": ["message"]
            },
            "response_schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The agent's response"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User identifier"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Session identifier"
                    },
                    "platform": {
                        "type": "string",
                        "description": "Platform identifier"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Response metadata"
                    }
                },
                "required": ["message"]
            }
        }
