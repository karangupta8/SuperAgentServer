# src/super_agent_server/server.py
"""
SuperAgentServer - Universal Agent Adapter Layer

Main FastAPI server that exposes LangChain agents across multiple protocols.
"""

import json
import logging
import os
from contextlib import asynccontextmanager, suppress
from typing import Optional

import uvicorn
from dotenv import find_dotenv, load_dotenv
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

from . import adapters, dependencies
from .adapters.schema_generator import SchemaGenerator
from .agent.base_agent import AgentRequest, BaseAgent
from .agent.example_agent import ExampleAgent
from .config import settings


# --- Pydantic Models for WebSocket ---
class WebSocketInput(BaseModel):
    input: str
    chat_history: list = []


class WebSocketMessage(BaseModel):
    input: WebSocketInput


# --- End Pydantic Models ---

# Load environment variables from .env file if it exists
load_dotenv(find_dotenv())

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_lifespan_handler(agent_instance: Optional[BaseAgent] = None):
    """Factory to create a lifespan handler, optionally with a pre-configured agent."""
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Manage application lifespan events."""
        nonlocal agent_instance

        logger.info("Starting SuperAgentServer...")

        # If no agent is pre-configured, try to initialize the default one
        if agent_instance is None:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                try:
                    logger.info("Initializing default ExampleAgent...")
                    agent_instance = ExampleAgent()
                    await agent_instance.initialize()
                except Exception as e:
                    logger.error(f"Failed to initialize default agent: {e}")
                    agent_instance = None  # Ensure it's None on failure
            else:
                logger.warning(
                    "OPENAI_API_KEY not set. Agent initialization will be skipped."
                )

        dependencies.agent = agent_instance

        # Always register adapters. The `get_agent` dependency will handle
        # whether the agent is available at request time, returning a 503 if not.
        # This makes server behavior consistent and avoids startup race conditions.
        try:
            if settings.MCP_ENABLED:
                app.include_router(adapters.mcp_adapter.router)
                logger.info("MCP adapter enabled.")
            if settings.WEBHOOK_ENABLED:
                app.include_router(adapters.webhook_adapter.router)
                logger.info("Webhook adapter enabled.")
            if settings.A2A_ENABLED:
                app.include_router(adapters.a2a_adapter.router)
                logger.info("A2A adapter enabled.")
            if settings.ACP_ENABLED:
                app.include_router(adapters.acp_adapter.router)
                logger.info("ACP adapter enabled.")
        except Exception as e:
            logger.error(f"Failed to configure adapters: {e}")

        if dependencies.agent:
            logger.info(
                "SuperAgentServer started successfully with an initialized agent."
            )
        else:
            logger.warning("Server is starting without a functional agent.")

        yield

        logger.info("Shutting down SuperAgentServer...")

    return lifespan


def create_app(agent_instance: Optional[BaseAgent] = None) -> FastAPI:
    """Create and configure a FastAPI app instance."""
    app = FastAPI(
        title="SuperAgentServer",
        description="Universal Agent Adapter Layer for LangChain agents",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=create_lifespan_handler(agent_instance)
    )

    # Add CORS middleware
    allowed_origins_str = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    )
    allowed_origins = [
        origin.strip() for origin in allowed_origins_str.split(",")
    ]
    if "*" in allowed_origins:
        logger.warning(
            "CORS is configured to allow all origins. "
            "This is insecure for production."
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Add routes to the app instance ---

    @app.get("/")
    async def root():
        """Root endpoint with server information."""
        return {
            "name": "SuperAgentServer",
            "version": "0.1.0",
            "description": "Universal Agent Adapter Layer for LangChain agents",
            "status": "running",
            "docs": "/docs"
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "agent_initialized": dependencies.agent is not None,
        }

    @app.post("/agent/chat")
    async def agent_chat(
        request: AgentRequest,
        agent: BaseAgent = Depends(dependencies.get_agent)
    ):
        """Direct agent chat endpoint."""
        try:
            response = await agent(request)
            return response
        except Exception as e:
            logger.error(f"Error in agent chat: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/agent/schema")
    async def get_agent_schema(
        agent: BaseAgent = Depends(dependencies.get_agent)
    ):
        """Get the agent's schema."""
        return agent.get_schema()

    @app.get("/manifests", tags=["Adapters"])
    async def get_all_manifests(
        request: Request,
        agent: BaseAgent = Depends(dependencies.get_agent)
    ):
        """
        Get the manifests for all enabled adapters.

        This endpoint provides a consolidated view of the capabilities and
        connection details for each active protocol adapter.
        """
        app = request.app
        generator = SchemaGenerator(app)
        all_manifests = generator.generate_all_manifests(agent)

        enabled_manifests = {}
        # We filter the generated manifests to only include the ones enabled
        # in settings. The keys in `all_manifests` are 'openapi', 'mcp',
        # 'webhook', 'a2a', 'acp'.
        for name in all_manifests.keys():
            if name == "openapi":  # openapi is not a typical adapter, skip it.
                continue

            if getattr(settings, f"{name.upper()}_ENABLED", False):
                if name in all_manifests:
                    enabled_manifests[name] = all_manifests[name]

        return enabled_manifests

    @app.websocket("/chat/stream")
    async def websocket_chat(websocket: WebSocket):
        """WebSocket endpoint for streaming chat with the agent."""
        await websocket.accept()
        logger.info("WebSocket connection established")

        agent = dependencies.agent  # Get the agent from the dependencies module
        if agent is None:
            logger.warning(
                "WebSocket connection rejected: Agent not initialized."
            )
            await websocket.send_text(json.dumps({
                "event": "error",
                "data": {
                    "error": "Agent not initialized. Server is in a degraded state."
                }
            }))
            await websocket.close(code=1011)  # Internal Error
            return

        try:
            while True:
                data = await websocket.receive_text()
                logger.info(f"Received WebSocket message: {data}")

                message = ""
                chat_history = []

                try:
                    # LangServe's client sends a list of one item
                    raw_data = json.loads(data)
                    if isinstance(raw_data, list) and len(raw_data) > 0:
                        message_data = WebSocketMessage.model_validate(raw_data[0])
                        message = message_data.input.input
                        chat_history = message_data.input.chat_history
                    else:
                        # Handle other potential formats if necessary, or raise error
                        raise ValueError(
                            "Invalid message format. Expected a list with one object."
                        )

                    if not message:
                        await websocket.send_text(json.dumps({
                            "event": "error",
                            "data": {"error": "Input message cannot be empty."}
                        }))
                        continue

                    await websocket.send_text(json.dumps({
                        "event": "on_chat_model_start",
                        "data": {"chunk": {"content": ""}}
                    }))

                    input_dict = {"input": message, "chat_history": chat_history}

                    async for chunk in agent.agent_executor.astream(input_dict):
                        if "messages" in chunk:
                            for message_chunk in chunk["messages"]:
                                if hasattr(message_chunk, "content"):
                                    content = message_chunk.content
                                    if content:
                                        await websocket.send_text(json.dumps({
                                            "event": "on_chat_model_stream",
                                            "data": {"chunk": {"content": content}}
                                        }))

                    await websocket.send_text(json.dumps({
                        "event": "on_chat_model_end",
                        "data": {}
                    }))

                except (ValidationError, ValueError) as e:
                    logger.warning(f"Invalid WebSocket message format: {e}")
                    await websocket.send_text(json.dumps({
                        "event": "error",
                        "data": {"error": f"Invalid message format: {e}"}
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
            # Suppress noisy errors on client disconnect
            with suppress(ConnectionResetError):
                logger.error(f"WebSocket error: {e}")

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Global exception handler."""
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

    return app


# Create the default app instance
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
