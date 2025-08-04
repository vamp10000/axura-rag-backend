#!/bin/bash

# Axura RAG System Installation Script
echo "🚀 Installing Axura RAG System..."

# Check if Python 3.8+ is installed
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
if [ "$(echo "$python_version >= 3.8" | bc -l)" -eq 0 ]; then
    echo "❌ Python 3.8 or higher is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file..."
    cp env.example .env
    echo "📝 Please edit .env file with your configuration"
fi

# Create chroma_db directory
echo "🗄️ Creating ChromaDB directory..."
mkdir -p chroma_db

echo "✅ Installation completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the server: uvicorn app.main:app --reload"
echo "4. Access the API docs: http://localhost:8000/docs"
echo ""
echo "🔗 For more information, see README.md" 