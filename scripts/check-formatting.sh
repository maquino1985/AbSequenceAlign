#!/bin/bash

# Code formatting and linting check script
# Run this before pushing to ensure code quality

set -e  # Exit on any error

echo "🔍 Running code formatting and linting checks..."

# Change to project root
cd "$(dirname "$0")/.."

# Check if we're in the AbSequenceAlign environment
if command -v conda &> /dev/null; then
    # Check if AbSequenceAlign environment exists
    if conda env list | grep -q "AbSequenceAlign"; then
        echo "🐍 Using conda environment: AbSequenceAlign"
        CONDA_CMD="conda run -n AbSequenceAlign"
    else
        echo "⚠️  AbSequenceAlign conda environment not found, using system Python"
        CONDA_CMD=""
    fi
else
    echo "⚠️  Conda not found, using system Python"
    CONDA_CMD=""
fi

# Check Python code formatting
echo "🐍 Checking Python code formatting..."
if ! $CONDA_CMD black --check app/backend/; then
    echo "❌ Black formatting check failed!"
    echo "💡 Run 'cd app/backend && conda run -n AbSequenceAlign black .' to fix formatting"
    exit 1
fi
echo "✅ Black formatting check passed"

# Check Python linting
echo "🐍 Checking Python linting..."
if ! $CONDA_CMD flake8 app/backend/; then
    echo "❌ Flake8 linting failed!"
    echo "💡 Fix the linting errors above before pushing"
    exit 1
fi
echo "✅ Flake8 linting passed"

# Check TypeScript/JavaScript code
echo "📝 Checking TypeScript/JavaScript code..."
if command -v npm &> /dev/null; then
    cd app/frontend
    
    # Run ESLint
    if ! npm run lint; then
        echo "❌ ESLint check failed!"
        echo "💡 Fix the linting errors above before pushing"
        exit 1
    fi
    echo "✅ ESLint check passed"
    
    # Run type checking
    if ! npm run type-check; then
        echo "❌ TypeScript type check failed!"
        echo "💡 Fix the type errors above before pushing"
        exit 1
    fi
    echo "✅ TypeScript type check passed"
    
    cd ../..
else
    echo "⚠️  npm not found, skipping frontend checks"
fi

echo "🎉 All formatting and linting checks passed!"
echo "🚀 Ready to push!"
