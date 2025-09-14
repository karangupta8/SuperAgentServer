from typing import Optional

from fastapi import HTTPException

from .agent.base_agent import BaseAgent

# This module holds the shared state and dependencies for the application
# to avoid circular imports.

# Global agent instance, to be initialized at startup.
agent: Optional[BaseAgent] = None

async def get_agent() -> BaseAgent:
    """FastAPI dependency to get the initialized agent instance."""
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized. Check server logs for details.")
    return agent