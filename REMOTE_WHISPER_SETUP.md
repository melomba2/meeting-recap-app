# Remote Whisper Server Setup Guide

This guide walks you through setting up a remote Whisper transcription server on another computer with a powerful GPU (like an RTX 5090). The app will offload transcription to this server via HTTP API, similar to how Ollama integration works.

## Prerequisites

- **GPU with CUDA support** (RTX 5090, RTX 4090, RTX 3090, etc.)
- **NVIDIA CUDA Toolkit** installed and working
- **Python 3.10+**
- **FFmpeg** installed
- Network connectivity between app machine and server machine

## Step 1: Install Dependencies on Remote Machine

### 1.1 Install NVIDIA CUDA Toolkit

If not already installed, download and install from:
https://developer.nvidia.com/cuda-downloads

Verify CUDA is working:
```bash
nvidia-smi  # Should show your GPU information
```

### 1.2 Install Python Dependencies

Create a virtual environment (recommended):
```bash
python3 -m venv whisper-env
source whisper-env/bin/activate  # On Windows: whisper-env\Scripts\activate
```

Install faster-whisper and server dependencies:
```bash
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install faster-whisper
pip install fastapi uvicorn python-multipart pydantic
```

### 1.3 Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
```bash
winget install FFmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install ffmpeg
```

## Step 2: Set Up Whisper Server

We'll use a FastAPI-based Whisper server for easy HTTP integration. You have two options:

### Option A: Using faster-whisper-server (Recommended)

1. **Install the server:**
```bash
pip install faster-whisper-server
```

2. **Start the server:**
```bash
faster-whisper-server --host 0.0.0.0 --port 9000 --model medium
```

Available models: `tiny`, `base`, `small`, `medium`, `large`

**Example with specific settings:**
```bash
faster-whisper-server \
  --host 0.0.0.0 \
  --port 9000 \
  --model medium \
  --device cuda \
  --compute_type float16
```

### Option B: Using whisper-asr-webservice

1. **Clone the repository:**
```bash
git clone https://github.com/ahmetoner/whisper-asr-webservice.git
cd whisper-asr-webservice
```

2. **Create a Dockerfile** (or use the existing one):
```dockerfile
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3 python3-pip ffmpeg \
    && pip install --upgrade pip

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

3. **Build and run with Docker:**
```bash
docker build -t whisper-server .
docker run --gpus all -p 9000:5000 whisper-server
```

## Step 3: Verify Server is Running

Test that the server is accessible:

```bash
# Test health check endpoint
curl http://localhost:9000/health

# Test with a sample audio file
curl -X POST -F "file=@sample.mp3" http://localhost:9000/transcribe
```

**Expected response:**
```json
{
  "text": "Your transcription here..."
}
```

## Step 4: Configure Remote Host (App Side)

### 4.1 Update App Configuration

In the app's Settings or configuration, set:

- **Transcription Mode**: Remote GPU
- **Remote Whisper Host**: `http://192.168.68.10:9000` (replace IP with your server IP)

### 4.2 Find Your Server's IP Address

**On the remote machine:**

**macOS/Linux:**
```bash
ifconfig | grep "inet "
```

**Windows:**
```bash
ipconfig | findstr IPv4
```

Use the local network IP (usually `192.168.x.x` or `10.x.x.x`)

## Step 5: Set Up as System Service (Optional but Recommended)

To have the Whisper server start automatically on reboot:

### macOS (using launchd):

1. **Create a plist file** at `~/Library/LaunchAgents/com.whisper.server.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.whisper.server</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/whisper-env/bin/faster-whisper-server</string>
        <string>--host</string>
        <string>0.0.0.0</string>
        <string>--port</string>
        <string>9000</string>
        <string>--model</string>
        <string>medium</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/whisper-server.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/whisper-server.err</string>
</dict>
</plist>
```

2. **Load the service:**
```bash
launchctl load ~/Library/LaunchAgents/com.whisper.server.plist
```

### Linux (using systemd):

1. **Create service file** at `/etc/systemd/system/whisper-server.service`:

```ini
[Unit]
Description=Whisper Transcription Server
After=network.target

[Service]
Type=simple
User=your-username
Environment="PATH=/path/to/whisper-env/bin"
ExecStart=/path/to/whisper-env/bin/faster-whisper-server --host 0.0.0.0 --port 9000 --model medium
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. **Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable whisper-server
sudo systemctl start whisper-server
```

### Windows (using Task Scheduler):

1. **Open Task Scheduler** and create a new task
2. **Set trigger**: On system startup
3. **Set action**: Run program
   - Program: `C:\path\to\whisper-env\Scripts\faster-whisper-server.exe`
   - Arguments: `--host 0.0.0.0 --port 9000 --model medium`

## Step 6: Network Configuration (if remote machine is on different network)

If the remote Whisper server is on a different network:

1. **Check firewall**: Ensure port 9000 is open on the remote machine
2. **Static IP**: Consider assigning a static IP to the remote machine
3. **Network access**: Ensure both machines can ping each other

### Firewall Rules

**Windows:**
```powershell
netsh advfirewall firewall add rule name="Whisper Server" dir=in action=allow protocol=tcp localport=9000
```

**macOS (using pfctl):**
```bash
echo "pass in proto tcp from any to any port 9000" | sudo pfctl -f -
```

**Linux (using ufw):**
```bash
sudo ufw allow 9000/tcp
```

## Troubleshooting

### Server won't start

- Check CUDA is available: `nvidia-smi`
- Check Python environment is activated: `which python`
- Look for error messages in console output
- Verify port 9000 is not already in use: `lsof -i :9000`

### Connection refused from app

- Verify server is running and listening: `curl http://localhost:9000/health`
- Check firewall is not blocking port 9000
- Verify correct IP address is configured in app settings
- Try with a simpler machine name or IP address
- Check network connectivity: `ping <server-ip>`

### Slow transcription

- Reduce model size: Use `base` or `small` instead of `medium`
- Check GPU is being used: Monitor with `nvidia-smi` during transcription
- Verify no other GPU processes are running
- Check network latency between machines

### Out of memory (CUDA)

- Reduce model size
- Reduce batch processing if applicable
- Ensure no other GPU applications are running

### Model files not downloading

- Check internet connection
- Manually download model: `python -c "from faster_whisper import WhisperModel; WhisperModel('medium')"`
- Check disk space available

## Performance Notes

**Expected Transcription Speeds:**

With RTX 5090 and faster-whisper:
- **Tiny model**: 40-50x real-time speed
- **Base model**: 30-40x real-time speed
- **Small model**: 15-25x real-time speed
- **Medium model**: 8-15x real-time speed
- **Large model**: 4-8x real-time speed

Real-time speed means: 1 hour of audio transcribes in ~(60 minutes / speed) time.

**GPU Memory Requirements:**
- Tiny: ~1 GB VRAM
- Base: ~1 GB VRAM
- Small: ~2 GB VRAM
- Medium: ~5 GB VRAM
- Large: ~10 GB VRAM

## Monitoring the Server

Check server logs and status:

```bash
# If using systemd
sudo systemctl status whisper-server
sudo journalctl -u whisper-server -f

# If running in terminal
# Look for output messages and errors

# Check GPU usage
nvidia-smi -l 1  # Update every second
```

## API Endpoint Reference

The Whisper server exposes these endpoints:

**Health Check:**
```bash
GET /health
# Response: {"status": "ok"}
```

**Transcribe File:**
```bash
POST /transcribe
Content-Type: multipart/form-data

Parameters:
- file: audio file (mp3, wav, m4a, etc.)
- model: whisper model size (optional, default from server config)
- language: language code (optional, default: en)

# Response
{
  "text": "Transcribed text here..."
}
```

**Get Models:**
```bash
GET /models
# Response: {"models": ["tiny", "base", "small", "medium", "large"]}
```

## Security Notes

For local network use only. Do NOT expose this server to the internet without:
- Adding authentication (API key)
- Using HTTPS/TLS encryption
- Implementing rate limiting
- Running behind a reverse proxy

Example with authentication (using Gunicorn):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:9000 app:app
```

## Next Steps

Once the server is running:

1. Open the Meeting Recap app
2. Go to Settings → Transcription Mode
3. Select "Remote GPU"
4. Enter the server IP/host: `http://192.168.68.10:9000`
5. Click "Test Connection" to verify connectivity
6. Process a recording using the remote server

---

**Questions or Issues?**

If you encounter problems:
1. Check the troubleshooting section above
2. Verify server is running: `curl http://your-server-ip:9000/health`
3. Check firewall settings
4. Review server logs for detailed error messages
