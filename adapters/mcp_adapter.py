"""
MCP (Model Context Protocol) adapter for exposing agents.
"""

from typing import Any, Dict, List, Optional
from fastapi import HTTPException
from pydantic import BaseModel

from .base_adapter import BaseAdapter, AdapterConfig
from agent.base_agent import AgentRequest, AgentResponse


class MCPRequest(BaseModel):
    """MCP request format."""
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[str] = None


class MCPResponse(BaseModel):
    """MCP response format."""
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None


class MCPTool(BaseModel):
    """MCP tool definition."""
    name: str
    description: str
    inputSchema: Dict[str, Any]


class MCPAdapter(BaseAdapter):
    """
    MCP adapter for exposing agents via the Model Context Protocol.
    
    This adapter maps agent functionality to MCP tools and resources.
    """
    
    def _setup_routes(self) -> None:
        """Set up MCP-specific routes."""
        
        @self.router.post("/tools/list")
        async def list_tools():
            """List available MCP tools."""
            return await self._process_request({
                "method": "tools/list",
                "params": {}
            })
        
        @self.router.post("/tools/call")
        async def call_tool(request: MCPRequest):
            """Call an MCP tool."""
            return await self._process_request({
                "method": "tools/call",
                "params": request.params or {},
                "id": request.id
            })
        
        @self.router.post("/resources/list")
        async def list_resources():
            """List available MCP resources."""
            return await self._process_request({
                "method": "resources/list",
                "params": {}
            })
        
        @self.router.post("/resources/read")
        async def read_resource(request: MCPRequest):
            """Read an MCP resource."""
            return await self._process_request({
                "method": "resources/read",
                "params": request.params or {},
                "id": request.id
            })
        
        @self.router.get("/manifest")
        async def get_manifest():
            """Get the MCP manifest."""
            return self.get_manifest()
    
    async def _process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process MCP requests."""
        method = request_data.get("method")
        params = request_data.get("params", {})
        request_id = request_data.get("id")
        
        try:
            if method == "tools/list":
                return self._create_mcp_response(
                    result={"tools": self._get_mcp_tools()},
                    request_id=request_id
                )
            
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                
                if tool_name == "agent_chat":
                    # Convert MCP tool call to agent request
                    agent_request = AgentRequest(
                        message=tool_args.get("message", ""),
                        session_id=tool_args.get("session_id"),
                        metadata=tool_args.get("metadata", {}),
                        tools=tool_args.get("tools")
                    )
                    
                    # Process with agent
                    response = await self.agent(agent_request)
                    
                    return self._create_mcp_response(
                        result={
                            "content": [
                                {
                                    "type": "text",
                                    "text": response.message
                                }
                            ],
                            "metadata": {
                                "session_id": response.session_id,
                                "tools_used": response.tools_used,
                                "timestamp": response.timestamp.isoformat()
                            }
                        },
                        request_id=request_id
                    )
                else:
                    raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")
            
            elif method == "resources/list":
                return self._create_mcp_response(
                    result={"resources": self._get_mcp_resources()},
                    request_id=request_id
                )
            
            elif method == "resources/read":
                resource_uri = params.get("uri")
                if resource_uri == "agent://schema":
                    return self._create_mcp_response(
                        result={
                            "contents": [
                                {
                                    "uri": resource_uri,
                                    "mimeType": "application/json",
                                    "text": str(self.agent.get_schema())
                                }
                            ]
                        },
                        request_id=request_id
                    )
                else:
                    raise HTTPException(status_code=404, detail=f"Resource not found: {resource_uri}")
            
            else:
                raise HTTPException(status_code=400, detail=f"Unknown method: {method}")
        
        except Exception as e:
            return self._create_mcp_response(
                error={
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                },
                request_id=request_id
            )
    
    def _create_mcp_response(self, result: Optional[Dict[str, Any]] = None, 
                           error: Optional[Dict[str, Any]] = None,
                           request_id: Optional[str] = None) -> Dict[str, Any]:
        """Create an MCP response."""
        response = {}
        if result is not None:
            response["result"] = result
        if error is not None:
            response["error"] = error
        if request_id is not None:
            response["id"] = request_id
        return response
    
    def _get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get MCP tools from agent schema."""
        schema = self.agent.get_schema()
        tools = []
        
        # Add the main agent chat tool
        tools.append({
            "name": "agent_chat",
            "description": f"Chat with the {self.agent.name} agent",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to send to the agent"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Session ID for conversation continuity"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional metadata"
                    },
                    "tools": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Available tools"
                    }
                },
                "required": ["message"]
            }
        })
        
        # Add agent-specific tools
        if "tools" in schema:
            for tool in schema["tools"]:
                tools.append({
                    "name": f"agent_{tool['name']}",
                    "description": tool["description"],
                    "inputSchema": tool["parameters"]
                })
        
        return tools
    
    def _get_mcp_resources(self) -> List[Dict[str, Any]]:
        """Get MCP resources."""
        return [
            {
                "uri": "agent://schema",
                "name": f"{self.agent.name} Schema",
                "description": f"Schema for {self.agent.name} agent",
                "mimeType": "application/json"
            }
        ]
    
    def get_manifest(self) -> Dict[str, Any]:
        """Get the MCP manifest."""
        schema = self.agent.get_schema()
        
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {}
            },
            "serverInfo": {
                "name": f"{self.agent.name}-mcp",
                "version": "0.1.0",
                "description": f"MCP adapter for {self.agent.name} agent"
            },
            "tools": self._get_mcp_tools(),
            "resources": self._get_mcp_resources()
        }
