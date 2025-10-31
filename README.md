# Meeting Recap App

Transform your meeting and gaming session recordings into transcripts, structured analysis, and narrative recaps automatically.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: macOS | Windows | Linux](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-blue)]()
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Latest Release](https://img.shields.io/badge/Release-v0.1.0-green.svg)](https://github.com/melomba2/meeting-recap-app/releases/tag/v0.1.0)
[![Build Status](https://img.shields.io/github/actions/workflow/status/melomba2/meeting-recap-app/build.yml?branch=main&label=Build)](https://github.com/melomba2/meeting-recap-app/actions/workflows/build.yml)
[![Status: Stable](https://img.shields.io/badge/Status-Stable-brightgreen)]()

## Features

✨ **Automatic Transcription** - Convert audio/video to text using OpenAI Whisper
- Supports MP3, WAV, M4A, MP4, MKV, and more
- Local GPU acceleration (NVIDIA CUDA) or remote server transcription
- Multiple model sizes (tiny, base, small, medium, large)

📊 **Content Analysis** - Extract insights using Ollama LLM
- Automatic topic extraction and summarization
- Key decisions and action items identification
- Flexible model selection (Gemma, Llama, etc.)

📖 **Narrative Recaps** - Generate "Previously on..." style recaps
- Multiple recap styles (epic, casual, dramatic, narrative)
- Perfect for D&D sessions, meetings, or gaming content
- TTS-ready formatted output

🌐 **Remote Server Support** - Offload processing to powerful machines
- Distribute transcription to remote GPU servers
- Connect to Ollama instances anywhere on your network
- Built-in server health checks and configuration testing

## Quick Start

### Prerequisites

**Required:**
- Python 3.10 or higher
- Ollama (for analysis and recap generation)
- FFmpeg (for audio extraction)

**Optional:**
- NVIDIA GPU with CUDA support (for faster local transcription)
- Remote Whisper server (to offload transcription)

### Installation

#### Step 1: Clone the Repository
```bash
git clone https://github.com/melomba2/meeting-recap-app.git
cd meeting-recap-app
```

#### Step 2: Run the Setup Script

**macOS/Linux:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

**Windows (PowerShell):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\scripts\setup.ps1
```

These scripts will:
- Check for Python 3.10+
- Install FFmpeg if needed
- Create a Python virtual environment
- Install all Python dependencies

#### Step 3: Install Ollama

Visit [ollama.ai](https://ollama.ai) and download Ollama for your platform.

Start Ollama and pull a model:
```bash
ollama serve
# In another terminal:
ollama pull gemma3n:latest
```

#### Step 4: Build and Run the App

Install Node.js dependencies:
```bash
npm install
```

**Development Mode** (with hot reload):
```bash
# Terminal 1: Start frontend dev server
npm run dev

# Terminal 2: Start Tauri app
npm run tauri:dev
```

**Production Build:**
```bash
npm run tauri:build
```

The built app will be in `src-tauri/target/release/`.

## Configuration

### Default Settings

The app comes pre-configured with:
- **Ollama Server**: `http://localhost:11434`
- **Whisper Server**: `http://localhost:9000` (optional, for remote transcription)
- **Output Directory**: `~/Documents/Meeting Recaps`
- **Whisper Model**: medium (balanced quality/speed)
- **Ollama Model**: gemma3n:latest

### Customizing Configuration

Settings are saved to your browser's localStorage automatically:
- **Whisper Model**: Choose from tiny, base, small, medium, large
- **Transcription Mode**: Local GPU or Remote GPU
- **Recap Style**: Epic, casual, dramatic, or narrative
- **Server URLs**: Configurable for remote servers

For environment-based configuration, copy `.env.example` to `.env`:
```bash
cp .env.example .env
# Edit .env with your custom settings
```

## Usage

### Basic Workflow

1. **Select Recording** - Drag and drop or use file picker
2. **Choose Options**:
   - Whisper model size
   - Transcription mode (local or remote)
   - Recap style
   - Enable/disable analysis and recap generation
3. **Configure Servers** (if using remote):
   - Enter server URLs
   - Click "Test Connection" to verify
4. **Start Processing** - Click "Start Processing"
5. **Get Results** - Files saved to configured output directory

### Output Files

The app generates three files (if all stages enabled):

1. **Transcript** (`*_transcript.txt`)
   - Raw transcribed text with speaker identification
   - Timestamped sections

2. **Analysis** (`*_analysis.txt`)
   - Key points extracted
   - Decisions made
   - Action items
   - Topics covered

3. **Recap** (`*_recap.txt`)
   - Narrative summary in chosen style
   - Can be used as TTS input
   - Perfect for social media posts or descriptions

## Server Setup

### Local Ollama (Recommended for Beginners)

1. Download and install [Ollama](https://ollama.ai)
2. Open a terminal and run: `ollama serve`
3. In another terminal, pull a model: `ollama pull gemma3n:latest`
4. The app will automatically connect to `http://localhost:11434`

### Remote Ollama Server

For detailed instructions on setting up Ollama on a remote machine, see [SETUP_SERVERS.md](SETUP_SERVERS.md).

### Remote Whisper Server

To offload transcription to a powerful GPU machine:
1. Follow setup instructions in [SETUP_SERVERS.md](SETUP_SERVERS.md)
2. In the app: Select "Remote GPU" transcription mode
3. Enter your remote server URL
4. Click "Test Connection" to verify

## Troubleshooting

### Python Not Found
- Verify Python 3.10+ is installed: `python3 --version`
- On Windows, ensure Python is added to PATH
- Try running setup script again

### FFmpeg Not Found
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt-get install ffmpeg`
- Windows: `winget install ffmpeg` (or manually from https://ffmpeg.org)

### Ollama Connection Failed
- Ensure Ollama is running: `ollama serve`
- Check URL is correct: `http://localhost:11434`
- Test connection manually: `curl http://localhost:11434/api/tags`

### Python Module Not Found
- Ensure virtual environment is active
- Run: `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\Activate.ps1` (Windows)
- Reinstall dependencies: `pip install -r requirements.txt`

### GPU Not Detected
- For NVIDIA: Ensure CUDA drivers are installed
- Test GPU: `python3 -c "import torch; print(torch.cuda.is_available())"`
- CPU mode will still work, just slower

### Build Fails
- Clear Rust build cache: `cargo clean --manifest-path=src-tauri/Cargo.toml`
- Update Rust: `rustup update`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

For more issues, check the [Discussions](https://github.com/melomba2/meeting-recap-app/discussions) or open an [Issue](https://github.com/melomba2/meeting-recap-app/issues).

## System Requirements

### Minimum Requirements
- **CPU**: Multi-core processor (4+ cores recommended)
- **RAM**: 8GB (16GB+ for medium/large Whisper models)
- **Storage**: 20GB free space
- **Network**: Internet connection for model downloads

### Recommended for GPU Acceleration
- **GPU**: NVIDIA with CUDA 11.8+ support
- **VRAM**: 4GB+ (larger models need 8GB+)
- **Drivers**: Latest NVIDIA drivers

### Supported Operating Systems
- macOS 11.0+
- Windows 10/11
- Ubuntu 20.04+, Debian 11+, other Linux distros

## Development

### Building from Source

1. Install Rust: https://rustup.rs/
2. Clone the repository
3. Run setup script (see Installation above)
4. For development: `npm run tauri:dev`
5. For production build: `npm run tauri:build`

### Project Structure
```
meeting-recap-app/
├── src/                    # Frontend (HTML/CSS/JS)
├── src-tauri/             # Rust/Tauri backend
├── src-python/            # Python processing modules
├── scripts/               # Setup and utility scripts
├── config/                # Configuration files
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Known Limitations

⚠️ **Security Notes**
- App uses unsigned binaries (expect security warnings on macOS/Windows)
- Configure firewall if using remote servers
- API tokens are stored in browser localStorage (not encrypted)

📝 **Processing Limitations**
- Maximum recommended file size: 2GB
- Very long meetings may require chunking (done automatically)
- Transcription quality depends on audio quality and background noise

🌐 **Network Requirements**
- Remote server communication uses unencrypted HTTP
- Both machines should be on the same network (for security)
- Ensure firewall allows configured ports

## Performance Tips

1. **Use Medium or Smaller Whisper Models** for faster processing
2. **Enable GPU Acceleration** if you have NVIDIA GPU
3. **Use Remote Whisper Server** for transcription-heavy workflows
4. **Disable Recap Generation** if you only need transcript + analysis
5. **Run Ollama on Dedicated Machine** for multiple users

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 💬 **Discussions**: [GitHub Discussions](https://github.com/melomba2/meeting-recap-app/discussions)
- 🐛 **Report Issues**: [GitHub Issues](https://github.com/melomba2/meeting-recap-app/issues)
- 📚 **Documentation**: [Setup Guide](SETUP_SERVERS.md) | [Contributing](CONTRIBUTING.md)

## Acknowledgments

Built with:
- [Tauri](https://tauri.app/) - Desktop framework
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [Ollama](https://ollama.ai/) - LLM inference
- [FastAPI](https://fastapi.tiangolo.com/) - REST API framework

## Roadmap

Coming soon:
- [ ] Automatic model caching and management
- [ ] Batch processing for multiple files
- [ ] Export to various formats (PDF, Markdown, etc.)
- [ ] Database for storing processing history
- [ ] Web UI for remote server administration
- [ ] Real-time transcription (streaming)
- [ ] Speaker diarization and identification

---

**Questions?** Check the [FAQ](SETUP_SERVERS.md#faq) or start a discussion!
