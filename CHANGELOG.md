# Changelog

All notable changes to the Meeting Recap App project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- (Upcoming features go here)

### Changed
- (Upcoming changes go here)

### Deprecated
- (Upcoming deprecations go here)

### Removed
- (Upcoming removals go here)

### Fixed
- (Upcoming fixes go here)

### Security
- (Upcoming security patches go here)

---

## [0.1.0] - 2024-10-30

### Added

#### Core Features
- ✨ Automatic audio/video transcription using OpenAI Whisper
  - Supports MP3, WAV, M4A, MP4, MKV formats
  - Multiple model sizes (tiny, base, small, medium, large)
  - GPU acceleration for faster processing
  - Hallucination detection and filtering

- 📊 Content analysis using Ollama LLM integration
  - Automatic topic extraction and categorization
  - Key decisions and action items identification
  - Structured analysis output with JSON support
  - Support for multiple LLM models

- 📖 Narrative recap generation with customizable styles
  - Multiple recap styles (epic, casual, dramatic, narrative)
  - "Previously on..." format for storytelling
  - TTS-ready formatted output
  - D&D session and meeting-specific recap templates

#### Desktop Application (Tauri)
- Modern desktop UI with drag-and-drop file upload
- Real-time progress tracking during processing
- File picker dialog for audio/video selection
- Settings panel for server configuration
- Dark/light theme support
- Cross-platform builds (Windows, macOS, Linux)

#### Server Integration
- Local Ollama server connection with health checks
- Remote Whisper server support for GPU offloading
- Configurable server URLs and API endpoints
- Connection testing and diagnostics
- Automatic fallback and error handling

#### Local REST API Server
- FastAPI-based HTTP server for third-party integration
- Job queue system with background processing
- API key authentication
- Endpoints: `/api/transcribe`, `/api/analyze`, `/api/recap`
- Job status tracking: `/api/status/{job_id}`, `/api/jobs`
- OpenAPI/Swagger documentation at `/docs`

#### Automation
- GitHub Actions CI/CD for multi-platform builds
- Automated release creation and asset uploads
- Cross-platform dependency installation
- Automated SHA256 checksum generation

#### Documentation
- Comprehensive README with quick start guide
- Platform-specific setup instructions (macOS, Windows, Linux)
- `SETUP_SERVERS.md` for Ollama and remote Whisper configuration
- `CONTRIBUTING.md` with development guidelines
- `API_EXAMPLES.md` for REST API usage
- Troubleshooting guide with common issues
- FAQ section for frequently asked questions

#### Repository Setup
- MIT License
- GitHub issue templates (bug reports, feature requests)
- Comprehensive `.gitignore` for Python and Rust projects
- Project structure documentation
- CLAUDE.md context file for AI assistance

### Technical Details

- **Language**: Rust (frontend/backend), Python (processing)
- **Framework**: Tauri 2.0 for cross-platform desktop app
- **Frontend**: HTML5, CSS3, JavaScript with Tauri IPC bridge
- **Backend**: Python 3.10+ with FastAPI for REST API
- **GPU Support**: NVIDIA CUDA acceleration with flexible path detection
- **Database**: Local JSON file storage for app settings
- **Configuration**: Environment-based with `.env.example` template

### Fixed
- Path resolution issues for Python interpreter detection
- CUDA/cuDNN library path detection across different systems
- Python virtual environment detection (supports multiple standard locations)
- Hardcoded personal paths replaced with flexible detection
- Hardcoded IP addresses replaced with localhost defaults
- JSON serialization errors in Rust-Python communication

### Known Limitations
- Unsigned binaries on macOS and Windows (may show security warnings)
- Very large files (>2GB) may require manual chunking
- Remote server setup requires network configuration knowledge
- CUDA/cuDNN setup needed for GPU acceleration (not required for CPU mode)

### System Requirements

**Minimum:**
- OS: macOS 11+, Windows 10/11, Ubuntu 20.04+
- RAM: 8GB (16GB+ recommended)
- Python: 3.10 or higher
- FFmpeg: Required for audio/video processing
- Ollama: Required for analysis and recap generation

**Optional:**
- NVIDIA GPU with CUDA 11.8+ for GPU acceleration
- cuDNN 9.1+ for deep learning acceleration

### Contributors
- Michael Lombard (Creator)

### Dependencies

**Python**:
- torch
- openai-whisper
- fastapi
- uvicorn
- requests
- pydantic

**System**:
- FFmpeg 4.0+
- CUDA Toolkit 11.8+ (for GPU)
- cuDNN 9.1+ (for GPU)

**Frontend**:
- Tauri 2.0
- Node.js 18+
- Vite
- TypeScript (optional)

---

## [Unreleased] - Future Versions

### Planned Features
- [ ] Batch processing for multiple files
- [ ] Processing history and job database
- [ ] Web dashboard for remote servers
- [ ] Support for additional LLM providers (OpenAI, Anthropic)
- [ ] Video summary generation
- [ ] Multi-language transcription
- [ ] Custom model fine-tuning
- [ ] Export to multiple formats (PDF, Word, JSON)
- [ ] Real-time transcription for meetings
- [ ] Obsidian vault integration
- [ ] Plugin system for custom processors

---

## How to Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Reporting bugs
- Suggesting features
- Submitting pull requests
- Code style and standards
- Testing requirements

## Support

- 📖 [Setup Guide](SETUP_SERVERS.md)
- 💬 [Discussions](https://github.com/yourusername/meeting-recap-app/discussions)
- 🐛 [Report Issues](https://github.com/yourusername/meeting-recap-app/issues)
- 📧 Direct contact via GitHub

---

**Note:** Replace `yourusername` with your actual GitHub username in links.
