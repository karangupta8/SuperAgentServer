# Scripts

This directory contains utility scripts for SuperAgentServer.

## Available Scripts

- `dev_runner.py` - Development server runner
- `telegram_setup.py` - Telegram bot setup utility
- `test_webhook_runner.py` - Webhook testing utility
- `test_websocket.py` - WebSocket testing utility
- `test_docker.py` - Docker setup testing utility

## Docker Testing

The `test_docker.py` script helps verify that Docker is properly set up and can build the SuperAgentServer image.

### Usage

```bash
# Test Docker setup
python scripts/test_docker.py

# Or use the Makefile
make test
```

### What it checks

- Docker installation and daemon status
- Docker Compose availability
- Environment configuration
- Docker image build capability
- Docker Compose configuration validity

### Example Output

```
🚀 SuperAgentServer Docker Test
==================================================
📁 Working directory: /path/to/super-agent-server
🐳 Checking Docker installation...
✅ Docker version check - Success
✅ Docker daemon check - Success
✅ Docker is installed and running

🐳 Checking Docker Compose...
✅ Docker Compose version check - Success
✅ Docker Compose is available

📄 Checking environment configuration...
✅ .env file exists
✅ OPENAI_API_KEY is configured

🔨 Testing Docker build...
✅ Docker image build - Success
✅ Docker image built successfully

🐳 Testing Docker Compose configuration...
✅ Docker Compose configuration validation - Success
✅ Docker Compose configuration is valid

==================================================
📊 Test Summary
==================================================
✅ PASS Docker Installation
✅ PASS Docker Compose
✅ PASS Environment Configuration
✅ PASS Docker Build
✅ PASS Docker Compose Config

🎯 Results: 5/5 tests passed

🎉 All tests passed! Docker setup is ready.

🚀 Next steps:
   1. Edit .env file with your OpenAI API key
   2. Run: docker-compose up --build
   3. Test: curl http://localhost:8000/health
```
