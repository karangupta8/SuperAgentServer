"""
MCP (Model Context Protocol) adapter for exposing agents.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..agent.base_agent import AgentRequest, BaseAgent
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


def _create_mcp_response(
    result: Optional[Dict[str, Any]] = None,
    error: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create an MCP response."""
    response = {}
    if result is not None:
        response["result"] = result
    if error is not None:
        response["error"] = error
    if request_id is not None:
        response["id"] = request_id
    return response


@router.post("/")
async def mcp_endpoint(
    request: MCPRequest, agent: BaseAgent = Depends(get_agent)
):
    """Handle MCP requests."""
    try:
        if request.method == "initialize":
            return _create_mcp_response(
                result={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": True},
                        "resources": {"subscribe": True, "listChanged": True},
                        "prompts": {"listChanged": True},
                    },
                    "serverInfo": {
                        "name": "super-agent-server",
                        "version": "0.1.0",
                    },
                },
                request_id=request.id,
            )

        elif request.method == "tools/list":
            # Get tools from agent schema
            agent_schema = agent.get_schema()
            tools = agent_schema.get("tools", [])
            mcp_tools = []
            for tool in tools:
                mcp_tools.append(
                    MCPTool(
                        name=tool.get("name", ""),
                        description=tool.get("description", ""),
                        inputSchema=tool.get("input_schema", {}),
                    )
                )
            return _create_mcp_response(
                result={"tools": [tool.dict() for tool in mcp_tools]},
                request_id=request.id,
            )

        elif request.method == "tools/call":
            # Call a tool
            params = request.params or {}
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})

            if not tool_name:
                return _create_mcp_response(
                    error={"code": -32602, "message": "Invalid params"},
                    request_id=request.id,
                )

            # Create agent request with tool call
            agent_request = AgentRequest(
                message=f"Call tool {tool_name} with args: {tool_args}",
                metadata={"tool_call": {"name": tool_name, "args": tool_args}},
            )

            response = await agent.process(agent_request)
            return _create_mcp_response(
                result={
                    "content": [
                        {
                            "type": "text",
                            "text": response.message,
                        }
                    ],
                    "isError": False,
                },
                request_id=request.id,
            )

        elif request.method == "resources/list":
            # List available resources
            return _create_mcp_response(
                result={
                    "resources": [
                        {
                            "uri": "agent://schema",
                            "name": "Agent Schema",
                            "description": "The agent's schema definition",
                            "mimeType": "application/json",
                        }
                    ]
                },
                request_id=request.id,
            )

        elif request.method == "resources/read":
            # Read a resource
            params = request.params or {}
            uri = params.get("uri")

            if uri == "agent://schema":
                agent_schema = agent.get_schema()
                return _create_mcp_response(
                    result={
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": "application/json",
                                "text": str(agent_schema),
                            }
                        ]
                    },
                    request_id=request.id,
                )

        elif request.method == "prompts/list":
            # List available prompts
            return _create_mcp_response(
                result={
                    "prompts": [
                        {
                            "name": "chat",
                            "description": "Chat with the agent",
                            "arguments": [
                                {
                                    "name": "message",
                                    "description": "The message to send",
                                    "required": True,
                                }
                            ],
                        }
                    ]
                },
                request_id=request.id,
            )

        elif request.method == "prompts/get":
            # Get a specific prompt
            params = request.params or {}
            prompt_name = params.get("name")

            if prompt_name == "chat":
                return _create_mcp_response(
                    result={
                        "description": "Chat with the agent",
                        "messages": [
                            {
                                "role": "user",
                                "content": {
                                    "type": "text",
                                    "text": "{{message}}",
                                },
                            }
                        ],
                    },
                    request_id=request.id,
                )

        else:
            return _create_mcp_response(
                error={"code": -32601, "message": "Method not found"},
                request_id=request.id,
            )

    except Exception as e:
        return _create_mcp_response(
            error={"code": -32603, "message": f"Internal error: {str(e)}"},
            request_id=request.id,
        )


async def get_manifest(agent: BaseAgent):
    """Generate the MCP manifest for the agent."""
    agent_schema = agent.get_schema()
    return {
        "name": "MCP Adapter",
        "description": (
            "Model Context Protocol adapter for exposing agents "
            "to MCP-compatible clients"
        ),
        "version": "2024-11-05",
        "capabilities": {
            "tools": {"listChanged": True},
            "resources": {"subscribe": True, "listChanged": True},
            "prompts": {"listChanged": True},
        },
        "agent": {
            "name": agent_schema.get("name"),
            "description": agent_schema.get("description"),
            "tools": agent_schema.get("tools", []),
        },
    }
