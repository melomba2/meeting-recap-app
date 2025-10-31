# Server Setup Guide

This guide covers setting up Ollama and remote Whisper servers for the Meeting Recap App.

## Table of Contents

1. [Ollama Setup](#ollama-setup)
   - [Local Installation](#local-installation)
   - [Remote Installation](#remote-installation)
2. [Remote Whisper Server Setup](#remote-whisper-server-setup)
3. [Network Configuration](#network-configuration)
4. [Troubleshooting](#troubleshooting)

---

## Ollama Setup

Ollama provides the LLM (Large Language Model) for analyzing transcripts and generating recaps.

### Local Installation

**Recommended for beginners** - Simple setup, runs on your machine.

#### macOS

1. Download Ollama from https://ollama.ai
2. Run the installer and follow prompts
3. Open Terminal and start Ollama:
   ```bash
   ollama serve
   ```
   You should see: `Listening on 127.0.0.1:11434`

4. In another Terminal window, pull a model:
   ```bash
   ollama pull gemma3n:latest
   ```
   This downloads ~5GB model (first time only)

5. Verify it works:
   ```bash
   curl http://localhost:11434/api/tags
   ```
   You should get JSON with available models

#### Windows

1. Download Ollama from https://ollama.ai
2. Run the installer (Administrator)
3. Open Command Prompt or PowerShell:
   ```bash
   ollama serve
   ```
4. In another terminal, pull a model:
   ```bash
   ollama pull gemma3n:latest
   ```
5. Verify connection:
   ```bash
   curl http://localhost:11434/api/tags
   ```

#### Linux (Ubuntu/Debian)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start the service
sudo systemctl start ollama
sudo systemctl enable ollama

# Pull a model
ollama pull gemma3n:latest

# Verify
curl http://localhost:11434/api/tags
```

### Remote Installation

**For power users** - Run Ollama on a powerful machine on your network.

#### Prerequisites

- Machine with 16GB+ RAM and modern CPU
- Linux, macOS, or Windows with WSL2
- Network connectivity between app machine and Ollama machine

#### Installation

1. **On the remote machine**, install Ollama (follow Local Installation steps above)

2. **Configure for network access**:

   **Linux/macOS:**
   ```bash
   # Edit systemd service
   sudo systemctl edit ollama

   # Add these lines in [Service] section:
   # [Service]
   # Environment="OLLAMA_HOST=0.0.0.0:11434"
   ```

   Or set environment variable:
   ```bash
   export OLLAMA_HOST=0.0.0.0:11434
   ollama serve
   ```

   **Windows:**
   ```powershell
   # Set environment variable
   [Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0:11434", "User")

   # Restart Ollama service
   Restart-Service ollama
   ```

3. **Pull models on remote machine**:
   ```bash
   ollama pull gemma3n:latest
   ```

4. **Find the remote IP address**:

   **macOS/Linux:**
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   # Look for something like: 192.168.1.100
   ```

   **Windows:**
   ```bash
   ipconfig
   # Look for IPv4 Address: 192.168.x.x
   ```

5. **From app machine, test connection**:
   ```bash
   curl http://192.168.x.x:11434/api/tags
   ```

6. **In the Meeting Recap App**:
   - Enable "Run content analysis"
   - Enter server URL: `http://192.168.x.x:11434`
   - Click "Test Connection"

### Available Models

Popular models to use with Ollama:

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| gemma3n:latest | 5GB | Fast | Good | Default, recommended |
| llama3:latest | 4GB | Very Fast | Good | Lightweight alternative |
| llama3.2:3b | 2GB | Fastest | Fair | Minimal resources |
| mistral:latest | 4GB | Fast | Good | Alternative |
| neural-chat:latest | 5GB | Fast | Very Good | Good quality |

**Install additional models:**
```bash
ollama pull mistral:latest
ollama pull llama3:latest
ollama pull neural-chat:latest
```

### Model Management

**List installed models:**
```bash
ollama list
```

**Remove a model to free space:**
```bash
ollama rm gemma3n:latest
```

**Update to latest version of a model:**
```bash
ollama pull gemma3n:latest  # Downloads latest version
```

---

## Remote Whisper Server Setup

Whisper handles transcription. The remote server option allows offloading to a machine with a powerful GPU (like NVIDIA RTX).

### Why Use Remote Whisper?

- **Speed**: GPU acceleration is 4x+ faster than CPU
- **Offload**: Frees up your local machine for other work
- **Flexibility**: Use a dedicated server for transcription

### Prerequisites

- Machine with NVIDIA GPU (RTX 3060+ recommended)
- Linux (WSL2 on Windows works too)
- CUDA Toolkit 11.8+
- cuDNN 9.1+
- Python 3.10+

### Installation

#### Step 1: Install NVIDIA CUDA and cuDNN

**On the remote machine:**

```bash
# Install CUDA Toolkit
# Go to: https://developer.nvidia.com/cuda-downloads
# Download and install for your OS

# Verify CUDA
nvidia-smi
nvcc --version

# Install cuDNN
# Download from: https://developer.nvidia.com/cudnn
# (Requires free NVIDIA account)
# Extract and add to PATH:
# Linux: Add to ~/.bashrc or ~/.zshrc
export LD_LIBRARY_PATH=$HOME/cudnn/lib:$LD_LIBRARY_PATH
```

#### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv whisper-env
source whisper-env/bin/activate  # Linux/macOS
# or: whisper-env\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install faster-whisper fastapi uvicorn python-multipart
```

#### Step 3: Create Whisper Server Script

Create `whisper_server.py` on the remote machine:

```python
#!/usr/bin/env python3
"""
Whisper Transcription Server using faster-whisper
Run: python whisper_server.py
Then access: http://localhost:9000/docs
"""

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
import os
import tempfile
import json

app = FastAPI(title="Whisper Transcription Server")

# Enable CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model cache
current_model = {"name": "medium", "model": None}


def get_model(model_name: str = "medium"):
    """Load model, caching to avoid reloading"""
    if current_model["name"] != model_name:
        print(f"Loading model: {model_name}")
        current_model["model"] = WhisperModel(
            model_name, device="cuda", compute_type="float16"
        )
        current_model["name"] = model_name
    return current_model["model"]


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "current_model": current_model["name"],
    }


@app.get("/models")
async def list_models():
    """List available Whisper models"""
    models = [
        "tiny",
        "base",
        "small",
        "medium",
        "large",
    ]
    return {"models": models}


@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    model: str = Form("medium"),
    language: str = Form("en"),
):
    """
    Transcribe audio file

    Parameters:
    - file: Audio file (MP3, WAV, M4A, etc.)
    - model: Whisper model size (tiny, base, small, medium, large)
    - language: Language code (en, es, fr, etc.)

    Returns:
    - text: Transcribed text
    - model: Model used
    - language: Language detected
    """
    # Save uploaded file to temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        # Get model
        whisper_model = get_model(model)

        # Transcribe
        print(f"Transcribing with model {model}...")
        segments, info = whisper_model.transcribe(
            temp_path, language=language
        )

        # Collect all segments
        text = ""
        for segment in segments:
            text += segment.text + " "

        return {
            "text": text.strip(),
            "model": model,
            "language": info.language,
        }

    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    import uvicorn

    # Bind to all interfaces to accept remote connections
    uvicorn.run(app, host="0.0.0.0", port=9000)
```

#### Step 4: Run the Server

```bash
# Start the server
python whisper_server.py

# Should see:
# INFO:     Uvicorn running on http://0.0.0.0:9000
# INFO:     Application startup complete
```

#### Step 5: Verify Server Works

From another machine on the same network:

```bash
# Test health
curl http://192.168.x.x:9000/health

# Test models endpoint
curl http://192.168.x.x:9000/models

# Test transcription with audio file
curl -X POST "http://192.168.x.x:9000/transcribe" \
  -F "file=@/path/to/audio.mp3" \
  -F "model=medium"
```

#### Step 6: Configure in App

1. In Meeting Recap App, select "Remote GPU" transcription mode
2. Enter server URL: `http://192.168.x.x:9000`
3. Click "Test Connection"
4. Should show connected and available models

### Running Server Persistently

**On Linux/WSL (systemd):**

Create `/etc/systemd/system/whisper-server.service`:

```ini
[Unit]
Description=Whisper Transcription Server
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/whisper/directory
Environment="LD_LIBRARY_PATH=$HOME/cudnn/lib:$LD_LIBRARY_PATH"
ExecStart=/home/your_username/whisper-env/bin/python /path/to/whisper_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable whisper-server
sudo systemctl start whisper-server
sudo systemctl status whisper-server
```

**On Windows (Task Scheduler):**

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: Start program
   - Program: `C:\path\to\whisper-env\Scripts\python.exe`
   - Arguments: `C:\path\to\whisper_server.py`

---

## Network Configuration

### Same Network (Recommended)

If both machines are on the same local network (home WiFi, office network):

1. **Find remote machine IP:**
   ```bash
   # Linux/macOS
   hostname -I  # or ifconfig

   # Windows
   ipconfig
   ```

2. **Check firewall allows port:**

   **Linux:**
   ```bash
   sudo ufw allow 11434  # Ollama
   sudo ufw allow 9000   # Whisper
   ```

   **Windows Firewall:**
   - Search "Windows Defender Firewall with Advanced Security"
   - Inbound Rules → New Rule
   - Port, TCP, Specific port (11434 or 9000)
   - Allow the connection

3. **Verify connectivity:**
   ```bash
   curl http://192.168.x.x:11434/api/tags
   curl http://192.168.x.x:9000/health
   ```

### Different Networks / Remote Access

⚠️ **Not recommended for security reasons**. If you must:

1. **Use VPN** to connect networks securely
2. **Enable HTTPS** (requires SSL certificate)
3. **Add authentication** (API keys, passwords)
4. **Never expose on public internet** without proper security

---

## Troubleshooting

### Ollama Issues

**Connection refused:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve

# On Windows, check if service is running:
Get-Service ollama
```

**Out of memory:**
```bash
# Reduce model size
ollama pull llama3.2:3b  # Smaller model

# Or increase system swap:
# Linux: sudo fallocate -l 4G /swapfile
# Windows: Increase virtual memory in System settings
```

**Model download fails:**
```bash
# Check internet connection
ping ollama.ai

# Try again with more time
ollama pull gemma3n:latest --verbose
```

### Remote Whisper Issues

**GPU not detected:**
```bash
# Check CUDA
nvidia-smi

# Check PyTorch GPU support
python3 -c "import torch; print(torch.cuda.is_available())"
```

**CUDA out of memory:**
```bash
# Check available VRAM
nvidia-smi

# Restart to clear cache
sudo systemctl restart whisper-server  # or restart computer
```

**Port already in use:**
```bash
# Find what's using port 9000
lsof -i :9000  # Linux/macOS
netstat -ano | findstr :9000  # Windows

# Kill the process or use different port
python whisper_server.py --port 9001
```

**Network connectivity:**
```bash
# From app machine, test:
ping 192.168.x.x
curl http://192.168.x.x:9000/health -v

# Check firewall
sudo iptables -L -n | grep 9000  # Linux
Get-NetFirewallRule -DisplayName "*9000*"  # Windows
```

### App Connection Issues

**"Cannot connect to Ollama server":**
- Verify URL format: `http://192.168.x.x:11434` (no trailing slash)
- Check server is running: `curl http://192.168.x.x:11434/api/tags`
- Ensure both machines are on same network
- Check firewall allows port 11434

**"Test Connection" button shows error:**
- Verify server address is correct
- Check network connectivity: `ping 192.168.x.x`
- Ensure server is fully started (wait 30 seconds after starting)
- Check app logs in browser DevTools (F12)

---

## Performance Tips

### For Ollama

1. **Use smaller models** for faster response:
   ```bash
   ollama pull llama3.2:3b  # Smallest, fastest
   ```

2. **Run on dedicated machine** if serving multiple users

3. **Allocate sufficient RAM**:
   - Tiny models: 4GB
   - Small models: 8GB
   - Large models: 16GB+

4. **Disable GPU if not available**:
   ```bash
   export OLLAMA_HOST=cpu://
   ollama serve
   ```

### For Whisper

1. **Use smaller models** for speed:
   - tiny: Fastest but less accurate
   - medium: Good balance (recommended)
   - large: Slowest but most accurate

2. **Ensure GPU has sufficient VRAM**:
   - Medium: 4GB
   - Large: 8GB+

3. **Use float16 computation** (already set in server script):
   ```python
   WhisperModel(model_name, device="cuda", compute_type="float16")
   ```

---

## FAQ

**Q: Do I need both Ollama and Whisper servers?**
A: No. Whisper is optional for transcription only. Ollama is required for analysis/recap generation.

**Q: Can I run both on the same machine?**
A: Yes, but ensure sufficient RAM (16GB+) and GPU VRAM (8GB+).

**Q: What if my machine doesn't have a GPU?**
A: Everything still works, just slower. CPU processing is fine for most use cases.

**Q: How do I update to a newer model version?**
A: `ollama pull gemma3n:latest` (always gets latest version)

**Q: Can I use different models for different files?**
A: Yes. In the app, you can select different models for each processing job.

**Q: Is there a web interface for server management?**
A: Not included. Use API directly or consider building a management UI.

**Q: How much disk space do I need?**
A: ~5-10GB per model. Whisper models vary, typically 2-3GB.

---

## Getting Help

- Check app logs: Browser DevTools (F12) → Console tab
- Test server directly: Use `curl` commands from this guide
- Check server logs: Look at terminal where server is running
- Open an issue: https://github.com/melomba2/meeting-recap-app/issues
