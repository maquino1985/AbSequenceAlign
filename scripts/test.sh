#!/bin/bash

# AbSequenceAlign Test Script

set -e

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run setup first:"
    echo "   ./scripts/setup.sh"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "❌ Dependencies not installed. Run setup first:"
    echo "   ./scripts/setup.sh"
    exit 1
fi

echo "🧪 Running AbSequenceAlign tests..."
echo ""

# Check if server is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Server is running, proceeding with tests..."
else
    echo "⚠️  Server is not running. Starting server in background..."
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    SERVER_PID=$!
    
    # Wait for server to start
    echo "⏳ Waiting for server to start..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✅ Server started successfully"
            break
        fi
        sleep 1
    done
    
    # Check if server started
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "❌ Failed to start server"
        exit 1
    fi
fi

# Run tests
echo "🧪 Running Phase 1 tests..."
python test_phase1.py

# Clean up if we started the server
if [ ! -z "$SERVER_PID" ]; then
    echo "🛑 Stopping test server..."
    kill $SERVER_PID
fi

echo ""
echo "✅ Tests completed!" 