"""
SuperAgentServer - Universal Agent Adapter Layer

Main FastAPI server that exposes LangChain agents across multiple protocols.
"""

import os
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from agent.base_agent import BaseAgent, AgentRequest, AgentResponse
from agent.example_agent import ExampleAgent
from adapters.base_adapter import AdapterRegistry, AdapterConfig
from adapters.mcp_adapter import MCPAdapter
from adapters.webhook_adapter import WebhookAdapter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global registry
adapter_registry = AdapterRegistry()

# Register adapter types
adapter_registry.register_adapter_type("mcp", MCPAdapter)
adapter_registry.register_adapter_type("webhook", WebhookAdapter)

# Create FastAPI app
app = FastAPI(
    title="SuperAgentServer",
    description="Universal Agent Adapter Layer for LangChain agents",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent: Optional[BaseAgent] = None


@app.on_event("startup")
async def startup_event():
    """Initialize the server on startup."""
    global agent
    
    logger.info("Starting SuperAgentServer...")
    
    # Initialize the example agent
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.warning("OPENAI_API_KEY not set, using mock agent")
        # You could create a mock agent here for testing
        return
    
    try:
        agent = ExampleAgent(openai_api_key=openai_api_key)
        await agent.initialize()
        
        # Create and register adapters
        mcp_config = AdapterConfig(
            name="mcp",
            prefix="mcp",
            enabled=True
        )
        
        webhook_config = AdapterConfig(
            name="webhook",
            prefix="webhook",
            enabled=True
        )
        
        # Create adapters
        mcp_adapter = adapter_registry.create_adapter("mcp", agent, mcp_config)
        webhook_adapter = adapter_registry.create_adapter("webhook", agent, webhook_config)
        
        # Register all adapters with the app
        adapter_registry.register_all_with_app(app)
        
        logger.info("SuperAgentServer started successfully")
        logger.info(f"Available adapters: {list(adapter_registry.get_all_adapters().keys())}")
        
    except Exception as e:
        logger.error(f"Failed to start SuperAgentServer: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint with server information."""
    return {
        "name": "SuperAgentServer",
        "version": "0.1.0",
        "description": "Universal Agent Adapter Layer for LangChain agents",
        "status": "running",
        "adapters": list(adapter_registry.get_all_adapters().keys())
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "adapters": len(adapter_registry.get_all_adapters())
    }


@app.get("/manifests")
async def get_manifests():
    """Get manifests for all adapters."""
    return adapter_registry.get_manifests()


@app.post("/agent/chat")
async def agent_chat(request: AgentRequest):
    """Direct agent chat endpoint (bypasses adapters)."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        response = await agent(request)
        return response
    except Exception as e:
        logger.error(f"Error in agent chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agent/schema")
async def get_agent_schema():
    """Get the agent's schema."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return agent.get_schema()


@app.get("/adapters")
async def list_adapters():
    """List all available adapters."""
    adapters = adapter_registry.get_all_adapters()
    return {
        "adapters": [
            {
                "name": name,
                "type": adapter.__class__.__name__,
                "config": adapter.config.dict(),
                "manifest": adapter.get_manifest()
            }
            for name, adapter in adapters.items()
        ]
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


def create_app(agent_instance: Optional[BaseAgent] = None) -> FastAPI:
    """
    Create a FastAPI app with a custom agent.
    
    Args:
        agent_instance: Custom agent instance to use
        
    Returns:
        Configured FastAPI app
    """
    global agent
    agent = agent_instance
    
    # Register adapters if agent is provided
    if agent:
        mcp_config = AdapterConfig(name="mcp", prefix="mcp", enabled=True)
        webhook_config = AdapterConfig(name="webhook", prefix="webhook", enabled=True)
        
        adapter_registry.create_adapter("mcp", agent, mcp_config)
        adapter_registry.create_adapter("webhook", agent, webhook_config)
        adapter_registry.register_all_with_app(app)
    
    return app


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
