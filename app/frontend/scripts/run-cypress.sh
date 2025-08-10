#!/bin/bash

# Wait for servers to be ready
echo "Waiting for servers to be ready..."
sleep 30

# Run Cypress tests
echo "Running Cypress tests..."
cypress run
