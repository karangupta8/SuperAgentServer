"""
Configuration examples for different deployment scenarios.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

# Add the project's 'src' directory to the Python path to allow running this
# script directly
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from super_agent_server.adapters.base_adapter import AdapterConfig
from super_agent_server.adapters.schema_generator import SchemaGenerator
from super_agent_server.agent.example_agent import ExampleAgent
from super_agent_server.server import create_app

# Example 1: Basic configuration
BASIC_CONFIG = {
    "agent": {
        "type": "example",
        "config": {
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "model_name": "gpt-3.5-turbo"
        }
    },
    "adapters": {
        "mcp": {
            "enabled": True,
            "prefix": "mcp",
            "config": {}
        },
        "webhook": {
            "enabled": True,
            "prefix": "webhook",
            "config": {}
        },
        "a2a": {
            "enabled": True,
            "prefix": "a2a",
            "config": {}
        },
        "acp": {
            "enabled": True,
            "prefix": "acp",
            "config": {}
        }
    },
    "server": {
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True
    }
}


# Example 2: Production configuration
PRODUCTION_CONFIG = {
    "agent": {
        "type": "example",
        "config": {
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "model_name": "gpt-4"
        }
    },
    "adapters": {
        "mcp": {
            "enabled": True,
            "prefix": "mcp",
            "config": {
                "max_requests_per_minute": 100,
                "timeout": 30
            }
        },
        "webhook": {
            "enabled": True,
            "prefix": "webhook",
            "config": {
                "verify_signatures": True,
                "max_payload_size": "10MB"
            }
        },
        "a2a": {
            "enabled": True,
            "prefix": "a2a",
            "config": {
                "timeout": 30
            }
        },
        "acp": {
            "enabled": True,
            "prefix": "acp",
            "config": {}
        }
    },
    "server": {
        "host": "0.0.0.0",
        "port": 8000,
        "reload": False,
        "workers": 4,
        "log_level": "info"
    }
}


# Example 3: Development configuration
DEVELOPMENT_CONFIG = {
    "agent": {
        "type": "example",
        "config": {
            "openai_api_key": os.getenv("OPENAI_API_KEY", "mock-key"),
            "model_name": "gpt-3.5-turbo"
        }
    },
    "adapters": {
        "mcp": {
            "enabled": True,
            "prefix": "mcp",
            "config": {
                "debug": True
            }
        },
        "webhook": {
            "enabled": True,
            "prefix": "webhook",
            "config": {
                "debug": True,
                "log_requests": True
            }
        },
        "a2a": {
            "enabled": True,
            "prefix": "a2a",
            "config": {
                "debug": True
            }
        },
        "acp": {
            "enabled": True,
            "prefix": "acp",
            "config": {}
        }
    },
    "server": {
        "host": "127.0.0.1",
        "port": 8000,
        "reload": True,
        "log_level": "debug"
    }
}


def create_agent_from_config(config: Dict[str, Any]):
    """Create an agent from configuration."""
    agent_config = config["agent"]

    if agent_config["type"] == "example":
        # ExampleAgent now reads its configuration from environment variables
        # The config dictionary values are for documentation/reference
        return ExampleAgent()
    else:
        raise ValueError(f"Unknown agent type: {agent_config['type']}")


def create_adapter_configs(
    config: Dict[str, Any]
) -> Dict[str, AdapterConfig]:
    """Create adapter configurations from config."""
    adapter_configs = {}

    for name, adapter_config in config["adapters"].items():
        if adapter_config["enabled"]:
            adapter_configs[name] = AdapterConfig(
                name=name,
                prefix=adapter_config["prefix"],
                enabled=True,
                config=adapter_config["config"]
            )

    return adapter_configs


def generate_manifests(agent, app):
    """Generate all manifests for the agent."""
    generator = SchemaGenerator(app)
    return generator.generate_all_manifests(agent)


# Example usage
if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    import asyncio

    async def main():
        # Use development config
        config = DEVELOPMENT_CONFIG

        # Create agent
        agent = create_agent_from_config(config)
        await agent.initialize()

        # Create app
        app = create_app(agent)

        # Generate manifests
        manifests = generate_manifests(agent, app)

        print("Generated Manifests:")
        print("=" * 50)
        for name, manifest in manifests.items():
            print(f"\n{name.upper()} Manifest:")
            print("-" * 30)
            print(manifest)

    asyncio.run(main())
