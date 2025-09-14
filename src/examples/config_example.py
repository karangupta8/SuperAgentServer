"""
Configuration examples for different deployment scenarios.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from agent.example_agent import ExampleAgent
from adapters.base_adapter import AdapterConfig
from adapters.schema_generator import SchemaGenerator
from server import create_app


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
        return ExampleAgent(
            openai_api_key=agent_config["config"]["openai_api_key"],
            model_name=agent_config["config"]["model_name"]
        )
    else:
        raise ValueError(f"Unknown agent type: {agent_config['type']}")


def create_adapter_configs(config: Dict[str, Any]) -> Dict[str, AdapterConfig]:
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
    import asyncio
    from fastapi import FastAPI
    
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
