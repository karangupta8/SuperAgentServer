# scripts/test_structure.py
#!/usr/bin/env python3
"""
Test script to validate the new project structure.
"""

import sys
import os
from pathlib import Path

# Load environment variables from .env file before any imports
from dotenv import load_dotenv
load_dotenv()

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    
    try:
        # Add src to path
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        
        # Test main package import
        from super_agent_server import BaseAgent, AgentRequest, AgentResponse, ExampleAgent
        print("✅ Main package imports work")
        
        # Test server import
        from super_agent_server.server import create_app, app
        print("✅ Server imports work")
        
        # Test adapter imports
        from super_agent_server.adapters import AdapterRegistry, AdapterConfig
        print("✅ Adapter imports work")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_file_structure():
    """Test that all expected files exist."""
    print("\nTesting file structure...")
    
    expected_files = [
        "src/super_agent_server/__init__.py",
        "src/super_agent_server/server.py",
        "src/super_agent_server/agent/__init__.py",
        "src/super_agent_server/agent/base_agent.py",
        "src/super_agent_server/agent/example_agent.py",
        "src/super_agent_server/adapters/__init__.py",
        "src/super_agent_server/adapters/base_adapter.py",
        "src/super_agent_server/adapters/mcp_adapter.py",
        "src/super_agent_server/adapters/webhook_adapter.py",
        "src/super_agent_server/adapters/a2a_adapter.py",
        "src/super_agent_server/adapters/acp_adapter.py",
        "src/super_agent_server/adapters/schema_generator.py",
        "tests/__init__.py",
        "tests/test_server.py",
        "tests/test_websocket.py",
        "scripts/dev_runner.py",
        "scripts/test_websocket.py",
        "config/env.example",
        "pyproject.toml",
        "requirements.txt",
        "LICENSE",
        "README.md"
    ]
    
    all_exist = True
    for file_path in expected_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def test_server_startup():
    """Test that the server can start up."""
    print("\nTesting server startup...")
    
    try:
        # Add src to path
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        
        from super_agent_server.server import create_app
        
        # Create app without agent (should work)
        app = create_app()
        print("✅ Server can be created")
        
        return True
        
    except Exception as e:
        print(f"❌ Server startup error: {e}")
        return False

def main():
    """Run all tests."""
    print("�� Testing SuperAgentServer structure...")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_imports,
        test_server_startup
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("�� All tests passed! The new structure is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())