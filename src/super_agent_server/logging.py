"""
Logging configuration for SuperAgentServer.
"""

import logging
import logging.config
from pathlib import Path
from typing import Optional

import yaml


def setup_logging(config_path: Optional[str] = None) -> None:
    """Set up logging configuration."""
    
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "logging.yaml"
    
    if Path(config_path).exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)
    else:
        # Fallback to basic logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )