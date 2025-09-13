from setuptools import setup, find_packages

setup(
    name="super-agent-server",
    version="0.1.0",
    description="Universal Agent Adapter Layer for LangChain agents",
    author="SuperAgentServer Team",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "langchain>=0.1.0",
        "langserve>=0.0.40",
        "pydantic>=2.5.0",
        "python-multipart>=0.0.6",
        "httpx>=0.25.2",
        "websockets>=12.0",
        "python-json-logger>=2.0.7",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
