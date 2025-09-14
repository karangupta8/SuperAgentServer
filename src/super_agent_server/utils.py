"""
Utility functions for SuperAgentServer.
"""

import asyncio
import sys
from typing import Any, Dict, Optional
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def ensure_directory(path: Path) -> None:
    """Ensure a directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def get_version() -> str:
    """Get the package version."""
    try:
        from . import __version__
        return __version__
    except ImportError:
        return "0.1.0"


def is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"


def setup_event_loop() -> None:
    """Set up the event loop for Windows compatibility."""
    if is_windows():
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())