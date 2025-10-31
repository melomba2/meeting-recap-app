#!/bin/bash
# Meeting Recap App - Setup Script for macOS and Linux
# This script installs dependencies and sets up the Python environment

set -e

echo "======================================"
echo "Meeting Recap App - Setup Script"
echo "======================================"
echo ""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo "Detected: macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "Detected: Linux"
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

echo ""
echo "Step 1: Checking Python installation..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)

echo "Found Python $python_version"

if [[ $python_major -lt 3 ]] || [[ $python_major -eq 3 && $python_minor -lt 10 ]]; then
    echo "ERROR: Python 3.10+ is required (found $python_version)"
    exit 1
fi

echo "✓ Python 3.10+ found"
echo ""

# Install FFmpeg
echo "Step 2: Checking FFmpeg installation..."
if ! command -v ffmpeg &> /dev/null; then
    echo "FFmpeg not found. Installing..."
    if [[ "$OS" == "macos" ]]; then
        if ! command -v brew &> /dev/null; then
            echo "ERROR: Homebrew not found. Please install from https://brew.sh"
            exit 1
        fi
        brew install ffmpeg
    elif [[ "$OS" == "linux" ]]; then
        if command -v apt &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y ffmpeg
        elif command -v yum &> /dev/null; then
            sudo yum install -y ffmpeg
        else
            echo "ERROR: Unsupported package manager. Please install FFmpeg manually."
            exit 1
        fi
    fi
    echo "✓ FFmpeg installed"
else
    echo "✓ FFmpeg already installed: $(ffmpeg -version | head -1)"
fi

echo ""
echo "Step 3: Creating Python virtual environment..."

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate venv
source venv/bin/activate

echo ""
echo "Step 4: Installing Python dependencies..."
echo "This may take a few minutes..."

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install PyTorch (CPU by default, GPU if CUDA available)
echo ""
echo "Installing PyTorch..."
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected. Installing PyTorch with CUDA support..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
else
    echo "No NVIDIA GPU detected. Installing PyTorch CPU version..."
    pip install torch torchvision torchaudio
fi

# Install other dependencies
echo "Installing other dependencies..."
pip install -r requirements.txt

echo ""
echo "✓ All dependencies installed"

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Install and run Ollama:"
echo "   - Download from https://ollama.ai/"
echo "   - Run: ollama serve"
echo "   - In another terminal: ollama pull gemma3n:latest"
echo ""
echo "2. (Optional) Set up remote Whisper server"
echo "   - See SETUP_SERVERS.md for instructions"
echo ""
echo "3. Build the desktop app:"
echo "   - npm install"
echo "   - npm run tauri:build"
echo ""
echo "4. Or run in development mode:"
echo "   - In one terminal: npm run dev"
echo "   - In another terminal: npm run tauri:dev"
echo ""
