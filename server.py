"""
SuperAgentServer - Universal Agent Adapter Layer

Main FastAPI server that exposes LangChain agents across multiple protocols.
"""

import os   
import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
import json
import asyncio

from agent.base_agent import BaseAgent, AgentRequest, AgentResponse
from agent.example_agent import ExampleAgent
from adapters.base_adapter import AdapterRegistry, AdapterConfig
from adapters.mcp_adapter import MCPAdapter
from adapters.webhook_adapter import WebhookAdapter

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global registry
adapter_registry = AdapterRegistry()

# Register adapter types
adapter_registry.register_adapter_type("mcp", MCPAdapter)
adapter_registry.register_adapter_type("webhook", WebhookAdapter)

# Global agent instance
agent: Optional[BaseAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    global agent
    
    # Startup
    logger.info("Starting SuperAgentServer...")
    
    # Initialize the example agent
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.warning("OPENAI_API_KEY not set. Agent initialization will be skipped.")
        yield
        return
    
    try:
        agent = ExampleAgent()
        await agent.initialize()
        
        # Create and register adapters
        mcp_config = AdapterConfig(name="mcp", prefix="mcp", enabled=True)
        webhook_config = AdapterConfig(name="webhook", prefix="webhook", enabled=True)
        
        # Create adapters
        adapter_registry.create_adapter("mcp", agent, mcp_config)
        adapter_registry.create_adapter("webhook", agent, webhook_config)
        
        # Register all adapters with the app
        adapter_registry.register_all_with_app(app)
        
        logger.info("SuperAgentServer started successfully")
        logger.info(f"Available adapters: {list(adapter_registry.get_all_adapters().keys())}")
        
    except Exception as e:
        logger.error(f"Failed to start SuperAgentServer: {e}")
        raise
    
    # Yield control back to the application
    yield
    
    # Shutdown
    logger.info("Shutting down SuperAgentServer...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="SuperAgentServer",
    description="Universal Agent Adapter Layer for LangChain agents",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
# For production, it's recommended to restrict origins.
# You can set this via the ALLOWED_ORIGINS environment variable (comma-separated).
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]
if "*" in allowed_origins:
    logger.warning("CORS is configured to allow all origins. This is insecure for production.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    """Direct agent chat endpoint."""
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


@app.websocket("/chat/stream")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for streaming chat with the agent."""
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            logger.info(f"Received WebSocket message: {data}")
            
            try:
                # Parse the incoming data
                message_data = json.loads(data)
                
                # Extract input and chat history
                if isinstance(message_data, list) and len(message_data) > 0:
                    # LangServe format: [{"input": {"input": "message", "chat_history": []}}]
                    input_data = message_data[0].get("input", {})
                    message = input_data.get("input", "")
                    chat_history = input_data.get("chat_history", [])
                elif isinstance(message_data, dict):
                    # Direct format: {"input": "message", "chat_history": []}
                    message = message_data.get("input", "")
                    chat_history = message_data.get("chat_history", [])
                else:
                    # Simple string
                    message = str(message_data)
                    chat_history = []
                
                if not message:
                    await websocket.send_text(json.dumps({
                        "event": "error",
                        "data": {"error": "No message provided"}
                    }))
                    continue
                
                # Process with agent
                if agent is None:
                    await websocket.send_text(json.dumps({
                        "event": "error",
                        "data": {"error": "Agent not initialized"}
                    }))
                    continue
                
                # Send initial response
                await websocket.send_text(json.dumps({
                    "event": "on_chat_model_start",
                    "data": {"chunk": {"content": ""}}
                }))
                
                # The agent object itself doesn't have `astream`. The underlying LangChain
                # runnable (agent_executor) provides the streaming functionality.
                # LangChain runnables expect a dictionary as input.
                input_dict = {"input": message, "chat_history": chat_history}
                
                # Use the agent's underlying executor for true, real-time streaming.
                async for chunk in agent.agent_executor.astream(input_dict):
                    # Agent stream chunks are dictionaries. The actual content is usually
                    # in a list under the 'messages' key.
                    if "messages" in chunk:
                        for message_chunk in chunk["messages"]:
                            if hasattr(message_chunk, "content"):
                                content = message_chunk.content
                                if content:
                                    # Send each content part as it arrives.
                                    await websocket.send_text(json.dumps({
                                        "event": "on_chat_model_stream",
                                        "data": {"chunk": {"content": content}}
                                    }))
                
                # Send final response
                await websocket.send_text(json.dumps({
                    "event": "on_chat_model_end",
                    "data": {} # LangServe sends an empty data object on end
                }))
                
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "event": "error",
                    "data": {"error": "Invalid JSON format"}
                }))
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                await websocket.send_text(json.dumps({
                    "event": "error",
                    "data": {"error": str(e)}
                }))
                
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


def create_app(agent_instance: Optional[BaseAgent] = None) -> FastAPI:
    """Create a FastAPI app with a custom agent."""
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
