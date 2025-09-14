# Docker Deployment Guide

Complete guide for deploying SuperAgentServer using Docker and Docker Compose.

## Overview

This guide covers containerized deployment of SuperAgentServer using Docker, including development, staging, and production environments.

## Prerequisites

- Docker 20.10+ installed
- Docker Compose 2.0+ installed
- Git (for cloning the repository)

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/superagentserver/super-agent-server.git
cd super-agent-server
```

### 2. Environment Configuration

```bash
# Copy the example environment file
cp config/env.example .env

# Edit the environment file with your settings
nano .env
```

**Required environment variables:**
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional but recommended
ALLOWED_ORIGINS=https://your-domain.com
DEBUG=False
LOG_LEVEL=INFO
```

### 3. Build and Run

```bash
# Build and start the container
docker-compose -f docker/docker-compose.yml up --build

# Or run in detached mode
docker-compose -f docker/docker-compose.yml up -d --build
```

### 4. Verify Deployment

```bash
# Check if the service is running
docker-compose ps

# Test the health endpoint
curl http://localhost:8000/health

# View logs
docker-compose logs -f super-agent-server
```

### Quick Test

```bash
# Test your Docker setup
python scripts/test_docker.py

# Or use the Makefile
make test
```

## Docker Commands Reference

### Using Makefile (Recommended)

```bash
# Quick start
make quickstart

# Development
make dev

# Production
make prod

# View logs
make logs

# Stop services
make down

# Clean up
make clean

# Test setup
make test
```

### Basic Operations

```bash
# Build the image
docker build -t super-agent-server -f docker/Dockerfile .

# Run a container
docker run -p 8000:8000 --env-file .env super-agent-server

# Run with specific environment variables
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  -e DEBUG=False \
  super-agent-server
```

### Docker Compose Operations

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f super-agent-server

# Scale the service
docker-compose up --scale super-agent-server=3

# Execute commands in running container
docker-compose exec super-agent-server bash
```

## Environment Configurations

### Development Environment

```bash
# Use the default docker-compose.yml
docker-compose up --build
```

**Environment variables for development:**
```bash
DEBUG=True
LOG_LEVEL=DEBUG
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Staging Environment

```bash
# Use staging-specific compose file
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up
```

### Production Environment

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d
```

**Environment variables for production:**
```bash
DEBUG=False
LOG_LEVEL=WARNING
ALLOWED_ORIGINS=https://your-domain.com
MODEL_NAME=gpt-4
```

## Advanced Configuration

### Custom Dockerfile

Create a custom Dockerfile for specific needs:

```dockerfile
FROM python:3.11-slim

# Install additional system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "super_agent_server.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Multi-stage Build

For optimized production images:

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application
COPY . .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "super_agent_server.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Production Deployment

### Using Production Compose

The `docker-compose.prod.yml` includes:

- **Nginx reverse proxy** for SSL termination and load balancing
- **Redis** for caching and session storage
- **PostgreSQL** for data persistence
- **Prometheus** for metrics collection
- **Grafana** for monitoring dashboards

### Setup Production Environment

1. **Configure environment variables:**
```bash
# Create production environment file
cp config/env.example .env.prod

# Set production values
OPENAI_API_KEY=your_production_key
ALLOWED_ORIGINS=https://your-domain.com
DEBUG=False
LOG_LEVEL=WARNING
POSTGRES_PASSWORD=secure_password
REDIS_PASSWORD=secure_redis_password
GRAFANA_PASSWORD=secure_grafana_password
```

2. **Start production services:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Configure SSL certificates:**
```bash
# Place your SSL certificates in ./ssl/
mkdir ssl
cp your-cert.pem ssl/
cp your-key.pem ssl/
```

### Nginx Configuration

Create `nginx.conf` for the reverse proxy:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream super_agent_server {
        server super-agent-server:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/your-cert.pem;
        ssl_certificate_key /etc/nginx/ssl/your-key.pem;

        location / {
            proxy_pass http://super_agent_server;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## Monitoring and Logging

### Health Checks

The Dockerfile includes a health check:

```dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1
```

### Log Management

```bash
# View real-time logs
docker-compose logs -f super-agent-server

# View logs with timestamps
docker-compose logs -t super-agent-server

# Save logs to file
docker-compose logs super-agent-server > logs/app.log

# Rotate logs (add to crontab)
0 0 * * * docker-compose logs --since=24h super-agent-server > logs/app-$(date +\%Y\%m\%d).log
```

### Monitoring with Prometheus

Access Prometheus at `http://localhost:9090` and Grafana at `http://localhost:3000`.

## Scaling

### Horizontal Scaling

```bash
# Scale to 3 instances
docker-compose up --scale super-agent-server=3

# Use with load balancer
docker-compose -f docker-compose.yml -f docker-compose.scale.yml up
```

### Resource Limits

```yaml
# In docker-compose.yml
services:
  super-agent-server:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
```

## Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check logs
docker-compose logs super-agent-server

# Check if port is available
netstat -tulpn | grep :8000

# Check environment variables
docker-compose config
```

**Health check failing:**
```bash
# Test health endpoint manually
docker-compose exec super-agent-server curl http://localhost:8000/health

# Check if the app is running
docker-compose exec super-agent-server ps aux
```

**Out of memory:**
```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G
```

### Debug Mode

```bash
# Run with debug logging
docker-compose run -e DEBUG=True -e LOG_LEVEL=DEBUG super-agent-server

# Access container shell
docker-compose exec super-agent-server bash

# Check Python environment
docker-compose exec super-agent-server python -c "import sys; print(sys.path)"
```

## Security Best Practices

### Container Security

1. **Use non-root user** (already configured in Dockerfile)
2. **Keep base image updated**
3. **Scan for vulnerabilities:**
```bash
docker scan super-agent-server
```

### Environment Security

1. **Use secrets management:**
```bash
# Create secrets
echo "your_openai_key" | docker secret create openai_key -

# Use in compose
services:
  super-agent-server:
    secrets:
      - openai_key
    environment:
      - OPENAI_API_KEY_FILE=/run/secrets/openai_key
```

2. **Network isolation:**
```yaml
networks:
  super-agent-network:
    driver: bridge
    internal: true  # No external access
```

### Data Security

1. **Encrypt volumes:**
```bash
# Create encrypted volume
docker volume create --driver local \
  --opt type=tmpfs \
  --opt device=tmpfs \
  --opt o=size=1g,uid=1000,gid=1000 \
  encrypted_data
```

2. **Backup strategies:**
```bash
# Backup volumes
docker run --rm -v super_agent_server_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/data-backup.tar.gz -C /data .

# Restore volumes
docker run --rm -v super_agent_server_data:/data -v $(pwd):/backup alpine \
  tar xzf /backup/data-backup.tar.gz -C /data
```

## Performance Optimization

### Image Optimization

1. **Use multi-stage builds** (see example above)
2. **Minimize layers:**
```dockerfile
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean
```

3. **Use .dockerignore** (already configured)

### Runtime Optimization

1. **Set appropriate resource limits**
2. **Use health checks**
3. **Configure logging levels**
4. **Enable gzip compression in Nginx**

## Backup and Recovery

### Backup Script

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/$DATE"

mkdir -p "$BACKUP_DIR"

# Backup volumes
docker-compose exec -T postgres pg_dump -U super_agent super_agent_server > "$BACKUP_DIR/database.sql"
docker-compose exec -T redis redis-cli --rdb - > "$BACKUP_DIR/redis.rdb"

# Backup configuration
cp .env "$BACKUP_DIR/"
cp docker-compose*.yml "$BACKUP_DIR/"

# Backup logs
docker-compose logs --since=24h > "$BACKUP_DIR/logs.txt"

echo "Backup completed: $BACKUP_DIR"
```

### Recovery Script

```bash
#!/bin/bash
# restore.sh

BACKUP_DIR=$1

if [ -z "$BACKUP_DIR" ]; then
    echo "Usage: $0 <backup_directory>"
    exit 1
fi

# Restore database
docker-compose exec -T postgres psql -U super_agent super_agent_server < "$BACKUP_DIR/database.sql"

# Restore Redis
docker-compose exec -T redis redis-cli --pipe < "$BACKUP_DIR/redis.rdb"

# Restore configuration
cp "$BACKUP_DIR/.env" ./
cp "$BACKUP_DIR/docker-compose*.yml" ./

echo "Recovery completed from: $BACKUP_DIR"
```

## Next Steps

- **[Production Deployment](production.md)** - Production deployment best practices
- **[Cloud Deployment](cloud/README.md)** - Cloud platform deployment
- **[Monitoring Setup](monitoring.md)** - Observability and monitoring
