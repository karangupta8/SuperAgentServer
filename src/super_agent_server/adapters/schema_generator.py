"""
Schema auto-generation from LangServe REST definitions.
"""

import json
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, create_model

from ..agent.base_agent import BaseAgent


class SchemaGenerator:
    """Generates adapter schemas from LangServe REST definitions."""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.openapi_schema = None
    
    def get_openapi_schema(self) -> Dict[str, Any]:
        """Get the OpenAPI schema for the FastAPI app."""
        if self.openapi_schema is None:
            self.openapi_schema = get_openapi(
                title=self.app.title,
                version=self.app.version,
                description=self.app.description,
                routes=self.app.routes
            )
        return self.openapi_schema
    
    def extract_agent_schema(self, agent: BaseAgent) -> Dict[str, Any]:
        """Extract schema from agent and convert to OpenAPI format."""
        agent_schema = agent.get_schema()
        
        # Convert to OpenAPI format
        openapi_schema = {
            "openapi": "3.0.0",
            "info": {
                "title": f"{agent.name} Agent API",
                "version": "1.0.0",
                "description": agent.description
            },
            "paths": {
                "/agent/chat": {
                    "post": {
                        "summary": "Chat with the agent",
                        "description": "Send a message to the agent and get a response",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": agent_schema["input_schema"]
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": agent_schema["output_schema"]
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": self._create_component_schemas(agent_schema)
            }
        }
        
        return openapi_schema
    
    def _create_component_schemas(self, agent_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Create OpenAPI component schemas from agent schema."""
        schemas = {}
        
        # Convert input schema
        if "input_schema" in agent_schema:
            schemas["AgentRequest"] = agent_schema["input_schema"]
        
        # Convert output schema
        if "output_schema" in agent_schema:
            schemas["AgentResponse"] = agent_schema["output_schema"]
        
        # Convert tool schemas
        if "tools" in agent_schema:
            for i, tool in enumerate(agent_schema["tools"]):
                tool_name = tool.get("name", f"Tool{i}")
                schemas[f"{tool_name}Tool"] = {
                    "type": "object",
                    "properties": tool.get("parameters", {}),
                    "required": tool.get("parameters", {}).get("required", [])
                }
        
        return schemas
    
    def generate_mcp_manifest(self, agent: BaseAgent) -> Dict[str, Any]:
        """Generate MCP manifest from agent schema."""
        agent_schema = agent.get_schema()
        
        manifest = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {}
            },
            "serverInfo": {
                "name": f"{agent.name}-mcp",
                "version": "0.1.0",
                "description": f"MCP adapter for {agent.name} agent"
            },
            "tools": [],
            "resources": []
        }
        
        # Add main chat tool
        manifest["tools"].append({
            "name": "agent_chat",
            "description": f"Chat with the {agent.name} agent",
            "inputSchema": agent_schema["input_schema"]
        })
        
        # Add agent-specific tools
        if "tools" in agent_schema:
            for tool in agent_schema["tools"]:
                manifest["tools"].append({
                    "name": f"agent_{tool['name']}",
                    "description": tool["description"],
                    "inputSchema": tool["parameters"]
                })
        
        # Add resources
        manifest["resources"].append({
            "uri": "agent://schema",
            "name": f"{agent.name} Schema",
            "description": f"Schema for {agent.name} agent",
            "mimeType": "application/json"
        })
        
        return manifest
    
    def generate_webhook_manifest(self, agent: BaseAgent) -> Dict[str, Any]:
        """Generate webhook manifest from agent schema."""
        agent_schema = agent.get_schema()
        
        return {
            "name": f"{agent.name}-webhook",
            "version": "0.1.0",
            "description": f"Webhook adapter for {agent.name} agent",
            "endpoints": {
                "webhook": {
                    "method": "POST",
                    "path": "/webhook/webhook",
                    "description": "Generic webhook endpoint",
                    "request_schema": agent_schema["input_schema"],
                    "response_schema": agent_schema["output_schema"]
                },
                "telegram": {
                    "method": "POST",
                    "path": "/webhook/telegram",
                    "description": "Telegram webhook endpoint"
                },
                "slack": {
                    "method": "POST",
                    "path": "/webhook/slack",
                    "description": "Slack webhook endpoint"
                },
                "discord": {
                    "method": "POST",
                    "path": "/webhook/discord",
                    "description": "Discord webhook endpoint"
                }
            }
        }
    
    def generate_a2a_card(self, agent: BaseAgent) -> Dict[str, Any]:
        """Generate A2A (Agent-to-Agent) protocol card."""
        agent_schema = agent.get_schema()
        
        return {
            "version": "1.0",
            "type": "agent_card",
            "agent": {
                "name": agent.name,
                "description": agent.description,
                "version": "0.1.0",
                "capabilities": {
                    "chat": True,
                    "tools": len(agent_schema.get("tools", [])),
                    "memory": True
                },
                "endpoints": {
                    "chat": {
                        "url": "/agent/chat",
                        "method": "POST",
                        "schema": agent_schema["input_schema"]
                    }
                },
                "tools": agent_schema.get("tools", []),
                "metadata": {
                    "framework": "langchain",
                    "adapter": "super-agent-server"
                }
            }
        }
    
    def generate_acp_manifest(self, agent: BaseAgent) -> Dict[str, Any]:
        """Generate ACP (Agent Communication Protocol) manifest."""
        agent_schema = agent.get_schema()
        
        return {
            "version": "1.0",
            "protocol": "acp",
            "agent": {
                "id": agent.name,
                "name": agent.name,
                "description": agent.description,
                "version": "0.1.0",
                "capabilities": [
                    "text_generation",
                    "tool_use",
                    "conversation"
                ],
                "api": {
                    "base_url": "/agent",
                    "endpoints": {
                        "chat": {
                            "path": "/chat",
                            "method": "POST",
                            "input_schema": agent_schema["input_schema"],
                            "output_schema": agent_schema["output_schema"]
                        }
                    }
                },
                "tools": agent_schema.get("tools", [])
            }
        }
    
    def generate_all_manifests(self, agent: BaseAgent) -> Dict[str, Any]:
        """Generate all adapter manifests for an agent."""
        return {
            "openapi": self.extract_agent_schema(agent),
            "mcp": self.generate_mcp_manifest(agent),
            "webhook": self.generate_webhook_manifest(agent),
            "a2a": self.generate_a2a_card(agent),
            "acp": self.generate_acp_manifest(agent)
        }
