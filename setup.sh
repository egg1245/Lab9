#!/bin/bash
# DormChef Quick Setup Script for Ubuntu 24.04
# Устанавливает зависимости и готовит окружение для запуска

set -e

echo "🍳 DormChef Setup Starting..."

# Check if Python 3.11+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION found"

# Check if venv module is available, install if not
if ! python3 -m venv --help &> /dev/null; then
    echo "📦 Installing python3-venv..."
    apt-get update -qq && apt-get install -y python3-venv > /dev/null 2>&1
fi

# Remove old venv if broken
if [ -d "venv" ] && [ ! -f "venv/bin/python" ]; then
    echo "🔄 Removing broken venv..."
    rm -rf venv
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✓ Virtual environment already exists"
fi

# Upgrade pip and install requirements
echo "⬆️  Upgrading pip..."
venv/bin/pip install --upgrade pip setuptools wheel -q

# Install Python dependencies
echo "📥 Installing Python dependencies..."
venv/bin/pip install -q -r backend/requirements.txt

# Check if PostgreSQL is available
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL client not found, but it can run in Docker"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps (for Ubuntu VM):"
echo "  bash start.sh"
echo ""
echo "Or manual steps:"
echo "  1. cp .env.example .env"
echo "  2. docker run -d --name dormchef-pg -e POSTGRES_PASSWORD=dormchef -p 5432:5432 postgres:16-alpine"
echo "  3. venv/bin/python backend/main.py &"
echo "  4. bash test.sh"
