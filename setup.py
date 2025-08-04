"""
Setup script for Axura RAG System
"""
from setuptools import setup, find_packages

setup(
    name="axura-rag",
    version="1.0.0",
    description="Retrieval-Augmented Generation system for Axura business data",
    author="Axura Team",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "python-multipart==0.0.6",
        "pydantic==2.5.0",
        "openai==1.3.7",
        "tiktoken==0.5.1",
        "chromadb==0.4.18",
        "langchain==0.0.350",
        "langchain-text-splitters==0.0.1",
        "langchain-openai==0.0.2",
        "pandas==2.1.4",
        "numpy==1.24.3",
        "python-docx==1.1.0",
        "PyPDF2==3.0.1",
        "openpyxl==3.1.2",
        "pymongo==4.6.0",
        "motor==3.3.2",
        "python-dotenv==1.0.0",
        "httpx==0.25.2",
        "aiofiles==23.2.1"
    ],
    extras_require={
        "dev": [
            "pytest==7.4.3",
            "pytest-asyncio==0.21.1"
        ]
    },
    python_requires=">=3.8",
) 