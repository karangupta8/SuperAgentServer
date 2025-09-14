# Installation Guide

This guide will help you install SuperAgentServer on your system.

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: At least 512MB RAM
- **Disk Space**: At least 100MB free space

## Installation Methods

### Method 1: From Source (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/superagentserver/super-agent-server.git
   cd super-agent-server
   ```

2. **Create a virtual environment:**
   ```bash
   # Using venv
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r config/requirements-dev.txt
   ```

4. **Install the package in development mode:**
   ```bash
   pip install -e .
   ```

### Method 2: Using pip (Future)

Once published to PyPI:
```bash
pip install super-agent-server
```

### Method 3: Using Docker

1. **Clone the repository:**
   ```bash
   git clone https://github.com/superagentserver/super-agent-server.git
   cd super-agent-server
   ```

2. **Build the Docker image:**
   ```bash
   docker build -t super-agent-server .
   ```

3. **Run the container:**
   ```bash
   docker run -p 8000:8000 -e OPENAI_API_KEY=your_key_here super-agent-server
   ```

## Verify Installation

1. **Check Python version:**
   ```bash
   python --version
   # Should show Python 3.8 or higher
   ```

2. **Test the installation:**
   ```bash
   python -c "import super_agent_server; print('Installation successful!')"
   ```

3. **Run the test suite:**
   ```bash
   pytest tests/
   ```

## Configuration

1. **Copy the environment template:**
   ```bash
   cp config/env.example .env
   ```

2. **Edit the environment file:**
   ```bash
   # Edit .env and add your OpenAI API key
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Troubleshooting

### Common Issues

**Issue: Python version too old**
```bash
# Solution: Install Python 3.8+
# On Ubuntu/Debian:
sudo apt update
sudo apt install python3.8 python3.8-venv

# On macOS with Homebrew:
brew install python@3.8
```

**Issue: Permission denied during installation**
```bash
# Solution: Use --user flag or virtual environment
pip install --user -r requirements.txt
# OR
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Issue: Missing system dependencies**
```bash
# On Ubuntu/Debian:
sudo apt install build-essential python3-dev

# On macOS:
xcode-select --install
```

**Issue: Import errors after installation**
```bash
# Solution: Ensure you're in the correct environment
which python
# Should point to your virtual environment
```

### Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](../reference/troubleshooting.md)
2. Search existing [GitHub Issues](https://github.com/superagentserver/super-agent-server/issues)
3. Create a new issue with:
   - Your operating system
   - Python version
   - Full error message
   - Steps to reproduce

## Next Steps

Once installation is complete, proceed to the [Quick Start Guide](quick-start.md) to get your first agent running!
