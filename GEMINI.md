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

**✅ Phase 4: Local API Server** - Complete
- Full REST API implementation in `api_server.py` with FastAPI
- Endpoints for `transcribe`, `analyze`, and `recap` with background job processing
- Job tracking with `/api/status/{job_id}` and `/api/jobs` endpoints
- API key authentication implemented
- Comprehensive API documentation in `API_EXAMPLES.md`

**✅ Phase 5: Testing & Polish** - Complete
- Desktop application testing guide created (`DESKTOP_APP_TESTING.md`)
- Fixed multiple integration issues (see debugging notes below)
- ✅ Transcription now working successfully after debugging FFmpeg and Python bridge issues
- ✅ All features fully operational and tested end-to-end

**✅ Phase 6: Remote GPU Transcription** - Complete
- `RemoteWhisperClient` class created for HTTP-based communication with remote Whisper server
- UI toggle to switch between Local GPU and Remote GPU transcription modes
- Remote server configuration with host input and connection test button
- Automatic fallback error handling when remote server is unavailable
- Settings persistence using localStorage
- Custom FastAPI DIY Whisper server with dynamic model loading
- Full integration with existing Tauri backend and Python bridge

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

### Transcription failure debugging - FIXED

**Status:** ✅ Resolved

**Root Problems Found and Fixed:**

1. **Missing FFmpeg Installation**
   - **Problem:** `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`
   - **Root Cause:** FFmpeg was not installed on the system
   - **Solution:** Installed FFmpeg via Homebrew: `brew install ffmpeg`

2. **Corrupted whisper_processor.py File**
   - **Problem:** `IndentationError: unexpected indent` at line 1
   - **Root Cause:** File was truncated and missing class definition and imports
   - **Solution:** Restored from backup file and cleaned up indentation errors, removed duplicate code

3. **Silent Python Errors (stderr not displayed)**
   - **Problem:** Python debug output was being captured but not shown in terminal
   - **Root Cause:** Rust code in `main.rs:transcribe_audio()` was capturing stderr but only displaying it on process failure
   - **Solution:** Modified Rust code to always print stderr and stdout to console with markers for visibility

4. **Missing Model Loading in Transcription Flow**
   - **Problem:** `transcribe_file()` was called without loading the Whisper model first
   - **Root Cause:** `main.py` created WhisperProcessor but didn't call `load_model()`
   - **Solution:** Added explicit `processor.load_model()` call after processor initialization with proper error handling

5. **Inadequate Error Logging in extract_audio()**
   - **Problem:** Audio extraction failures returned `False` without showing FFmpeg error messages
   - **Root Cause:** FFmpeg stderr output was being captured but not logged
   - **Solution:** Added detailed FFmpeg error logging to show exit codes and stderr output

**Files Modified:**
- `src-python/whisper_processor.py` - Fixed indentation, improved error handling
- `src-python/main.py` - Added model loading, enhanced debug output
- `src-tauri/src/main.rs` - Modified to always display stderr/stdout from Python

### Analysis and Recap Generation Pipeline Fixes - FIXED

**Status:** ✅ Resolved

**Root Problems Found and Fixed:**

1. **JSON Serialization Errors in Rust**
   - **Problem:** `Invalid JSON: Unterminated string starting at: line 1 column 30`
   - **Root Cause:** Format strings used in `generate_recap()`, `analyze_transcript()`, and `transcribe_audio()` functions didn't properly escape JSON special characters in file paths
   - **Solution:** Replaced format string approach with `serde_json::json!()` macro which automatically handles escaping
   ```rust
   // Before (unsafe)
   let command = format!(
       r#"{{"command": "recap", "file": "{}", "style": "{}"}}"#,
       file_path.replace("\\", "\\\\"),  // Insufficient escaping
       style
   );

   // After (safe)
   let command = serde_json::json!({
       "command": "recap",
       "file": file_path,      // Properly escaped automatically
       "style": style
   });
   let command = command.to_string();
   ```

2. **File Path vs Content Returned from Analysis**
   - **Problem:** `[Errno 63] File name too long` error where analysis file content was being used as a filename
   - **Root Cause:** When transcripts were large and needed chunking, `transcript_analyzer.py:analyze_transcript()` returned the analysis content directly instead of the file path when `output_path` was provided. This caused `main.py` to receive text instead of a path, which was then used as a filename in recap generation
   - **Solution:** Fixed control flow to ensure file is always saved to `output_path` and the file path (not content) is returned
   ```python
   # Fixed logic ensures result is always saved and path is returned
   if output_path:
       output_file = Path(output_path)
       output_file.parent.mkdir(parents=True, exist_ok=True)
       with open(output_file, 'w', encoding='utf-8') as f:
           f.write(result)
       return str(output_file)  # Returns PATH, not content
   ```

3. **Missing `save_recap()` Method**
   - **Problem:** `AttributeError: 'DNDRecapGenerator' object has no attribute 'save_recap'`
   - **Root Cause:** Method was called in `main()` function but not defined in the class
   - **Solution:** Implemented `save_recap()` method in `recap_generator.py`

**Flow Fixed:**
- ✅ Transcription → Returns transcript file path
- ✅ Analysis → Chunking (if needed) → Save to file → Returns analysis file path
- ✅ Recap Generation → Reads analysis file → Generates recap → Returns recap file path

**Files Modified:**
- `src-tauri/src/main.rs` - Changed `transcribe_audio()`, `analyze_transcript()`, `generate_recap()` to use proper JSON serialization
- `src-python/transcript_analyzer.py` - Fixed control flow to always save and return file path
- `src-python/recap_generator.py` - Added missing `save_recap()` method

### Remote GPU Transcription Setup & Debugging - FIXED

**Status:** ✅ Fully Operational

**Setup Environment:**
- Remote Machine: Windows with NVIDIA GPU (RTX 5090)
- Remote Machine OS: Windows with WSL2 for Python environment
- App Machine: macOS
- Network: Local network (192.168.68.x subnet)

**Problems Encountered and Resolved:**

1. **pip install faster-whisper-server Failed**
   - **Problem:** `faster-whisper-server` not found on PyPI
   - **Root Cause:** Package name was incorrect or unavailable on PyPI
   - **Solution:** Created custom DIY FastAPI server instead of relying on third-party package
   - **Result:** More flexibility and direct control over the server implementation

2. **WSL Networking - Server Only Binding to Localhost**
   - **Problem:** Server running on Windows WSL2 only listening on `127.0.0.1:5000`, not accessible from network
   - **Root Cause:** WSL2 has isolated network stack; binding to `0.0.0.0` inside WSL doesn't expose to Windows network interfaces
   - **Solution:** Set up Windows Port Forwarding with netsh:
   ```bash
   netsh interface portproxy add v4tov4 listenport=5000 listenaddress=0.0.0.0 connectport=5000 connectaddress=172.28.64.22
   ```
   - **Key Learning:** WSL IP (172.28.64.22) needs to be explicitly forwarded to Windows network

3. **Missing /models Endpoint**
   - **Problem:** App's `check_whisper_health()` calls `/models` endpoint, but DIY server didn't have it
   - **Root Cause:** Initial server implementation only had `/health` and `/transcribe` endpoints
   - **Solution:** Added `/models` endpoint returning list of available Whisper models
   - **Result:** Health check now returns available models for UI feedback

4. **Hardcoded Model in Server**
   - **Problem:** Server loaded only "medium" model; couldn't use other models selected in UI
   - **Root Cause:** Model was hardcoded in server initialization
   - **Solution:** Implemented dynamic model loading on-demand

5. **Python Environment Mismatch**
   - **Problem:** App was using Python 3.9, but key packages (`requests`, etc.) only installed in Python 3.12
   - **Root Cause:** During Python 3.12 upgrade, packages were only installed for 3.12 in system location (Homebrew protected environment)
   - **Solution:** Created Python 3.12 virtual environment and installed all dependencies there
   - Updated `~/.zshrc` to auto-activate the virtual environment

6. **Rust Response Parsing**
   - **Problem:** `check_whisper_health` Rust command wasn't properly parsing Python response
   - **Root Cause:** Python response had data nested in `data` field, but Rust was returning the full response
   - **Solution:** Updated Rust code to extract the `data` field from response

**Server Implementation - DIY FastAPI**

Created simple, working Whisper server in `whisper_server.py`:
- Loads Whisper model once at startup with GPU acceleration (float16)
- Dynamically switches models on-demand (tiny, base, small, medium, large)
- Provides `/health` endpoint for connectivity testing
- Provides `/models` endpoint for listing available models
- Provides `/transcribe` endpoint accepting multipart file upload
- Caches loaded model to avoid reloading for efficiency

**Final Configuration:**

1. **Windows (Remote Server):** WSL2 Python with port forwarding to Windows
2. **macOS (App Machine):** Python 3.12 virtual environment with all dependencies
3. **Network:** Both machines on same local network with port 5000 open

**Testing Status:**
- ✅ curl health check from macOS works
- ✅ curl models check returns available models
- ✅ App Test Connection button successfully connects
- ✅ Ready for actual transcription testing

### cuDNN Library Missing Error - FIXED

**Status:** ✅ Resolved

**Problem:** GPU acceleration on remote WSL2 server failed when loading cuDNN libraries:
```
Unable to load any of {libcudnn_ops.so.9.1.0, libcudnn_ops.so.9.1, libcudnn_ops.so.9, libcudnn_ops.so}
Invalid handle. Cannot load symbol cudnnCreateTensorDescriptor
Aborted (core dumped)
```

**Root Cause:** Whisper model loaded but cuDNN (CUDA Deep Neural Network library) was missing for GPU acceleration, causing server crash and client-side `RemoteDisconnected` error.

**Solution:**
1. Downloaded cuDNN 9.1+ from https://developer.nvidia.com/cudnn
2. Extracted to `~/cudnn` on WSL2 and added to `LD_LIBRARY_PATH`:
   ```bash
   export LD_LIBRARY_PATH="$HOME/cudnn/lib:$LD_LIBRARY_PATH"
   ```
3. Verified with `ldconfig -p | grep cudnn`

**Result:** Server now successfully runs transcription with GPU acceleration. All three pipeline stages (transcribe → analyze → recap) fully operational.

## Project Overview

**Meeting Recap App** - A desktop application that processes meeting and D&D session recordings to generate transcripts, analysis, and narrative recaps. The project converts existing batch/Python-based workflows into a unified desktop app with local REST API for third-party tool integration.

**Key Capabilities**:
- Audio transcription using Whisper (optimized for RTX 5090 GPU, with remote GPU support)
- Content analysis using Ollama/Gemma3n
- D&D-style narrative recap generation with TTS-ready output
- Local REST API server for automation and third-party integrations
- Remote GPU transcription via HTTP API to offload processing to another machine

## Technology Stack

**Desktop Framework**: Tauri (recommended) or Electron
- Tauri offers 3-10x smaller memory footprint and better GPU access
- Frontend: HTML/CSS/JavaScript or React/Vue/Svelte
- Python integration via Tauri sidecar

**Backend**: Python 3.10+
- Whisper for local transcription
- faster-whisper for remote GPU transcription (via HTTP API)
- Ollama for LLM inference
- FastAPI for REST API server
- Obsidian Local REST API client for vault integration

**Remote Transcription Server** (Optional):
- faster-whisper-server for high-performance remote transcription
- 4x faster than original Whisper with same accuracy
- CUDA-accelerated with efficient memory usage

## System Architecture

The application consists of five major components that communicate via JSON:

1. **Desktop UI Framework** ✅ - Tauri app providing the user interface
   - Built with Rust backend + HTML/CSS/JS frontend
   - Vite for hot-reload development
   - File upload with drag-and-drop support

2. **Python Backend** ✅ - Core processing modules (transcription, analysis, recap generation)
   - Communication via stdin/stdout JSON-RPC
   - Rust spawns Python processes and pipes commands
   - Existing scripts in `python scripts/` directory
   - Supports both local and remote transcription via mode selection

3. **Local REST API Server** ✅ - Exposes workflow functions as HTTP endpoints for third-party tools
   - FastAPI server implemented in `api_server.py`
   - Endpoints for transcribe, analyze, recap
   - API key authentication implemented
   - Currently debugging startup issues

5. **Remote Transcription Server** ✅ (Optional) - faster-whisper-server for GPU acceleration on another machine
   - HTTP API for transcription requests
   - 4x faster than local Whisper with same accuracy
   - Runs on configurable port (default: 9000)
   - See `REMOTE_WHISPER_SETUP.md` for setup instructions

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

**Remote Transcription Server**:
- Python sends HTTP POST to `{whisper_host}/transcribe` with audio file
- Multipart form data with file, model, and language parameters
- Returns JSON: `{"text": "transcribed content..."}`
- Health check via `GET {whisper_host}/health`
- Uses same HTTP pattern as Ollama integration for consistency

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

### Transcription Solution (Fixed)

The transcription issues have been resolved with the following key fixes:

1. **FFmpeg Installation**: FFmpeg was missing from the system and has been installed to enable audio processing from video files:
   ```bash
   curl -L https://evermeet.cx/ffmpeg/ffmpeg-7.1.zip -o ~/bin/ffmpeg.zip
   cd ~/bin 
   unzip ffmpeg.zip
   chmod +x ffmpeg
   export PATH="$HOME/bin:$PATH"
   ```

2. **Python Script Enhancements**: Improved error handling and debug information in `src-python/whisper_processor.py` and `src-python/main.py` with better path resolution and type safety.

3. **Indentation Fix**: Resolved `IndentationError: unexpected indent` in `src-python/main.py` line 75 by fixing inconsistent indentation in the transcription section.

Transcription now works properly in the Tauri desktop application after these fixes.

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
│   ├── api_server.py       # Local REST API server (FastAPI) ✅ IMPLEMENTED
│   └── remote_whisper_client.py  # Remote Whisper server integration ✅ IMPLEMENTED
├── src/                    # Frontend (JS/HTML/CSS) ✅ IMPLEMENTED
│   ├── index.html          # Main window with modern UI
│   ├── main.js             # Application logic and Tauri bridge
│   ├── styles.css          # Professional styling
│   └── assets/             # Static assets (images, icons)
├── config/                 # Configuration files ✅ IMPLEMENTED
│   └── defaults.json       # Default settings (Whisper, Ollama, paths)
├── node_modules/           # npm dependencies
├── package.json            # npm configuration
├── vite.config.js          # Vite build configuration
├── Workflow/               # Development workflow documentation
│   ├── 00_main_app_workflow.md
│   ├── 01_ui_framework_setup.md
│   ├── 02_backend_integration.md
│   ├── 03_file_progress.md
│   └── 04_local_api_server.md
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

**remote_whisper_client.py**: Remote Whisper server integration
- HTTP client for communicating with remote Whisper server
- Model selection and dynamic loading
- Health check and server connectivity testing

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

The project is organized into six development phases (see Workflow/00_main_app_workflow.md):

1. Foundation Setup - Tauri/Electron initialization and Python bridge
2. Backend Integration - Refactor batch scripts into modular Python
3. UI Implementation - Build interface with drag-and-drop and progress tracking
4. Local API Server - Expose functions as REST endpoints
5. Testing & Polish - End-to-end testing and distribution builds
6. Remote GPU Transcription - Support transcription on remote machine via HTTP API

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
