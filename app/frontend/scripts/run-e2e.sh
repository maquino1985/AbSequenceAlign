#!/bin/bash

# Export the ports so they're available to child processes
export VITE_PORT=5679
export BACKEND_PORT=8000

echo "Using frontend port: $VITE_PORT"
echo "Using backend port: $BACKEND_PORT"

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
VITE_PORT=$VITE_PORT npm run dev:port &
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

# Run Cypress tests with the correct ports
CYPRESS_BASE_URL=http://localhost:$VITE_PORT CYPRESS_BACKEND_PORT=$BACKEND_PORT npm run cypress:run

# Store the exit code
EXIT_CODE=$?

# Exit with the Cypress exit code
exit $EXIT_CODE