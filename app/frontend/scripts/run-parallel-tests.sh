#!/bin/bash

# Kill any existing Cypress processes
pkill -f cypress || true
sleep 1

# Set the base URL
export BASE_URL="http://localhost:5173"

echo "Running Cypress tests in parallel..."

# Run each test file in parallel
npx cypress run --spec "cypress/e2e/0-health-check.cy.ts" --config baseUrl=$BASE_URL &
PID1=$!

npx cypress run --spec "cypress/e2e/quick-ui-test.cy.ts" --config baseUrl=$BASE_URL &
PID2=$!

# Wait for all background processes to complete
wait $PID1 $PID2

echo "All parallel tests completed!"
