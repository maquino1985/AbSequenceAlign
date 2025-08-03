#!/bin/bash

# AbSequenceAlign Development Script

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

echo "🚀 Starting AbSequenceAlign in development mode..."
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the application with auto-reload
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 