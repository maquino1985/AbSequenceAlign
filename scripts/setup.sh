#!/bin/bash

# AbSequenceAlign Development Setup Script

set -e

echo "🚀 Setting up AbSequenceAlign development environment..."

# Check if Python 3.11+ is available
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.11 or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Check if conda is available
if command -v conda &> /dev/null; then
    echo "🐍 Conda detected! Using conda environment..."
    
    # Create conda environment
    if conda env list | grep -q "absequencealign"; then
        echo "✅ Conda environment 'absequencealign' already exists"
    else
        echo "📦 Creating conda environment..."
        conda env create -f environment.yml
    fi
    
    echo "🔧 Activating conda environment..."
    eval "$(conda shell.bash hook)"
    conda activate absequencealign
    
    echo "✅ Conda environment setup complete!"
    echo ""
    echo "To activate the environment manually:"
    echo "  conda activate absequencealign"
    echo ""
    echo "To start development:"
    echo "  conda activate absequencealign"
    echo "  python -m app.main"
    
else
    echo "📚 Installing Python dependencies with pip..."
    echo "Note: ANARCI will be installed from GitHub (this may take a few minutes)..."
    pip install --use-pep517 -r requirements.txt
fi

# Check for external tools
echo "🔍 Checking for external bioinformatics tools..."

tools_missing=false

if ! command -v muscle &> /dev/null; then
    echo "⚠️  MUSCLE not found. Install with: sudo apt-get install muscle"
    tools_missing=true
else
    echo "✅ MUSCLE found"
fi

if ! command -v mafft &> /dev/null; then
    echo "⚠️  MAFFT not found. Install with: sudo apt-get install mafft"
    tools_missing=true
else
    echo "✅ MAFFT found"
fi

if ! command -v clustalo &> /dev/null; then
    echo "⚠️  CLUSTALO not found. Install with: sudo apt-get install clustalo"
    tools_missing=true
else
    echo "✅ CLUSTALO found"
fi

if ! command -v hmmsearch &> /dev/null; then
    echo "⚠️  HMMER not found. Install with: sudo apt-get install hmmer"
    tools_missing=true
else
    echo "✅ HMMER found"
fi

if [ "$tools_missing" = true ]; then
    echo ""
    echo "📝 Note: External tools are optional. The application will work without them,"
    echo "   but some alignment methods may not be available."
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO

# External Tools (optional)
MUSCLE_PATH=/usr/bin/muscle
MAFFT_PATH=/usr/bin/mafft
CLUSTALO_PATH=/usr/bin/clustalo
EOF
    echo "✅ Created .env file"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start development:"
echo "  source venv/bin/activate"
echo "  python -m app.main"
echo ""
echo "To run with Docker:"
echo "  docker-compose up --build"
echo ""
echo "To run tests:"
echo "  python test_phase1.py"
echo ""
echo "API will be available at: http://localhost:8000"
echo "Documentation: http://localhost:8000/docs" 