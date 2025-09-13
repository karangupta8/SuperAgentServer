"""
Test script to verify SuperAgentServer functionality.
"""

import asyncio
import httpx
import json
from server import create_app
from examples.simple_agent import SimpleChatAgent


async def test_server():
    """Test the SuperAgentServer functionality."""
    print("🧪 Testing SuperAgentServer...")
    print("=" * 50)
    
    # Create a simple agent for testing
    agent = SimpleChatAgent()
    await agent.initialize()
    
    # Create the FastAPI app
    app = create_app(agent)
    
    # Test the agent directly
    print("\n1. Testing Agent Directly:")
    print("-" * 30)
    
    from agent.base_agent import AgentRequest
    
    test_request = AgentRequest(
        message="Hello, how are you?",
        session_id="test-session"
    )
    
    response = await agent(test_request)
    print(f"Input: {test_request.message}")
    print(f"Output: {response.message}")
    print(f"Session: {response.session_id}")
    print(f"Metadata: {response.metadata}")
    
    # Test the agent schema
    print("\n2. Testing Agent Schema:")
    print("-" * 30)
    
    schema = agent.get_schema()
    print(f"Agent Name: {schema['name']}")
    print(f"Description: {schema['description']}")
    print(f"Input Schema: {json.dumps(schema['input_schema'], indent=2)}")
    
    # Test MCP adapter
    print("\n3. Testing MCP Adapter:")
    print("-" * 30)
    
    from adapters.mcp_adapter import MCPAdapter
    from adapters.base_adapter import AdapterConfig
    
    mcp_config = AdapterConfig(name="mcp", prefix="mcp", enabled=True)
    mcp_adapter = MCPAdapter(agent, mcp_config)
    
    # Test MCP tools list
    tools_response = await mcp_adapter._process_request({
        "method": "tools/list",
        "params": {}
    })
    print(f"MCP Tools: {json.dumps(tools_response, indent=2)}")
    
    # Test MCP tool call
    call_response = await mcp_adapter._process_request({
        "method": "tools/call",
        "params": {
            "name": "agent_chat",
            "arguments": {
                "message": "Hello from MCP!",
                "session_id": "mcp-test"
            }
        }
    })
    print(f"MCP Tool Call Result: {json.dumps(call_response, indent=2)}")
    
    # Test Webhook adapter
    print("\n4. Testing Webhook Adapter:")
    print("-" * 30)
    
    from adapters.webhook_adapter import WebhookAdapter
    
    webhook_config = AdapterConfig(name="webhook", prefix="webhook", enabled=True)
    webhook_adapter = WebhookAdapter(agent, webhook_config)
    
    # Test generic webhook
    webhook_response = await webhook_adapter._process_request({
        "message": "Hello from webhook!",
        "user_id": "test-user",
        "platform": "test"
    })
    print(f"Webhook Response: {json.dumps(webhook_response, indent=2)}")
    
    # Test webhook manifest
    webhook_manifest = webhook_adapter.get_manifest()
    print(f"Webhook Manifest: {json.dumps(webhook_manifest, indent=2)}")
    
    # Test schema generator
    print("\n5. Testing Schema Generator:")
    print("-" * 30)
    
    from adapters.schema_generator import SchemaGenerator
    
    generator = SchemaGenerator(app)
    all_manifests = generator.generate_all_manifests(agent)
    
    print("Generated Manifests:")
    for name, manifest in all_manifests.items():
        print(f"\n{name.upper()}:")
        print(f"  Keys: {list(manifest.keys())}")
        if name == "openapi":
            print(f"  Title: {manifest.get('info', {}).get('title', 'N/A')}")
        elif name == "mcp":
            print(f"  Protocol Version: {manifest.get('protocolVersion', 'N/A')}")
            print(f"  Tools Count: {len(manifest.get('tools', []))}")
        elif name == "webhook":
            print(f"  Name: {manifest.get('name', 'N/A')}")
            print(f"  Endpoints: {list(manifest.get('endpoints', {}).keys())}")
    
    print("\n✅ All tests completed successfully!")
    print("\n🚀 To run the server:")
    print("   python server.py")
    print("\n🌐 Available endpoints:")
    print("   - GET  / - Server info")
    print("   - POST /agent/chat - Direct agent chat")
    print("   - GET  /agent/schema - Agent schema")
    print("   - POST /mcp/tools/list - MCP tools")
    print("   - POST /mcp/tools/call - MCP tool call")
    print("   - POST /webhook/webhook - Generic webhook")
    print("   - GET  /manifests - All manifests")


if __name__ == "__main__":
    asyncio.run(test_server())
