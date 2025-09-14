"""
Configuration management for SuperAgentServer.
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # CORS settings
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="ALLOWED_ORIGINS"
    )
    
    # OpenAI settings
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    model_name: str = Field(default="gpt-3.5-turbo", env="MODEL_NAME")
    temperature: float = Field(default=0.7, env="TEMPERATURE")
    
    # Adapter settings
    mcp_enabled: bool = Field(default=True, env="MCP_ENABLED")
    webhook_enabled: bool = Field(default=True, env="WEBHOOK_ENABLED")
    a2a_enabled: bool = Field(default=True, env="A2A_ENABLED")
    acp_enabled: bool = Field(default=True, env="ACP_ENABLED")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()