"""
ACP (Agent Communication Protocol) adapter for exposing agents.

The ACP protocol provides a standardized messaging framework for agent interactions,
ensuring interoperability across different platforms and AI systems.
"""

import json
import uuid
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from fastapi import HTTPException, Request
from pydantic import BaseModel, Field

from .base_adapter import BaseAdapter, AdapterConfig
from agent.base_agent import AgentRequest, AgentResponse


class ACPMessage(BaseModel):
    """ACP message format following the standardized protocol."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # request, response, notification, error
    action: str  # chat, tool_call, status, capability
    content: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    source: str  # agent identifier
    destination: Optional[str] = None  # target agent identifier
    correlation_id: Optional[str] = None  # for request-response correlation
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ACPToolCall(BaseModel):
    """ACP tool call definition."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status: str = "pending"  # pending, executing, completed, failed


class ACPCapability(BaseModel):
    """ACP agent capability definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    version: str = "1.0.0"
    category: str = "general"
    tags: List[str] = []


class ACPStatus(BaseModel):
    """ACP agent status definition."""
    agent_id: str
    status: str  # online, offline, busy, error
    capabilities: List[str]
    active_sessions: int
    last_activity: datetime
    metadata: Optional[Dict[str, Any]] = None


class ACPAdapter(BaseAdapter):
    """
    ACP adapter for exposing agents via the Agent Communication Protocol.
    
    This adapter provides a standardized messaging framework for agent interactions,
    ensuring interoperability across different platforms and AI systems.
    """
    
    def __init__(self, agent, config: AdapterConfig):
        super().__init__(agent, config)
        self.agent_id = f"{self.agent.name}-acp-{str(uuid.uuid4())[:8]}"
        self.capabilities: List[ACPCapability] = self._build_capabilities()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.tool_calls: Dict[str, ACPToolCall] = {}
    
    def _setup_routes(self) -> None:
        """Set up ACP-specific routes."""
        
        @self.router.post("/message")
        async def send_message(message: ACPMessage):
            """Send a message using ACP protocol."""
            return await self._process_request({
                "action": "send_message",
                "message": message.dict()
            })
        
        @self.router.post("/message/process")
        async def process_message(request: Request):
            """Process an incoming ACP message."""
            data = await request.json()
            return await self._process_request({
                "action": "process_message",
                "message": data
            })
        
        @self.router.post("/tool/call")
        async def call_tool(tool_call: ACPToolCall):
            """Call a tool using ACP protocol."""
            return await self._process_request({
                "action": "call_tool",
                "tool_call": tool_call.dict()
            })
        
        @self.router.get("/tool/{tool_id}")
        async def get_tool_result(tool_id: str):
            """Get tool call result."""
            return await self._process_request({
                "action": "get_tool_result",
                "tool_id": tool_id
            })
        
        @self.router.get("/capabilities")
        async def list_capabilities():
            """List agent capabilities."""
            return await self._process_request({
                "action": "list_capabilities"
            })
        
        @self.router.get("/status")
        async def get_status():
            """Get agent status."""
            return await self._process_request({
                "action": "get_status"
            })
        
        @self.router.post("/session/start")
        async def start_session(request: Request):
            """Start a new session."""
            data = await request.json()
            return await self._process_request({
                "action": "start_session",
                "session_data": data
            })
        
        @self.router.post("/session/{session_id}/end")
        async def end_session(session_id: str):
            """End a session."""
            return await self._process_request({
                "action": "end_session",
                "session_id": session_id
            })
        
        @self.router.get("/session/{session_id}")
        async def get_session(session_id: str):
            """Get session information."""
            return await self._process_request({
                "action": "get_session",
                "session_id": session_id
            })
        
        @self.router.get("/manifest")
        async def get_manifest():
            """Get the ACP manifest."""
            return self.get_manifest()
    
    async def _process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process ACP requests."""
        action = request_data.get("action")
        
        try:
            if action == "send_message":
                return await self._handle_send_message(request_data)
            elif action == "process_message":
                return await self._handle_process_message(request_data)
            elif action == "call_tool":
                return await self._handle_call_tool(request_data)
            elif action == "get_tool_result":
                return await self._handle_get_tool_result(request_data)
            elif action == "list_capabilities":
                return await self._handle_list_capabilities(request_data)
            elif action == "get_status":
                return await self._handle_get_status(request_data)
            elif action == "start_session":
                return await self._handle_start_session(request_data)
            elif action == "end_session":
                return await self._handle_end_session(request_data)
            elif action == "get_session":
                return await self._handle_get_session(request_data)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
        
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                },
                "timestamp": datetime.now().isoformat()
            }
    
    async def _handle_send_message(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sending a message using ACP protocol."""
        message_data = request_data.get("message", {})
        
        # In a real implementation, this would route the message to the destination
        # For now, we'll just acknowledge the message
        return {
            "success": True,
            "message_id": message_data.get("id"),
            "status": "sent",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_process_message(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle processing an incoming ACP message."""
        message_data = request_data.get("message", {})
        message_type = message_data.get("type")
        action = message_data.get("action")
        
        if message_type == "request" and action == "chat":
            # Process chat request
            content = message_data.get("content", {})
            session_id = message_data.get("session_id")
            
            agent_request = AgentRequest(
                message=content.get("text", ""),
                session_id=session_id,
                metadata={
                    **(message_data.get("metadata", {})),
                    "source": message_data.get("source"),
                    "correlation_id": message_data.get("correlation_id")
                }
            )
            
            response = await self.agent(agent_request)
            
            # Create response message
            response_message = ACPMessage(
                type="response",
                action="chat",
                content={
                    "text": response.message,
                    "tools_used": response.tools_used
                },
                source=self.agent_id,
                destination=message_data.get("source"),
                correlation_id=message_data.get("correlation_id"),
                session_id=response.session_id,
                metadata={
                    "response_metadata": response.metadata,
                    "timestamp": response.timestamp.isoformat()
                }
            )
            
            return {
                "success": True,
                "response": response_message.dict(),
                "timestamp": datetime.now().isoformat()
            }
        
        elif message_type == "notification":
            # Handle notification
            return {
                "success": True,
                "status": "notification_processed",
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            return {
                "success": False,
                "error": {
                    "code": "UNSUPPORTED_MESSAGE_TYPE",
                    "message": f"Unsupported message type: {message_type}"
                },
                "timestamp": datetime.now().isoformat()
            }
    
    async def _handle_call_tool(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call using ACP protocol."""
        tool_data = request_data.get("tool_call", {})
        tool_call = ACPToolCall(**tool_data)
        self.tool_calls[tool_call.id] = tool_call
        
        try:
            # Execute the tool call using the agent
            if tool_call.name == "chat":
                agent_request = AgentRequest(
                    message=tool_call.parameters.get("message", ""),
                    session_id=tool_call.parameters.get("session_id"),
                    metadata={
                        **(tool_call.parameters.get("metadata", {})),
                        "tool_call_id": tool_call.id
                    }
                )
                
                response = await self.agent(agent_request)
                
                tool_call.status = "completed"
                tool_call.result = {
                    "message": response.message,
                    "tools_used": response.tools_used,
                    "metadata": response.metadata
                }
                
                return {
                    "success": True,
                    "tool_call_id": tool_call.id,
                    "status": "completed",
                    "result": tool_call.result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                tool_call.status = "failed"
                tool_call.error = f"Unknown tool: {tool_call.name}"
                
                return {
                    "success": False,
                    "tool_call_id": tool_call.id,
                    "status": "failed",
                    "error": tool_call.error,
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            tool_call.status = "failed"
            tool_call.error = str(e)
            
            return {
                "success": False,
                "tool_call_id": tool_call.id,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _handle_get_tool_result(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle getting tool call result."""
        tool_id = request_data.get("tool_id")
        
        if tool_id not in self.tool_calls:
            raise HTTPException(status_code=404, detail="Tool call not found")
        
        tool_call = self.tool_calls[tool_id]
        return {
            "success": True,
            "tool_call": tool_call.dict(),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_list_capabilities(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle listing agent capabilities."""
        return {
            "success": True,
            "capabilities": [cap.dict() for cap in self.capabilities],
            "agent_id": self.agent_id,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_get_status(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle getting agent status."""
        status = ACPStatus(
            agent_id=self.agent_id,
            status="online",
            capabilities=[cap.name for cap in self.capabilities],
            active_sessions=len(self.active_sessions),
            last_activity=datetime.now(),
            metadata={
                "adapter_version": "1.0.0",
                "agent_name": self.agent.name,
                "description": self.agent.description
            }
        )
        
        return {
            "success": True,
            "status": status.dict(),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_start_session(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle starting a new session."""
        session_data = request_data.get("session_data", {})
        session_id = str(uuid.uuid4())
        
        self.active_sessions[session_id] = {
            "id": session_id,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "metadata": session_data.get("metadata", {})
        }
        
        return {
            "success": True,
            "session_id": session_id,
            "status": "started",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_end_session(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ending a session."""
        session_id = request_data.get("session_id")
        
        if session_id not in self.active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        del self.active_sessions[session_id]
        
        return {
            "success": True,
            "session_id": session_id,
            "status": "ended",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_get_session(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle getting session information."""
        session_id = request_data.get("session_id")
        
        if session_id not in self.active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = self.active_sessions[session_id]
        return {
            "success": True,
            "session": session,
            "timestamp": datetime.now().isoformat()
        }
    
    def _build_capabilities(self) -> List[ACPCapability]:
        """Build agent capabilities from the agent's schema."""
        schema = self.agent.get_schema()
        
        return [
            ACPCapability(
                name="chat",
                description=f"Chat with the {self.agent.name} agent. {self.agent.description}",
                input_schema=schema.get("input_schema", {}),
                output_schema=schema.get("output_schema", {}),
                version="1.0.0",
                category="conversation",
                tags=["chat", "conversation", "ai", "llm"]
            )
        ]
    
    def get_manifest(self) -> Dict[str, Any]:
        """Get the ACP manifest."""
        return {
            "protocol": "ACP",
            "version": "1.0.0",
            "agent_id": self.agent_id,
            "agent_name": self.agent.name,
            "description": f"ACP adapter for {self.agent.name} agent",
            "capabilities": [cap.dict() for cap in self.capabilities],
            "endpoints": {
                "send_message": {
                    "method": "POST",
                    "path": f"/{self.config.prefix}/message",
                    "description": "Send a message using ACP protocol"
                },
                "process_message": {
                    "method": "POST",
                    "path": f"/{self.config.prefix}/message/process",
                    "description": "Process an incoming ACP message"
                },
                "call_tool": {
                    "method": "POST",
                    "path": f"/{self.config.prefix}/tool/call",
                    "description": "Call a tool using ACP protocol"
                },
                "get_tool_result": {
                    "method": "GET",
                    "path": f"/{self.config.prefix}/tool/{{tool_id}}",
                    "description": "Get tool call result"
                },
                "list_capabilities": {
                    "method": "GET",
                    "path": f"/{self.config.prefix}/capabilities",
                    "description": "List agent capabilities"
                },
                "get_status": {
                    "method": "GET",
                    "path": f"/{self.config.prefix}/status",
                    "description": "Get agent status"
                },
                "start_session": {
                    "method": "POST",
                    "path": f"/{self.config.prefix}/session/start",
                    "description": "Start a new session"
                },
                "end_session": {
                    "method": "POST",
                    "path": f"/{self.config.prefix}/session/{{session_id}}/end",
                    "description": "End a session"
                },
                "get_session": {
                    "method": "GET",
                    "path": f"/{self.config.prefix}/session/{{session_id}}",
                    "description": "Get session information"
                }
            },
            "supported_message_types": ["request", "response", "notification", "error"],
            "supported_actions": ["chat", "tool_call", "status", "capability", "session"],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "adapter_version": "1.0.0",
                "protocol_compliance": "ACP-1.0"
            }
        }
