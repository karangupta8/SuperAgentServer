# SuperAgentServer Makefile
# Common Docker and development commands

.PHONY: help build up down logs test clean dev prod

# Default target
help:
	@echo "SuperAgentServer - Available Commands:"
	@echo ""
	@echo "🐳 Docker Commands:"
	@echo "  build     - Build the Docker image"
	@echo "  up        - Start the application with Docker Compose"
	@echo "  down      - Stop the application"
	@echo "  logs      - View application logs"
	@echo "  dev       - Start development environment"
	@echo "  prod      - Start production environment"
	@echo "  test      - Test Docker setup"
	@echo "  clean     - Clean up Docker resources"
	@echo ""
	@echo "🔧 Development Commands:"
	@echo "  install   - Install Python dependencies"
	@echo "  run       - Run the application locally"
	@echo "  lint      - Run code linting"
	@echo "  format    - Format code with black and isort"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  docs      - View documentation"
	@echo "  help      - Show this help message"

# Docker Commands
build:
	@echo "🔨 Building Docker image..."
	docker build -t super-agent-server -f docker/Dockerfile .

up:
	@echo "🚀 Starting SuperAgentServer with Docker Compose..."
	docker-compose -f docker/docker-compose.yml up --build

down:
	@echo "🛑 Stopping SuperAgentServer..."
	docker-compose down

logs:
	@echo "📋 Viewing application logs..."
	docker-compose logs -f super-agent-server

dev:
	@echo "🔧 Starting development environment..."
	docker-compose -f docker/docker-compose.yml up --build

prod:
	@echo "🏭 Starting production environment..."
	docker-compose -f docker/docker-compose.prod.yml up -d

test:
	@echo "🧪 Testing Docker setup..."
	python scripts/test_docker.py

clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v
	docker system prune -f
	docker volume prune -f

# Development Commands
install:
	@echo "📦 Installing Python dependencies..."
	pip install -r requirements.txt
	pip install -e .

run:
	@echo "🏃 Running SuperAgentServer locally..."
	python scripts/dev_runner.py

lint:
	@echo "🔍 Running code linting..."
	flake8 src/
	mypy src/

format:
	@echo "✨ Formatting code..."
	black src/ tests/
	isort src/ tests/

# Documentation
docs:
	@echo "📚 Opening documentation..."
	@echo "Deployment Guide: docs/deployment/README.md"
	@echo "Docker Guide: docs/deployment/docker.md"
	@echo "API Documentation: http://localhost:8000/docs (when running)"

# Quick start for new users
quickstart: build up
	@echo "🎉 SuperAgentServer is starting up!"
	@echo "📋 Check logs with: make logs"
	@echo "🌐 API docs will be available at: http://localhost:8000/docs"
	@echo "❤️  Health check: http://localhost:8000/health"
