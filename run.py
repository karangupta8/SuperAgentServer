#!/usr/bin/env python3
"""
Simple run script for SuperAgentServer.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from server import app
import uvicorn


def main():
    """Main entry point."""
    print("🚀 Starting SuperAgentServer...")
    print("=" * 50)
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set")
        print("   The example agent will not work without an OpenAI API key")
        print("   Set it in your environment or .env file")
        print()
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print(f"🌐 Server: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"🔧 Debug Mode: {debug}")
    print(f"📝 Log Level: {log_level}")
    print()
    print("Available endpoints:")
    print("  - GET  / - Server information")
    print("  - GET  /health - Health check")
    print("  - POST /agent/chat - Direct agent chat")
    print("  - GET  /agent/schema - Agent schema")
    print("  - POST /mcp/tools/list - MCP tools")
    print("  - POST /mcp/tools/call - MCP tool call")
    print("  - POST /webhook/webhook - Generic webhook")
    print("  - POST /webhook/telegram - Telegram webhook")
    print("  - POST /webhook/slack - Slack webhook")
    print("  - POST /webhook/discord - Discord webhook")
    print("  - GET  /manifests - All adapter manifests")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Run the server
    try:
        uvicorn.run(
            "server:app",
            host=host,
            port=port,
            reload=debug,
            log_level=log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
