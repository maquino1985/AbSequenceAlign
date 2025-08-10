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

# Function to check for conda in common locations
find_conda() {
    local conda_locations=(
        "$HOME/miniconda3/bin/conda"
        "$HOME/anaconda3/bin/conda"
        "$HOME/opt/miniconda3/bin/conda"
        "$HOME/opt/anaconda3/bin/conda"
        "/usr/local/miniconda3/bin/conda"
        "/usr/local/anaconda3/bin/conda"
        "/opt/miniconda3/bin/conda"
        "/opt/anaconda3/bin/conda"
    )

    for loc in "${conda_locations[@]}"; do
        if [ -x "$loc" ]; then
            echo "$loc"
            return 0
        fi
    done
    return 1
}

# Check if conda is available in PATH
if ! command -v conda &> /dev/null; then
    echo "🔍 Conda not found in PATH, checking common locations..."
    CONDA_PATH=$(find_conda)
    
    if [ -n "$CONDA_PATH" ]; then
        echo "✅ Found conda at: $CONDA_PATH"
        # Add conda to PATH for this session
        export PATH="$(dirname "$CONDA_PATH"):$PATH"
        # Initialize conda for shell
        eval "$("$CONDA_PATH" 'shell.bash' 'hook')"
    else
        echo "❌ Conda not found. Would you like to:"
        echo "1) Install Miniconda"
        echo "2) Specify conda location manually"
        echo "3) Exit"
        read -p "Choose an option (1-3): " choice
        
        case $choice in
            1)
                echo "📥 Downloading Miniconda installer..."
                if [[ "$OSTYPE" == "darwin"* ]]; then
                    MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
                else
                    MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
                fi
                
                curl -o miniconda.sh $MINICONDA_URL
                bash miniconda.sh -b -p "$HOME/miniconda3"
                rm miniconda.sh
                
                export PATH="$HOME/miniconda3/bin:$PATH"
                eval "$("$HOME/miniconda3/bin/conda" 'shell.bash' 'hook')"
                ;;
            2)
                read -p "Enter the full path to conda: " custom_conda
                if [ -x "$custom_conda" ]; then
                    export PATH="$(dirname "$custom_conda"):$PATH"
                    eval "$("$custom_conda" 'shell.bash' 'hook')"
                else
                    echo "❌ Invalid conda path. Exiting."
                    exit 1
                fi
                ;;
            3)
                echo "Exiting setup."
                exit 1
                ;;
            *)
                echo "Invalid choice. Exiting."
                exit 1
                ;;
        esac
    fi
fi

echo "🐍 Using conda from: $(which conda)"

# Create/update conda environment
echo "🔧 Setting up conda environment..."

# Check if environment exists
if conda env list | grep -q "^AbSequenceAlign "; then
    echo "✅ Conda environment 'AbSequenceAlign' exists, updating..."
    conda env update -f environment.yml
else
    echo "📦 Creating new conda environment 'AbSequenceAlign'..."
    conda env create -f environment.yml
fi

# Activate the environment
echo "🔧 Activating conda environment..."
conda activate AbSequenceAlign

echo "✅ Conda environment setup complete!"
echo ""
echo "To activate the environment manually:"
echo "  conda activate AbSequenceAlign"
echo ""
echo "To start development:"
echo "  conda activate AbSequenceAlign"
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