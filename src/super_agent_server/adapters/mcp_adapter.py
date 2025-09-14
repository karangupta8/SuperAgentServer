"""
MCP (Model Context Protocol) adapter for exposing agents.
"""

import json
from typing import Any, Dict, List, Optional, cast
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ..agent.base_agent import AgentRequest, AgentResponse, BaseAgent
from ..dependencies import get_agent


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


router = APIRouter(prefix="/mcp", tags=["MCP Adapter"])


def _create_mcp_response(result: Optional[Dict[str, Any]] = None,
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


def _get_mcp_tools(agent: BaseAgent) -> List[Dict[str, Any]]:
    """Get MCP tools from agent schema."""
    schema = agent.get_schema()
    return [{
        "name": "chat",
        "description": f"Chat with the {agent.name} agent. {agent.description}",
        "inputSchema": schema["input_schema"]
    }]


def _get_mcp_resources(agent: BaseAgent) -> List[Dict[str, Any]]:
    """Get MCP resources."""
    return [
        {
            "uri": "agent://schema",
            "name": f"{agent.name} Schema",
            "description": f"Complete schema for {agent.name} agent including input/output formats and available tools",
            "mimeType": "application/json"
        },
        {
            "uri": "agent://capabilities",
            "name": f"{agent.name} Capabilities",
            "description": f"Available capabilities and tools for {agent.name} agent",
            "mimeType": "application/json"
        }
    ]


async def _process_mcp_request(request_data: Dict[str, Any], agent: BaseAgent) -> Dict[str, Any]:
    """Process MCP requests."""
    method = request_data.get("method")
    params = request_data.get("params", {})
    request_id = request_data.get("id")

    try:
        if method == "tools/list":
            return _create_mcp_response(
                result={"tools": _get_mcp_tools(agent)},
                request_id=request_id
            )

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})

            if tool_name == "chat":
                agent_request = AgentRequest(
                    message=tool_args.get("message", ""),
                    session_id=tool_args.get("session_id"),
                    metadata=tool_args.get("metadata", {}),
                    tools=tool_args.get("tools")
                )
                response = await agent.process(agent_request)
                return _create_mcp_response(
                    result={
                        "content": [{"type": "text", "text": response.message}],
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
            return _create_mcp_response(
                result={"resources": _get_mcp_resources(agent)},
                request_id=request_id
            )

        elif method == "resources/read":
            resource_uri = params.get("uri")
            if resource_uri == "agent://schema":
                return _create_mcp_response(
                    result={
                        "contents": [{
                            "uri": resource_uri,
                            "mimeType": "application/json",
                            "text": str(agent.get_schema())
                        }]
                    },
                    request_id=request_id
                )
            elif resource_uri == "agent://capabilities":
                schema = agent.get_schema()
                capabilities = {
                    "agent_name": agent.name,
                    "description": agent.description,
                    "available_tools": schema.get("tools", []),
                    "input_schema": schema.get("input_schema", {}),
                    "output_schema": schema.get("output_schema", {})
                }
                return _create_mcp_response(
                    result={
                        "contents": [{
                            "uri": resource_uri,
                            "mimeType": "application/json",
                            "text": str(capabilities)
                        }]
                    },
                    request_id=request_id
                )
            else:
                raise HTTPException(status_code=404, detail=f"Resource not found: {resource_uri}")

        else:
            raise HTTPException(status_code=400, detail=f"Unknown method: {method}")

    except Exception as e:
        return _create_mcp_response(
            error={"code": -32603, "message": "Internal error", "data": str(e)},
            request_id=request_id
        )


@router.post("/tools/list")
async def list_tools(agent: BaseAgent = Depends(get_agent)):
    """List available MCP tools."""
    return await _process_mcp_request({"method": "tools/list"}, agent)


@router.post("/tools/call")
async def call_tool(request: MCPRequest, agent: BaseAgent = Depends(get_agent)):
    """Call an MCP tool."""
    return await _process_mcp_request({
        "method": "tools/call",
        "params": request.params or {},
        "id": request.id
    }, agent)


@router.post("/resources/list")
async def list_resources(agent: BaseAgent = Depends(get_agent)):
    """List available MCP resources."""
    return await _process_mcp_request({"method": "resources/list"}, agent)


@router.post("/resources/read")
async def read_resource(request: MCPRequest, agent: BaseAgent = Depends(get_agent)):
    """Read an MCP resource."""
    return await _process_mcp_request({
        "method": "resources/read",
        "params": request.params or {},
        "id": request.id
    }, agent)


@router.get("/manifest")
async def get_manifest(agent: BaseAgent = Depends(get_agent)):
    """Get the MCP manifest."""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}, "resources": {}},
        "serverInfo": {
            "name": f"{agent.name}-mcp",
            "version": "0.1.0",
            "description": f"MCP adapter for {agent.name} agent"
        },
        "tools": _get_mcp_tools(agent),
        "resources": _get_mcp_resources(agent)
    }
