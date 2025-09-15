#!/usr/bin/env python3
"""
Simple run script for SuperAgentServer.
"""

import os
import sys
import argparse
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project's 'src' directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from super_agent_server.server import app
import uvicorn


def main():
    """Main entry point."""
    print("🚀 Starting SuperAgentServer...")

    parser = argparse.ArgumentParser(description="Run the SuperAgentServer for development.")
    parser.add_argument(
        "agent_app",
        nargs="?",
        default="super_agent_server.server:app",
        help="The agent app to run, in 'module:variable' format. "
             "Defaults to 'super_agent_server.server:app' (which loads ExampleAgent)."
    )
    args = parser.parse_args()
    print("=" * 50)

    # Check for minimum Python version
    if sys.version_info < (3, 8):
        print(f"❌ Error: Your Python version is {sys.version_info.major}.{sys.version_info.minor}.")
        print("   SuperAgentServer requires Python 3.8 or newer.")
        print("   Please create a new virtual environment with a compatible Python version.")
        sys.exit(1)
    
    # Check for critical dependency versions
    try:
        from importlib.metadata import version, PackageNotFoundError
        ws_version = version("websockets")
        if tuple(map(int, ws_version.split('.'))) < (12, 0):
            print(f"❌ Error: Your websockets version is {ws_version}, but >=12.0 is required.")
            print("   This can cause unexpected errors with streaming.")
            print("   Please run: pip install --force-reinstall --no-cache-dir -r requirements.txt")
            sys.exit(1)
    except (ImportError, PackageNotFoundError):
        # Fallback for older Python or if a package is missing
        print("⚠️  Warning: Could not verify dependency versions.")
        print("   If you encounter errors, please ensure your packages are up to date:")
        print("   pip install --force-reinstall --no-cache-dir -r requirements.txt")
        print()
        pass # Don't exit, just warn


    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set")
        print("   The example agent will not work without an OpenAI API key")
        print("   Set it in your environment or .env file")
        print()

    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        print("⚠️  Warning: TELEGRAM_BOT_TOKEN not set")
        print("   The Telegram webhook adapter will not be able to send replies.")
        print("   To enable bi-directional chat, set it in your .env file.")
        print()

    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print(f"🌐 Server: http://{host}:{port}")
    print(f"📦 Agent App: {args.agent_app}")
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
    print("  - POST /webhook - Generic webhook")
    print("  - POST /webhook/telegram - Telegram webhook")
    print("  - POST /webhook/slack - Slack webhook")
    print("  - POST /webhook/discord - Discord webhook")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Run the server
    try:
        uvicorn.run(
            args.agent_app,
            host=host,
            port=port,
            reload=debug,
            log_level=log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        # This is expected when pressing Ctrl+C, so we don't need to print an error.
        # The 'finally' block will handle the exit message.
        pass
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)
    finally:
        print("\n👋 Server has been shut down.")

if __name__ == "__main__":
    main()
