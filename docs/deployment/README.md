# Deployment Guide

Complete guide for deploying SuperAgentServer in various environments.

## Overview

This guide covers deploying SuperAgentServer in different environments, from development to production, including Docker, cloud platforms, and monitoring.

## Quick Navigation

- **[🐳 Docker](docker.md)** - Container-based deployment (Recommended)
- **[Production](production.md)** - Production deployment best practices
- **[Cloud Platforms](cloud/README.md)** - AWS, GCP, Azure deployment
- **[Monitoring](monitoring.md)** - Logging, metrics, and observability

## Deployment Options

### 1. Local Development
- **Purpose**: Development and testing
- **Requirements**: Python 3.8+, virtual environment
- **Best for**: Individual developers, testing

### 2. Docker (Recommended)
- **Purpose**: Containerized deployment
- **Requirements**: Docker, Docker Compose
- **Best for**: Consistent environments, easy scaling, production deployment

### 3. Cloud Platforms
- **Purpose**: Scalable, managed deployment
- **Requirements**: Cloud account, container registry
- **Best for**: Production, high availability

### 4. Kubernetes
- **Purpose**: Orchestrated container deployment
- **Requirements**: Kubernetes cluster
- **Best for**: Enterprise, complex deployments

## Prerequisites

### System Requirements

- **CPU**: 1+ cores (2+ recommended for production)
- **Memory**: 512MB+ (2GB+ recommended for production)
- **Storage**: 1GB+ free space
- **Network**: Internet access for API calls

### Software Requirements

- **Python**: 3.8 or higher
- **Docker**: 20.10+ (for containerized deployment)
- **Git**: For cloning the repository

### Environment Variables

Required environment variables:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
HOST=0.0.0.0
PORT=8000
DEBUG=False
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://your-domain.com
```

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/superagentserver/super-agent-server.git
cd super-agent-server

# Configure environment
cp config/env.example .env
# Edit .env with your OpenAI API key

# Build and run with Docker
docker-compose up --build
```

### Option 2: Local Installation

```bash
# Clone and install
git clone https://github.com/superagentserver/super-agent-server.git
cd super-agent-server
pip install -r requirements.txt
pip install -e .

# Configure environment
cp config/env.example .env
# Edit .env with your settings

# Run the server
python scripts/dev_runner.py
```

## Production Checklist

### Security
- [ ] Set strong API keys
- [ ] Configure CORS properly
- [ ] Enable HTTPS
- [ ] Set up authentication
- [ ] Configure rate limiting
- [ ] Update dependencies regularly

### Performance
- [ ] Use production WSGI server (Gunicorn)
- [ ] Configure proper logging
- [ ] Set up monitoring
- [ ] Optimize database connections
- [ ] Configure caching

### Reliability
- [ ] Set up health checks
- [ ] Configure auto-restart
- [ ] Set up backup procedures
- [ ] Test failover scenarios
- [ ] Monitor resource usage

### Scalability
- [ ] Use load balancer
- [ ] Configure horizontal scaling
- [ ] Set up container orchestration
- [ ] Monitor performance metrics
- [ ] Plan for traffic spikes

## Environment-Specific Guides

### Development

```bash
# Quick start for development
git clone https://github.com/superagentserver/super-agent-server.git
cd super-agent-server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
cp config/env.example .env
# Edit .env
python scripts/dev_runner.py
```

### Staging

```bash
# Staging deployment
export ENVIRONMENT=staging
export DEBUG=True
export LOG_LEVEL=INFO
export ALLOWED_ORIGINS=https://staging.your-domain.com
python scripts/dev_runner.py
```

### Production

```bash
# Production deployment
export ENVIRONMENT=production
export DEBUG=False
export LOG_LEVEL=WARNING
export ALLOWED_ORIGINS=https://your-domain.com
gunicorn super_agent_server.server:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Monitoring and Observability

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/

# Adapter status
curl http://localhost:8000/adapters
```

### Logging

```bash
# View logs
tail -f logs/super_agent_server.log

# Filter error logs
grep "ERROR" logs/super_agent_server.log

# Monitor in real-time
tail -f logs/super_agent_server.log | grep -E "(ERROR|WARNING)"
```

### Metrics

Key metrics to monitor:

- **Response time**: Average response time per endpoint
- **Throughput**: Requests per second
- **Error rate**: Percentage of failed requests
- **Memory usage**: RAM consumption
- **CPU usage**: CPU utilization
- **Active connections**: Number of concurrent connections

## Troubleshooting

### Common Issues

**Server won't start:**
```bash
# Check if port is available
lsof -i :8000

# Check Python version
python --version

# Check dependencies
pip list | grep super-agent-server
```

**Agent not responding:**
```bash
# Check OpenAI API key
echo $OPENAI_API_KEY

# Check agent status
curl http://localhost:8000/health

# Check logs
tail -f logs/super_agent_server.log
```

**Performance issues:**
```bash
# Check resource usage
htop

# Check memory usage
free -h

# Check disk usage
df -h
```

### Debug Mode

```bash
# Enable debug logging
export DEBUG=True
export LOG_LEVEL=DEBUG
python scripts/dev_runner.py
```

### Log Analysis

```bash
# Count errors
grep -c "ERROR" logs/super_agent_server.log

# Find most common errors
grep "ERROR" logs/super_agent_server.log | sort | uniq -c | sort -nr

# Monitor real-time errors
tail -f logs/super_agent_server.log | grep "ERROR"
```

## Security Considerations

### API Security

- **Authentication**: Implement proper authentication
- **Authorization**: Control access to endpoints
- **Rate Limiting**: Prevent abuse
- **Input Validation**: Validate all inputs
- **HTTPS**: Use secure connections

### Data Security

- **Environment Variables**: Store secrets securely
- **API Keys**: Rotate regularly
- **Logs**: Don't log sensitive data
- **Backups**: Secure backup storage

### Network Security

- **Firewall**: Configure properly
- **CORS**: Restrict origins
- **VPN**: Use for internal communication
- **Load Balancer**: SSL termination

## Backup and Recovery

### Backup Strategy

```bash
# Backup configuration
cp -r config/ backups/config-$(date +%Y%m%d)/

# Backup logs
cp -r logs/ backups/logs-$(date +%Y%m%d)/

# Backup environment
cp .env backups/env-$(date +%Y%m%d)/
```

### Recovery Procedures

```bash
# Restore from backup
cp -r backups/config-20240115/* config/
cp -r backups/logs-20240115/* logs/
cp backups/env-20240115 .env

# Restart services
systemctl restart super-agent-server
```

## Scaling Considerations

### Horizontal Scaling

```yaml
# docker-compose.yml for scaling
version: '3.8'
services:
  super-agent-server:
    image: super-agent-server:latest
    deploy:
      replicas: 3
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

### Load Balancing

```nginx
# nginx.conf
upstream super_agent_server {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://super_agent_server;
    }
}
```

## Next Steps

- **[Docker Deployment](docker.md)** - Containerized deployment guide
- **[Production Setup](production.md)** - Production deployment best practices
- **[Cloud Deployment](cloud/README.md)** - Cloud platform deployment
- **[Monitoring Setup](monitoring.md)** - Observability and monitoring
