# GEMINI.md

This file provides guidance to Gemini when working with code in this repository.

## Phase Summary

**✅ Phase 1: Foundation Setup** - Complete
- Tauri desktop application launches and displays UI.
- File upload via drag-and-drop and file picker is working.
- Python bridge can execute commands from Rust/Frontend.

**✅ Phase 2: Backend Integration** - Complete
- Python scripts have been refactored into callable modules in `src-python/`.
- `main.py` serves as the API layer for the UI.
- Progress tracking and error handling have been implemented.

**✅ Phase 3: UI Implementation** - Complete
- The UI is in a good state, with all the options and dropdowns visible.
- Real-time progress visualization is implemented.

**✅ Phase 4: Obsidian Integration** - Complete
- `ObsidianClient` class created to connect to the Obsidian API.
- `create_obsidian_note` command implemented to create a new note in Obsidian.
- UI elements for Obsidian integration have been added to the frontend.

**✅ Phase 5: Local API Server** - Complete
- Full REST API implementation in `api_server.py` with FastAPI
- Endpoints for `transcribe`, `analyze`, and `recap` with background job processing
- Job tracking with `/api/status/{job_id}` and `/api/jobs` endpoints
- API key authentication implemented
- Comprehensive API documentation in `API_EXAMPLES.md`

**✅ Phase 6: Preset Management** - Complete
- `PresetManager` class created to handle saving and loading presets
- UI elements for preset management have been added to the frontend
- All preset commands implemented in Rust backend

**Phase 7: Testing & Polish** - In Progress
- Desktop application testing guide created (`DESKTOP_APP_TESTING.md`)
- Fixed multiple integration issues (see debugging notes below)
- Currently debugging transcription failure in desktop app

## Debugging Notes

### `cargo not found` error

When running `npm run tauri dev`, the command would fail with a `cargo: command not found` error. This was because the `npm` script environment did not have the same `PATH` as the interactive shell.

**Solution:**

Modified the `tauri` script in `package.json` to `source ~/.cargo/env && tauri`. This ensures that the Cargo environment is set up correctly before the `tauri` command is executed.

### Blank application window

The application window would open, but it would be blank. This was because the frontend was not being loaded into the webview.

**Solution:**

Moved the `index.html`, `styles.css`, and `main.js` files from the `src` directory to the project root. This fixed the issue and the frontend is now being loaded correctly.

### API server not starting

The API server was not starting correctly due to a number of issues:

*   **`uvicorn` not installed:** The `uvicorn` package was not installed. This was solved by installing it with `pip`.
*   **`pip` not installed:** The `pip` package was not installed. This was solved by installing it with `get-pip.py`.
*   **`fastapi` not installed:** The `fastapi` package was not installed. This was solved by installing it with `pip`.
*   **`ModuleNotFoundError`:** The `uvicorn` process could not find the modules in the `src-python` directory. This was solved by adding the `src-python` directory to the `sys.path` in the `api_server.py` file.
*   **Syntax error in `recap_generator.py`:** There was a syntax error in the `recap_generator.py` file. This was fixed by removing the extra `else` statement.

## Project Overview

**Meeting Recap App** - A desktop application that processes meeting and D&D session recordings to generate transcripts, analysis, and narrative recaps. The project converts existing batch/Python-based workflows into a unified desktop app with Obsidian vault integration and local REST API for third-party tool integration.

**Key Capabilities**:
- Audio transcription using Whisper (optimized for RTX 5090 GPU)
- Content analysis using Ollama/Gemma3n
- D&D-style narrative recap generation with TTS-ready output
- Obsidian vault integration for automatic note creation
- Local REST API server for automation and third-party integrations

## Technology Stack

**Desktop Framework**: Tauri (recommended) or Electron
- Tauri offers 3-10x smaller memory footprint and better GPU access
- Frontend: HTML/CSS/JavaScript or React/Vue/Svelte
- Python integration via Tauri sidecar

**Backend**: Python 3.10+
- Whisper for transcription
- Ollama for LLM inference
- FastAPI for REST API server
- Obsidian Local REST API client for vault integration

## System Architecture

The application consists of four major components that communicate via JSON:

1. **Desktop UI Framework** ✅ - Tauri app providing the user interface
   - Built with Rust backend + HTML/CSS/JS frontend
   - Vite for hot-reload development
   - File upload with drag-and-drop support

2. **Python Backend** ✅ - Core processing modules (transcription, analysis, recap generation)
   - Communication via stdin/stdout JSON-RPC
   - Rust spawns Python processes and pipes commands
   - Existing scripts in `python scripts/` directory

3. **Obsidian Integration** ⚠️ TODO - REST API client for automatic note creation in vaults

4. **Local REST API Server** ⚠️ TODO - Exposes workflow functions as HTTP endpoints for third-party tools

### Communication Flow

**UI ↔ Python Communication**:
- Uses JSON-RPC over stdin/stdout or HTTP
- UI sends commands as JSON objects with job parameters
- Python streams progress updates: `{"status": "processing", "stage": "transcription", "progress": 45}`
- Python returns structured results: `{"status": "complete", "transcript_path": "/path/to/file"}`

**Obsidian Integration**:
- Uses Obsidian Local REST API plugin (default port: 27123)
- Authentication via Bearer token stored in app settings
- Endpoints: `GET /vault/`, `POST /vault/[path]`, `PATCH /vault/[path]`

**Local API Server**:
- Runs on configurable port (default: 8765)
- Requires `X-API-Key` header for authentication
- Core endpoints: `/api/transcribe`, `/api/analyze`, `/api/recap`, `/api/status/{job_id}`, `/api/results/{job_id}`

## Prerequisites

### Required Software (Current)
- **Python 3.10+** with pip
- **FFmpeg** (for audio extraction)
  - Windows: `winget install FFmpeg`
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
- **CUDA Toolkit** (for RTX 5090 GPU support)
  - Download: https://developer.nvidia.com/cuda-downloads
- **Ollama** (running on 192.168.68.10:11434)
  - Install: https://ollama.ai/
  - Start: `ollama serve`
  - Pull model: `ollama pull gemma3n:latest`

### For Desktop App Development (Future)
- **Node.js 18+** and npm
- **Rust** (for Tauri): `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- **Tauri CLI**: `npm install -g @tauri-apps/cli`

## Development Commands

### Desktop Application (Tauri)

**Running the App:**
```bash
# Terminal 1: Start frontend dev server (Vite)
npm run dev

# Terminal 2: Start Tauri app (opens application window)
npm run tauri:dev

# Note: Both commands must run simultaneously for hot-reload to work
```

**Building for Production:**
```bash
# Build for current platform (creates installer in src-tauri/target/release)
npm run tauri:build

# Check Rust code without building
cargo check --manifest-path=src-tauri/Cargo.toml
```

**Testing:**
```bash
# Test Python connection from within the app
# Click "Test Python Connection" button in the Debug section

# Verify Python is accessible
python3 --version

# Check GPU availability
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Standalone Python Scripts (Legacy/Testing)

```bash
# Install Python dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install openai-whisper requests

# Run standalone transcription
python "python scripts/local_processor.py" path/to/recording.mp4 --model medium

# Run transcript analysis
python "python scripts/transcript_analyzer.py" path/to/transcript.txt --model gemma3n:latest

# Generate D&D recap
python "python scripts/recap_generator.py" path/to/analysis.txt --style epic
```

### Debugging

- **Frontend**: Right-click in app window → Inspect (opens DevTools)
- **Rust Backend**: Check terminal output from `npm run tauri dev`
- **Python Backend**: Check log files or stderr output

## Project Structure

```
meeting-recap-app/
├── python scripts/         # Existing Python processing scripts
│   ├── local_processor.py      # Whisper transcription (RTX 5090 optimized)
│   ├── transcript_analyzer.py  # Ollama/Gemma3n analysis
│   └── recap_generator.py      # D&D recap generation
├── src-tauri/              # Tauri backend (Rust) ✅ IMPLEMENTED
│   ├── src/
│   │   ├── main.rs         # Tauri commands and Python bridge
│   │   └── lib.rs          # Library exports
│   ├── Cargo.toml          # Rust dependencies
│   └── tauri.conf.json     # App configuration
├── src-python/             # Python integration layer ✅ IMPLEMENTED
│   ├── main.py             # Entry point that orchestrates existing scripts
│   ├── file_handler.py     # File I/O operations and validation
│   ├── api_server.py       # Local REST API server (FastAPI) - TODO
│   └── obsidian_client.py  # Obsidian REST API integration - TODO
├── src/                    # Frontend (JS/HTML/CSS) ✅ IMPLEMENTED
│   ├── index.html          # Main window with modern UI
│   ├── main.js             # Application logic and Tauri bridge
│   ├── styles.css          # Professional styling
│   └── assets/             # Static assets (images, icons)
├── config/                 # Configuration files ✅ IMPLEMENTED
│   ├── defaults.json       # Default settings (Whisper, Ollama, paths)
│   └── presets/            # Preset configurations - TODO
├── node_modules/           # npm dependencies
├── package.json            # npm configuration
├── vite.config.js          # Vite build configuration
├── Workflow/               # Development workflow documentation
│   ├── 00_main_app_workflow.md
│   ├── 01_ui_framework_setup.md
│   ├── 02_backend_integration.md
│   ├── 03_file_progress.md
│   ├── 04_obsidian_integration.md
│   └── 05_local_api_server.md
├── CLAUDE.md               # Context file for Claude Code
└── GEMINI.md               # Context file for Gemini
```

## Python Backend Architecture

The backend is split into two parts:

### Existing Processing Scripts (in "python scripts/" directory)

**local_processor.py**: Whisper transcription (RTX 5090 optimized)
- Class: `WhisperProcessor`
- GPU-accelerated transcription with anti-repetition settings
- Supports multiple Whisper model sizes (tiny, base, small, medium, large)
- Includes hallucination detection and filtering
- Extracts audio from MP4 files automatically

**transcript_analyzer.py**: Ollama/Gemma3n integration
- Class: `OllamaTranscriptAnalyzer`
- Connects to Ollama instance (default: http://192.168.68.10:11434)
- Processes transcripts with LLM analysis using gemma3n model
- Includes model availability checking and fallback suggestions
- Generates structured analysis with key points, decisions, and action items

**recap_generator.py**: D&D-style recap generation
- Class: `DNDRecapGenerator`
- Creates narrative "Previously on..." style recaps
- Supports multiple style options (epic, casual, dramatic)
- TTS-ready output formatting
- Integrates with Ollama for content generation

### Integration Layer (to be created in src-python/)

**main.py**: Orchestration layer
- Entry point that calls existing scripts
- Implements progress callbacks for UI updates
- Handles JSON-based communication with Tauri frontend
- Coordinates multi-stage workflow (extract → transcribe → analyze → recap)

**file_handler.py**: I/O management
- Validates file extensions, sizes, and formats
- Manages temp file cleanup and output folder organization
- Wraps existing script file operations

**api_server.py**: FastAPI REST server
- Exposes existing scripts as HTTP endpoints
- Runs on localhost with API key authentication
- Implements job queue with async background tasks
- Auto-generates OpenAPI/Swagger docs at /docs

**obsidian_client.py**: Vault interaction
- Authenticates with Obsidian Local REST API
- Creates notes with YAML frontmatter and markdown formatting
- Handles vault path navigation and conflict resolution

## Using the Existing Python Scripts

### Python Dependencies

The existing scripts require the following packages:

```bash
# PyTorch with CUDA support (for RTX 5090 GPU acceleration)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Whisper for transcription
pip install openai-whisper

# HTTP requests for Ollama API
pip install requests

# System requirement: FFmpeg must be installed
# Windows: winget install FFmpeg
# Mac: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

### Standalone Usage

The three existing scripts in "python scripts/" can be run standalone for testing:

```bash
# Transcribe an audio/video file
python "python scripts/local_processor.py" path/to/recording.mp4 --model medium

# Available model sizes: tiny, base, small, medium, large
# Larger models = better accuracy but slower processing

# Analyze a transcript
python "python scripts/transcript_analyzer.py" path/to/transcript.txt --model gemma3n:latest

# Generate a D&D recap from analysis
python "python scripts/recap_generator.py" path/to/analysis.txt --style epic

# Available styles: epic, casual, dramatic, narrative
```

### Integration Notes

When integrating into the Tauri app, the src-python/main.py module will import and call these scripts programmatically, wrapping their functionality with progress reporting and UI-friendly JSON responses.

## Processing Pipeline

The application processes recordings through four stages:

1. **Extract Audio** - Extracts audio from MP4 or processes audio files directly
2. **Transcribe** - Uses Whisper to generate text transcript (GPU-accelerated)
3. **Analyze** - Processes transcript with Ollama/Gemma3n for insights
4. **Generate Recap** - Creates narrative recap with optional TTS output

Each stage reports progress back to UI with percentage complete and status messages.

## GPU Utilization

The application is optimized for RTX 5090 GPU usage:
- Ensure Python processes can access GPU via CUDA drivers
- Whisper transcription runs on GPU by default
- Check GPU availability with `nvidia-smi` if issues occur
- Verify app has permission to access GPU hardware

## Security Considerations

**API Keys and Secrets**:
- Store securely using system keychain (Windows Credential Manager, macOS Keychain)
- Never store in plaintext configuration files
- Encrypt configuration files at rest

**Local API Server**:
- Bind only to localhost (127.0.0.1) - never expose to network
- Require API key authentication on all endpoints
- Implement rate limiting per key
- Validate all file paths to prevent directory traversal

**Obsidian Integration**:
- Validate API tokens before use
- Handle vault permissions properly
- Never expose vault contents to external networks

## File Validation and Queue Processing

**Supported File Types**: Audio files (MP3, WAV, M4A) and video files (MP4, MKV)

**Validation Rules**:
- Check file extension against allowlist
- Validate file size limits (configurable in settings)
- Verify file format with metadata inspection

**Batch Processing**:
- Maintain queue of pending/completed jobs
- Display queue status in UI with per-file progress
- Support cancellation of in-progress jobs
- Auto-cleanup temp files after completion

## Obsidian Note Creation

Generated notes include:

**YAML Frontmatter**:
```yaml
---
date: 2025-10-27
session: 42
type: recap
duration: "8m 34s"
---
```

**Markdown Body**:
- Structured sections (Summary, Key Points, Action Items, etc.)
- Proper heading hierarchy
- Syntax highlighting for code blocks if applicable

## Development Phases

The project is organized into seven development phases (see Workflow/00_main_app_workflow.md):

1. Foundation Setup - Tauri/Electron initialization and Python bridge
2. Backend Integration - Refactor batch scripts into modular Python
3. UI Implementation - Build interface with drag-and-drop and progress tracking
4. Obsidian Integration - Connect to vault REST API
5. Local API Server - Expose functions as REST endpoints
6. Preset Management - Save/load workflow configurations
7. Testing & Polish - End-to-end testing and distribution builds

## Troubleshooting Common Issues

**Python Not Found**:
- Verify Python in system PATH
- Check `tauri.conf.json` has correct Python path
- Try absolute path to Python executable

**GPU Not Detected**:
- Verify CUDA drivers installed
- Test with `nvidia-smi` command
- Check app permissions to access GPU

**File Access Denied**:
- Verify `tauri.conf.json` allowlist includes required paths
- Check user has read/write permissions
- Test with different file locations

**Build Fails**:
- Clear build cache: `cargo clean`
- Update dependencies: `npm update && cargo update`
- Check error messages for missing system dependencies

**Obsidian API Connection Fails**:
- Verify Obsidian Local REST API plugin installed and enabled
- Check API token is valid and not expired
- Confirm vault URL and port (default: http://localhost:27123)
- Test with curl: `curl -H "Authorization: Bearer TOKEN" http://localhost:27123/vault/`

**Ollama Not Running**:
- Start Ollama service: `ollama serve`
- Verify it's running: `curl http://192.168.68.10:11434/api/tags`
- Check available models: `ollama list`
- Pull required model: `ollama pull gemma3n:latest`
- Alternative models: `llama3:latest`, `llama3.2:3b`

**Python Import Errors**:
- Verify Python version: `python --version` (requires 3.10+)
- Install PyTorch with CUDA: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`
- Install Whisper: `pip install openai-whisper`
- Install requests: `pip install requests`
- Check CUDA installation: `nvidia-smi`
