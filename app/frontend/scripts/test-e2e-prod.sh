#!/bin/bash

# Production-like E2E testing script
# This script builds the frontend and serves it with Nginx for E2E testing

set -e

echo "🚀 Starting production-like E2E tests..."

# Build the frontend
echo "📦 Building frontend..."
npm run build

# Start backend server (if not already running)
echo "🔧 Starting backend server..."
cd ../backend
PYTHONPATH="$(pwd)/.." python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ../frontend

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 10
curl -f http://localhost:8000/health || (echo "❌ Backend not ready" && exit 1)

# Start frontend with Nginx
echo "🌐 Starting frontend with Nginx..."
docker run -d --name frontend-nginx-e2e \
  -v $(pwd)/dist:/usr/share/nginx/html:ro \
  -v $(pwd)/nginx.conf:/etc/nginx/conf.d/default.conf:ro \
  -p 5679:80 \
  nginx:alpine

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to be ready..."
sleep 5
curl -f http://localhost:5679 || (echo "❌ Frontend not ready" && exit 1)

# Run Cypress tests
echo "🧪 Running Cypress tests..."
npx cypress run --config baseUrl=http://localhost:5679

# Cleanup
echo "🧹 Cleaning up..."
docker stop frontend-nginx-e2e || true
docker rm frontend-nginx-e2e || true
kill $BACKEND_PID || true

echo "✅ Production-like E2E tests completed!"
