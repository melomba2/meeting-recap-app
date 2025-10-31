# Meeting Recap App - Setup Script for Windows PowerShell
# This script installs dependencies and sets up the Python environment

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Meeting Recap App - Setup Script" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "WARNING: This script should be run as Administrator for some operations." -ForegroundColor Yellow
    Write-Host "Some installations may fail without admin privileges." -ForegroundColor Yellow
    Write-Host ""
}

# Step 1: Check Python
Write-Host "Step 1: Checking Python installation..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion"

    # Parse version
    if ($pythonVersion -match '(\d+)\.(\d+)') {
        $majorVersion = [int]$matches[1]
        $minorVersion = [int]$matches[2]

        if ($majorVersion -lt 3 -or ($majorVersion -eq 3 -and $minorVersion -lt 10)) {
            Write-Host "ERROR: Python 3.10+ is required (found $pythonVersion)" -ForegroundColor Red
            exit 1
        }
    }

    Write-Host "✓ Python 3.10+ found" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Python not found. Please install Python 3.10+ from https://www.python.org/" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Check/Install FFmpeg
Write-Host "Step 2: Checking FFmpeg installation..." -ForegroundColor Green
try {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host "✓ FFmpeg already installed: $ffmpegVersion" -ForegroundColor Green
}
catch {
    Write-Host "FFmpeg not found. Installing..." -ForegroundColor Yellow

    # Try winget first
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "Installing FFmpeg using winget..."
        winget install ffmpeg
    }
    else {
        Write-Host "ERROR: winget not found. Please install FFmpeg manually:" -ForegroundColor Red
        Write-Host "  - Download from: https://ffmpeg.org/download.html" -ForegroundColor Red
        Write-Host "  - Or use: choco install ffmpeg" -ForegroundColor Red
        exit 1
    }

    Write-Host "✓ FFmpeg installed" -ForegroundColor Green
}

Write-Host ""

# Step 3: Create Python virtual environment
Write-Host "Step 3: Creating Python virtual environment..." -ForegroundColor Green

if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}
else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate venv
& ".\venv\Scripts\Activate.ps1"

Write-Host ""

# Step 4: Install dependencies
Write-Host "Step 4: Installing Python dependencies..." -ForegroundColor Green
Write-Host "This may take a few minutes..." -ForegroundColor Yellow

# Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# Install PyTorch
Write-Host "Installing PyTorch..." -ForegroundColor Yellow
try {
    # Check for NVIDIA GPU
    if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
        Write-Host "NVIDIA GPU detected. Installing PyTorch with CUDA support..." -ForegroundColor Yellow
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    }
    else {
        Write-Host "No NVIDIA GPU detected. Installing PyTorch CPU version..." -ForegroundColor Yellow
        pip install torch torchvision torchaudio
    }
}
catch {
    Write-Host "ERROR installing PyTorch: $_" -ForegroundColor Red
    exit 1
}

# Install other dependencies
Write-Host "Installing other dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "✓ All dependencies installed" -ForegroundColor Green

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Green
Write-Host "1. Install and run Ollama:" -ForegroundColor White
Write-Host "   - Download from https://ollama.ai/" -ForegroundColor Gray
Write-Host "   - Run: ollama serve" -ForegroundColor Gray
Write-Host "   - In another terminal: ollama pull gemma3n:latest" -ForegroundColor Gray
Write-Host ""
Write-Host "2. (Optional) Set up remote Whisper server" -ForegroundColor White
Write-Host "   - See SETUP_SERVERS.md for instructions" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Install Node.js dependencies:" -ForegroundColor White
Write-Host "   - npm install" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Build the desktop app:" -ForegroundColor White
Write-Host "   - npm run tauri:build" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Or run in development mode:" -ForegroundColor White
Write-Host "   - In one terminal: npm run dev" -ForegroundColor Gray
Write-Host "   - In another terminal: npm run tauri:dev" -ForegroundColor Gray
Write-Host ""

Write-Host "For more help, see the README.md and SETUP_SERVERS.md files." -ForegroundColor Green
