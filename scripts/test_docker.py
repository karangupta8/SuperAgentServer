#!/usr/bin/env python3
"""
Docker Test Script for SuperAgentServer

This script helps verify that Docker is properly set up and can build the SuperAgentServer image.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and return the result."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            check=True
        )
        print(f"✅ {description} - Success")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"   Error: {e.stderr}")
        return False, e.stderr


def check_docker_installation():
    """Check if Docker is installed and running."""
    print("🐳 Checking Docker installation...")
    
    # Check if docker command exists
    success, output = run_command("docker --version", "Docker version check")
    if not success:
        print("\n❌ Docker is not installed or not in PATH.")
        print("   Please install Docker Desktop from: https://www.docker.com/products/docker-desktop")
        return False
    
    # Check if Docker daemon is running
    success, output = run_command("docker info", "Docker daemon check")
    if not success:
        print("\n❌ Docker daemon is not running.")
        print("   Please start Docker Desktop and ensure it's running.")
        return False
    
    print("✅ Docker is installed and running")
    return True


def check_docker_compose():
    """Check if Docker Compose is available."""
    print("\n🐳 Checking Docker Compose...")
    
    # Try docker compose (newer version)
    success, output = run_command("docker compose version", "Docker Compose version check")
    if success:
        print("✅ Docker Compose is available")
        return True
    
    # Try docker-compose (older version)
    success, output = run_command("docker-compose --version", "Docker Compose (legacy) version check")
    if success:
        print("✅ Docker Compose (legacy) is available")
        return True
    
    print("❌ Docker Compose is not available")
    print("   Please install Docker Compose or update Docker Desktop")
    return False


def check_environment_file():
    """Check if environment file exists."""
    print("\n📄 Checking environment configuration...")
    
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file exists")
        
        # Check if OPENAI_API_KEY is set
        with open(env_file, 'r') as f:
            content = f.read()
            if "OPENAI_API_KEY=your_openai_api_key_here" in content:
                print("⚠️  Warning: OPENAI_API_KEY is not set in .env file")
                print("   Please edit .env and add your OpenAI API key")
                return False
            elif "OPENAI_API_KEY=" in content:
                print("✅ OPENAI_API_KEY is configured")
                return True
    else:
        print("❌ .env file does not exist")
        print("   Please copy config/env.example to .env and configure it")
        return False


def test_docker_build():
    """Test building the Docker image."""
    print("\n🔨 Testing Docker build...")
    
    # Check if Dockerfile exists
    if not Path("docker/Dockerfile").exists():
        print("❌ docker/Dockerfile not found")
        return False
    
    # Build the image
    success, output = run_command(
        "docker build -t super-agent-server-test .", 
        "Docker image build"
    )
    
    if success:
        print("✅ Docker image built successfully")
        
        # Clean up test image
        run_command("docker rmi super-agent-server-test", "Cleanup test image")
        return True
    else:
        print("❌ Docker build failed")
        return False


def test_docker_compose():
    """Test Docker Compose configuration."""
    print("\n🐳 Testing Docker Compose configuration...")
    
    # Check if docker-compose.yml exists
    if not Path("docker/docker-compose.yml").exists():
        print("❌ docker/docker-compose.yml not found")
        return False
    
    # Validate compose file
    success, output = run_command(
        "docker compose config", 
        "Docker Compose configuration validation"
    )
    
    if success:
        print("✅ Docker Compose configuration is valid")
        return True
    else:
        print("❌ Docker Compose configuration is invalid")
        return False


def main():
    """Main test function."""
    print("🚀 SuperAgentServer Docker Test")
    print("=" * 50)
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"📁 Working directory: {project_root}")
    
    tests = [
        ("Docker Installation", check_docker_installation),
        ("Docker Compose", check_docker_compose),
        ("Environment Configuration", check_environment_file),
        ("Docker Build", test_docker_build),
        ("Docker Compose Config", test_docker_compose),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} - Error: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Docker setup is ready.")
        print("\n🚀 Next steps:")
        print("   1. Edit .env file with your OpenAI API key")
        print("   2. Run: docker-compose up --build")
        print("   3. Test: curl http://localhost:8000/health")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\n📚 For help, see: docs/deployment/docker.md")
    
    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
