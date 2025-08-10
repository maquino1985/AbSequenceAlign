#!/bin/bash

# Function to find an available port
find_available_port() {
  local port=$1
  while true; do
    if ! lsof -i :$port > /dev/null 2>&1; then
      echo $port
      return
    fi
    ((port++))
  done
}

# Find available ports
VITE_PORT=$(find_available_port 5678)
BACKEND_PORT=$(find_available_port 8000)

echo "Using frontend port: $VITE_PORT"
echo "Using backend port: $BACKEND_PORT"

# Export ports for other processes to use
export VITE_PORT=$VITE_PORT
export BACKEND_PORT=$BACKEND_PORT

# Kill any existing processes
cleanup() {
  echo "Cleaning up processes..."
  sudo lsof -ti:$VITE_PORT,$BACKEND_PORT | xargs kill -9 2>/dev/null || true
  pkill -f vite
  pkill -f node
  pkill -f python
  pkill -f uvicorn
  sleep 2
}

# Set up cleanup on script exit
trap cleanup EXIT

# Initial cleanup
cleanup

# Start backend server
cd ../backend
PYTHONPATH=/Users/aquinmx3/repos/AbSequenceAlign/app python -m uvicorn main:app --port $BACKEND_PORT &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend server..."
MAX_RETRIES=30
COUNT=0
while ! curl -s http://localhost:$BACKEND_PORT/health >/dev/null; do
  ((COUNT++))
  if [ $COUNT -eq $MAX_RETRIES ]; then
    echo "Backend server failed to start"
    exit 1
  fi
  sleep 1
done

echo "Backend server is ready"

# Start frontend server
cd ../frontend
VITE_PORT=$VITE_PORT npm run dev &
FRONTEND_PID=$!

# Wait for frontend to be ready
echo "Waiting for frontend server..."
MAX_RETRIES=30
COUNT=0
while ! curl -s http://localhost:$VITE_PORT >/dev/null; do
  ((COUNT++))
  if [ $COUNT -eq $MAX_RETRIES ]; then
    echo "Frontend server failed to start"
    exit 1
  fi
  sleep 1
done

echo "Frontend server is ready"

# Keep the script running
wait
