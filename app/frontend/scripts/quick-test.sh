#!/bin/bash

# Kill existing processes
pkill -f vite || true
sleep 1

# Set port
export VITE_PORT=${VITE_PORT:-5678}

echo "Starting frontend only on port $VITE_PORT"

# Start frontend in background
npm run dev:port &
FRONTEND_PID=$!

# Wait for frontend with short timeout
echo "Waiting for frontend to start..."
timeout 15s bash -c 'until curl -s http://localhost:5678 > /dev/null; do sleep 1; done' || echo "Frontend timeout"

# Run only the quick UI test
echo "Running quick UI tests..."
npx cypress run --spec "cypress/e2e/quick-ui-test.cy.ts" --config defaultCommandTimeout=3000,requestTimeout=5000,responseTimeout=5000

# Cleanup
kill $FRONTEND_PID 2> /dev/null || true
pkill -f vite || true
