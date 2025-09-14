# docs/DEPLOYMENT.md
# Deployment Guide for SuperAgentServer

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/superagentserver/super-agent-server.git
cd super-agent-server

# Set up environment
cp config/env.example .env
# Edit .env with your OpenAI API key

# Run with Docker Compose
docker-compose up -d
```

### Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt
pip install -e .

# Run the server
python scripts/dev_runner.py
```

## Production Deployment

### Using Docker

```bash
# Build the image
docker build -t super-agent-server .

# Run the container
docker run -d \
  --name super-agent-server \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  super-agent-server
```

### Using Systemd

```ini
# /etc/systemd/system/super-agent-server.service
[Unit]
Description=SuperAgentServer
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/opt/super-agent-server
ExecStart=/opt/super-agent-server/venv/bin/uvicorn super_agent_server.server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | - | Yes |
| `HOST` | Server host | 0.0.0.0 | No |
| `PORT` | Server port | 8000 | No |
| `DEBUG` | Debug mode | True | No |
| `LOG_LEVEL` | Logging level | INFO | No |

## Health Checks

The server provides health check endpoints:

- `GET /health` - Basic health check
- `GET /` - Server information

## Monitoring

### Logs
- Application logs: `logs/super_agent_server.log`
- Access logs: Available via uvicorn

### Metrics
- Health endpoint: `http://localhost:8000/health`
- Server info: `http://localhost:8000/`

## Troubleshooting

### Common Issues

1. **OpenAI API Key not set**
   - Ensure `OPENAI_API_KEY` is set in environment or .env file

2. **Port already in use**
   - Change the `PORT` environment variable
   - Or stop the process using the port

3. **Permission denied**
   - Ensure the user has proper permissions
   - Check file ownership

### Debug Mode

Enable debug mode for detailed logging:

```bash
export DEBUG=True
export LOG_LEVEL=DEBUG
python scripts/dev_runner.py
```
