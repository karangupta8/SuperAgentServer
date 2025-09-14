"""
Application configuration settings.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables and .env file.
    """
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )

    # Core Server Settings
    HOST: str = Field(
        default="0.0.0.0", description="Server host address"
    )
    PORT: int = Field(default=8000, description="Server port number")
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # OpenAI Configuration
    OPENAI_API_KEY: str | None = Field(
        default=None, description="OpenAI API key"
    )
    MODEL_NAME: str = Field(
        default="gpt-3.5-turbo", description="OpenAI model name"
    )
    TEMPERATURE: float = Field(
        default=0.7, description="Model temperature"
    )

    # CORS Configuration
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        description="Comma-separated list of allowed origins"
    )

    # Adapter Settings
    MCP_ENABLED: bool = Field(
        default=True, description="Enable MCP adapter"
    )
    WEBHOOK_ENABLED: bool = Field(
        default=True, description="Enable webhook adapter"
    )
    A2A_ENABLED: bool = Field(
        default=True, description="Enable A2A adapter"
    )
    ACP_ENABLED: bool = Field(
        default=True, description="Enable ACP adapter"
    )

    # Webhook Configuration
    TELEGRAM_BOT_TOKEN: str | None = Field(
        default=None, description="Telegram bot token"
    )
    SLACK_BOT_TOKEN: str | None = Field(
        default=None, description="Slack bot token"
    )
    DISCORD_BOT_TOKEN: str | None = Field(
        default=None, description="Discord bot token"
    )


# Create a single, global instance of the settings
settings = Settings()