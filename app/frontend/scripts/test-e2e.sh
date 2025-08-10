#!/bin/bash

# Kill existing processes more aggressively
sudo lsof -ti:5678 | xargs kill -9 2> /dev/null || true
sudo lsof -ti:8000 | xargs kill -9 2> /dev/null || true
pkill -f vite || true
pkill -f node || true
pkill -f python || true
pkill -f uvicorn || true
sleep 1

# Set ports
export VITE_PORT=${VITE_PORT:-5678}
export BACKEND_PORT=${BACKEND_PORT:-8000}

echo "Starting servers on ports: Frontend=$VITE_PORT, Backend=$BACKEND_PORT"

# Start frontend in background
npm run dev:port &
FRONTEND_PID=$!

# Start backend in background
cd ../backend
source ~/miniconda3/etc/profile.d/conda.sh
conda activate AbSequenceAlign
PYTHONPATH=/Users/aquinmx3/repos/AbSequenceAlign/app python -m uvicorn main:app --port $BACKEND_PORT &
BACKEND_PID=$!

cd ../frontend

# Wait for servers with shorter timeout
echo "Waiting for servers to start..."
timeout 30s bash -c 'until curl -s http://localhost:5678 > /dev/null; do sleep 1; done' || echo "Frontend timeout"
timeout 30s bash -c 'until curl -s http://localhost:8000/health > /dev/null; do sleep 1; done' || echo "Backend timeout"

# Run Cypress with optimized settings
echo "Running Cypress tests..."
npx cypress run --config defaultCommandTimeout=5000,requestTimeout=8000,responseTimeout=8000

# Cleanup
kill $FRONTEND_PID 2> /dev/null || true
kill $BACKEND_PID 2> /dev/null || true
pkill -f vite || true
pkill -f uvicorn || true
