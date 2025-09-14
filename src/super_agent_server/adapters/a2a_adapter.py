"""
A2A (Agent-to-Agent) adapter for exposing agents via the Agent-to-Agent protocol.

The A2A protocol enables direct communication between AI agents, allowing them to
collaborate and share tasks efficiently across different platforms and frameworks.
"""

import json
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from fastapi import HTTPException, Request
from pydantic import BaseModel, Field

from .base_adapter import BaseAdapter, AdapterConfig
from agent.base_agent import AgentRequest, AgentResponse


class A2AMessage(BaseModel):
    """A2A message format."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    content: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    source_agent: Optional[str] = None
    target_agent: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class A2ATask(BaseModel):
    """A2A task definition."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    status: str = "pending"  # pending, in_progress, completed, failed
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class A2ACapability(BaseModel):
    """A2A agent capability definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    version: str = "1.0.0"
    tags: List[str] = []


class A2AAdapter(BaseAdapter):
    """
    A2A adapter for exposing agents via the Agent-to-Agent protocol.
    
    This adapter enables agents to communicate directly with other A2A-compatible
    agents, facilitating multi-agent collaboration and task sharing.
    """
    
    def __init__(self, agent, config: AdapterConfig):
        super().__init__(agent, config)
        self.agent_id = f"{self.agent.name}-{str(uuid.uuid4())[:8]}"
        self.tasks: Dict[str, A2ATask] = {}
        self.capabilities: List[A2ACapability] = self._build_capabilities()
    
    def _setup_routes(self) -> None:
        """Set up A2A-specific routes."""
        
        @self.router.post("/message")
        async def send_message(message: A2AMessage):
            """Send a message to another agent."""
            return await self._process_request({
                "action": "send_message",
                "message": message.dict()
            })
        
        @self.router.post("/message/receive")
        async def receive_message(request: Request):
            """Receive a message from another agent."""
            data = await request.json()
            return await self._process_request({
                "action": "receive_message",
                "message": data
            })
        
        @self.router.post("/task/create")
        async def create_task(task: A2ATask):
            """Create a new task for this agent."""
            return await self._process_request({
                "action": "create_task",
                "task": task.dict()
            })
        
        @self.router.get("/task/{task_id}")
        async def get_task(task_id: str):
            """Get task status and result."""
            return await self._process_request({
                "action": "get_task",
                "task_id": task_id
            })
        
        @self.router.post("/task/{task_id}/execute")
        async def execute_task(task_id: str, request: Request):
            """Execute a specific task."""
            data = await request.json()
            return await self._process_request({
                "action": "execute_task",
                "task_id": task_id,
                "input": data
            })
        
        @self.router.get("/capabilities")
        async def list_capabilities():
            """List agent capabilities."""
            return await self._process_request({
                "action": "list_capabilities"
            })
        
        @self.router.get("/status")
        async def get_agent_status():
            """Get agent status and health."""
            return await self._process_request({
                "action": "get_status"
            })
        
        @self.router.get("/manifest")
        async def get_manifest():
            """Get the A2A manifest."""
            return self.get_manifest()
    
    async def _process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process A2A requests."""
        action = request_data.get("action")
        
        try:
            if action == "send_message":
                return await self._handle_send_message(request_data)
            elif action == "receive_message":
                return await self._handle_receive_message(request_data)
            elif action == "create_task":
                return await self._handle_create_task(request_data)
            elif action == "get_task":
                return await self._handle_get_task(request_data)
            elif action == "execute_task":
                return await self._handle_execute_task(request_data)
            elif action == "list_capabilities":
                return await self._handle_list_capabilities(request_data)
            elif action == "get_status":
                return await self._handle_get_status(request_data)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _handle_send_message(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sending a message to another agent."""
        message_data = request_data.get("message", {})
        
        # In a real implementation, this would route the message to the target agent
        # For now, we'll just acknowledge the message
        return {
            "success": True,
            "message_id": message_data.get("id"),
            "status": "sent",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_receive_message(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle receiving a message from another agent."""
        message_data = request_data.get("message", {})
        
        # Process the message with the agent
        if message_data.get("type") == "chat":
            agent_request = AgentRequest(
                message=message_data.get("content", {}).get("text", ""),
                session_id=message_data.get("session_id"),
                metadata={
                    **(message_data.get("metadata", {})),
                    "source_agent": message_data.get("source_agent"),
                    "message_id": message_data.get("id")
                }
            )
            
            response = await self.agent(agent_request)
            
            return {
                "success": True,
                "response": {
                    "id": str(uuid.uuid4()),
                    "type": "chat_response",
                    "content": {
                        "text": response.message
                    },
                    "timestamp": datetime.now().isoformat(),
                    "source_agent": self.agent_id,
                    "target_agent": message_data.get("source_agent"),
                    "session_id": response.session_id,
                    "metadata": {
                        "tools_used": response.tools_used,
                        "response_metadata": response.metadata
                    }
                }
            }
        
        return {
            "success": True,
            "status": "acknowledged",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_create_task(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle creating a new task."""
        task_data = request_data.get("task", {})
        task = A2ATask(**task_data)
        self.tasks[task.id] = task
        
        return {
            "success": True,
            "task_id": task.id,
            "status": "created",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_get_task(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle getting task status."""
        task_id = request_data.get("task_id")
        
        if task_id not in self.tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task = self.tasks[task_id]
        return {
            "success": True,
            "task": task.dict(),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_execute_task(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle executing a task."""
        task_id = request_data.get("task_id")
        input_data = request_data.get("input", {})
        
        if task_id not in self.tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task = self.tasks[task_id]
        task.status = "in_progress"
        task.updated_at = datetime.now()
        
        try:
            # Execute the task using the agent
            agent_request = AgentRequest(
                message=input_data.get("message", ""),
                session_id=input_data.get("session_id"),
                metadata={
                    **(input_data.get("metadata", {})),
                    "task_id": task_id,
                    "task_name": task.name
                }
            )
            
            response = await self.agent(agent_request)
            
            task.status = "completed"
            task.result = {
                "message": response.message,
                "tools_used": response.tools_used,
                "metadata": response.metadata
            }
            task.updated_at = datetime.now()
            
            return {
                "success": True,
                "task_id": task_id,
                "status": "completed",
                "result": task.result,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.updated_at = datetime.now()
            
            return {
                "success": False,
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
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
        return {
            "success": True,
            "agent_id": self.agent_id,
            "status": "healthy",
            "capabilities_count": len(self.capabilities),
            "active_tasks": len([t for t in self.tasks.values() if t.status in ["pending", "in_progress"]]),
            "completed_tasks": len([t for t in self.tasks.values() if t.status == "completed"]),
            "timestamp": datetime.now().isoformat()
        }
    
    def _build_capabilities(self) -> List[A2ACapability]:
        """Build agent capabilities from the agent's schema."""
        schema = self.agent.get_schema()
        
        return [
            A2ACapability(
                name="chat",
                description=f"Chat with the {self.agent.name} agent. {self.agent.description}",
                input_schema=schema.get("input_schema", {}),
                output_schema=schema.get("output_schema", {}),
                version="1.0.0",
                tags=["chat", "conversation", "ai"]
            )
        ]
    
    def get_manifest(self) -> Dict[str, Any]:
        """Get the A2A manifest."""
        return {
            "protocol": "A2A",
            "version": "1.0.0",
            "agent_id": self.agent_id,
            "agent_name": self.agent.name,
            "description": f"A2A adapter for {self.agent.name} agent",
            "capabilities": [cap.dict() for cap in self.capabilities],
            "endpoints": {
                "send_message": {
                    "method": "POST",
                    "path": f"/{self.config.prefix}/message",
                    "description": "Send a message to another agent"
                },
                "receive_message": {
                    "method": "POST",
                    "path": f"/{self.config.prefix}/message/receive",
                    "description": "Receive a message from another agent"
                },
                "create_task": {
                    "method": "POST",
                    "path": f"/{self.config.prefix}/task/create",
                    "description": "Create a new task for this agent"
                },
                "get_task": {
                    "method": "GET",
                    "path": f"/{self.config.prefix}/task/{{task_id}}",
                    "description": "Get task status and result"
                },
                "execute_task": {
                    "method": "POST",
                    "path": f"/{self.config.prefix}/task/{{task_id}}/execute",
                    "description": "Execute a specific task"
                },
                "list_capabilities": {
                    "method": "GET",
                    "path": f"/{self.config.prefix}/capabilities",
                    "description": "List agent capabilities"
                },
                "get_status": {
                    "method": "GET",
                    "path": f"/{self.config.prefix}/status",
                    "description": "Get agent status and health"
                }
            },
            "supported_message_types": ["chat", "task", "status", "capability"],
            "supported_task_types": ["chat", "analysis", "generation"],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "adapter_version": "1.0.0"
            }
        }
