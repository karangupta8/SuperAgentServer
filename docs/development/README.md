# Development Guide

Complete guide for contributing to SuperAgentServer development.

## Overview

This guide covers everything you need to know about contributing to SuperAgentServer, including setup, coding standards, testing, and release processes.

## Quick Navigation

- **[Contributing](contributing.md)** - How to contribute to the project
- **[Architecture](architecture.md)** - System design and architecture
- **[Testing](testing.md)** - Testing guidelines and practices
- **[Release Process](release-process.md)** - Release and deployment process

## Development Setup

### Prerequisites

- **Python**: 3.8 or higher
- **Git**: For version control
- **Docker**: For containerized development (optional)
- **IDE**: VS Code, PyCharm, or your preferred editor

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/your-username/super-agent-server.git
cd super-agent-server

# Add upstream remote
git remote add upstream https://github.com/superagentserver/super-agent-server.git
```

### 2. Create Development Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r config/requirements-dev.txt

# Install in development mode
pip install -e .
```

### 3. Set Up Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files
```

### 4. Configure Environment

```bash
# Copy environment template
cp config/env.example .env

# Edit with your settings
# Add your OpenAI API key for testing
```

## Development Workflow

### 1. Create a Feature Branch

```bash
# Create and switch to feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

### 2. Make Changes

```bash
# Make your changes
# Write code, tests, documentation

# Check code quality
pre-commit run --all-files

# Run tests
pytest tests/

# Run specific tests
pytest tests/test_your_feature.py
```

### 3. Commit Changes

```bash
# Add changes
git add .

# Commit with descriptive message
git commit -m "feat: add new feature description"

# Push to your fork
git push origin feature/your-feature-name
```

### 4. Create Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Fill out the PR template
4. Request review from maintainers

## Coding Standards

### Python Style

We use **Black** for code formatting and **isort** for import sorting.

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check formatting
black --check src/ tests/
isort --check-only src/ tests/
```

### Code Quality

We use **flake8** for linting and **mypy** for type checking.

```bash
# Run linter
flake8 src/ tests/

# Run type checker
mypy src/

# Run all quality checks
pre-commit run --all-files
```

### Documentation

- Use **Google-style docstrings**
- Include **type hints** for all functions
- Write **clear, concise comments**
- Update **README files** when needed

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Example function with proper documentation.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is empty
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    
    return param2 > 0
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/super_agent_server --cov-report=html

# Run specific test file
pytest tests/test_server.py

# Run specific test
pytest tests/test_server.py::test_root_endpoint

# Run with verbose output
pytest -v
```

### Writing Tests

```python
"""
Test example for new features.
"""

import pytest
from unittest.mock import Mock, patch
from super_agent_server.agent import BaseAgent, AgentRequest, AgentResponse


class TestNewFeature:
    """Test cases for new feature."""
    
    def test_feature_initialization(self):
        """Test feature initializes correctly."""
        feature = NewFeature()
        assert feature is not None
    
    @pytest.mark.asyncio
    async def test_feature_processing(self):
        """Test feature processing."""
        feature = NewFeature()
        await feature.initialize()
        
        request = AgentRequest(message="test")
        response = await feature.process(request)
        
        assert response.message is not None
    
    def test_feature_with_mock(self):
        """Test feature with mocked dependencies."""
        with patch('super_agent_server.external_service') as mock_service:
            mock_service.return_value = "mocked_response"
            
            feature = NewFeature()
            result = feature.call_external_service()
            
            assert result == "mocked_response"
            mock_service.assert_called_once()
```

### Test Categories

- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Test performance characteristics

## Architecture

### System Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │    │   Web Browsers  │    │  External APIs  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │     SuperAgentServer      │
                    │                           │
                    │  ┌─────────────────────┐  │
                    │  │   FastAPI Server    │  │
                    │  └─────────┬───────────┘  │
                    │            │              │
                    │  ┌─────────▼───────────┐  │
                    │  │   Adapter Registry  │  │
                    │  └─────────┬───────────┘  │
                    │            │              │
                    │  ┌─────────▼───────────┐  │
                    │  │   Agent System      │  │
                    │  └─────────────────────┘  │
                    └───────────────────────────┘
```

### Key Components

1. **FastAPI Server**: Main web server
2. **Adapter Registry**: Manages protocol adapters
3. **Agent System**: Core agent functionality
4. **Configuration**: Settings and environment management

### Design Principles

- **Modularity**: Components are loosely coupled
- **Extensibility**: Easy to add new adapters and agents
- **Testability**: All components are testable
- **Performance**: Optimized for high throughput
- **Reliability**: Robust error handling and recovery

## Release Process

### Version Numbering

We use **Semantic Versioning** (SemVer):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. **Update Version**
   ```bash
   # Update version in pyproject.toml
   # Update CHANGELOG.md
   # Commit changes
   git commit -m "chore: bump version to 1.2.0"
   ```

2. **Create Release Branch**
   ```bash
   git checkout -b release/1.2.0
   git push origin release/1.2.0
   ```

3. **Run Tests**
   ```bash
   pytest tests/
   pre-commit run --all-files
   ```

4. **Create Release**
   ```bash
   # Create tag
   git tag -a v1.2.0 -m "Release version 1.2.0"
   git push origin v1.2.0
   
   # Create GitHub release
   # Upload packages to PyPI
   ```

### Automated Releases

We use GitHub Actions for automated releases:

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        run: twine upload dist/*
```

## Contributing Guidelines

### Pull Request Process

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests for new functionality**
5. **Update documentation**
6. **Run all tests and checks**
7. **Submit a pull request**

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] All existing tests still pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Code Review Process

1. **Automated Checks**: CI/CD runs all tests and checks
2. **Manual Review**: Maintainers review code
3. **Feedback**: Address any feedback
4. **Approval**: Maintainer approves the PR
5. **Merge**: PR is merged into main branch

## Development Tools

### VS Code Configuration

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## Troubleshooting

### Common Issues

**Tests failing:**
```bash
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Run tests with verbose output
pytest -v
```

**Pre-commit hooks failing:**
```bash
# Run hooks manually
pre-commit run --all-files

# Skip hooks temporarily
git commit --no-verify -m "commit message"
```

**Import errors:**
```bash
# Check if package is installed
pip list | grep super-agent-server

# Reinstall in development mode
pip install -e .
```

### Getting Help

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Documentation**: Check the docs for answers
- **Code Review**: Learn from code reviews

## Next Steps

- **[Contributing Guide](contributing.md)** - Detailed contribution guidelines
- **[Architecture Documentation](architecture.md)** - System design details
- **[Testing Guide](testing.md)** - Testing best practices
- **[Release Process](release-process.md)** - Release and deployment
