#!/bin/bash
# DormChef Start Script
# Запускает все необходимые сервисы

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🍳 DormChef Starting...${NC}"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo "📝 Edit .env and add your OPENAI_API_KEY if needed"
fi

# Load environment
set -a
source .env
set +a

# Check virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Virtual environment not found. Running setup...${NC}"
    sudo bash setup.sh
fi

# Start PostgreSQL container if not running
if ! docker ps | grep -q dormchef-db; then
    echo -e "${YELLOW}🐘 Starting PostgreSQL container...${NC}"
    docker run -d \
        --name dormchef-db \
        -e POSTGRES_USER=dormchef \
        -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-dormchef} \
        -e POSTGRES_DB=dormchef \
        -p 5432:5432 \
        postgres:16-alpine
    
    echo "⏳ Waiting for PostgreSQL to be ready..."
    sleep 10
else
    echo -e "${GREEN}✓ PostgreSQL already running${NC}"
fi

# Start FastAPI backend
echo -e "${BLUE}🚀 Starting FastAPI backend on http://localhost:8000...${NC}"
cd backend
../venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
