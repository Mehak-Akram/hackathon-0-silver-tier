#!/bin/bash
# Startup script for Gold Tier Autonomous AI Employee

echo "=========================================="
echo "Gold Tier Autonomous AI Employee"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Creating..."
    python -m venv .venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your credentials before continuing"
    exit 1
fi

# Create required directories
echo "📁 Creating required directories..."
mkdir -p Needs_Action Plans Done Pending_Approval Briefings Audit_Logs logs

echo ""
echo "=========================================="
echo "Starting Gold Tier AI Employee..."
echo "=========================================="
echo ""

# Start MCP server in background
echo "🚀 Starting MCP Server..."
python mcp_server/server.py > logs/mcp-server.log 2>&1 &
MCP_PID=$!
echo "   MCP Server PID: $MCP_PID"

# Wait a moment for MCP server to start
sleep 2

# Start orchestrator
echo "🚀 Starting Orchestrator..."
python orchestrator/main.py

# Cleanup on exit
echo ""
echo "Shutting down..."
kill $MCP_PID 2>/dev/null
echo "✅ Stopped"
