# Meeting Recap App - Main Development Workflow

## Project Overview

**Goal**: Convert existing batch/Python-based meeting and D&D session recording processor into a local desktop application with Obsidian vault integration and local service interoperability.

**Current State**: 
- Collection of batch scripts and Python modules
- Optimized for RTX 5090 GPU processing
- Uses Whisper for transcription, Gemma3n for analysis
- Generates D&D-style recaps with TTS-ready output

**Target State**: 
- Unified desktop application with modern GUI
- Seamless Obsidian vault integration via REST API
- Local API server for third-party integrations
- User-friendly interface for non-technical users

---

## System Architecture

### Core Components

1. **Python Backend (Existing)**
   - Whisper transcription engine
   - Ollama/Gemma3n analysis pipeline
   - File processing and management
   - Audio extraction from MP4

2. **Desktop UI Framework (New)**
   - Choice: Tauri (Rust-based, lightweight) or Electron (Node.js-based, mature)
   - Frontend: HTML/CSS/JavaScript or React/Vue/Svelte
   - Native system integration

3. **Local REST API Server (New)**
   - Exposes workflow functions as HTTP endpoints
   - Authentication via API keys
   - Supports integration with Obsidian and other local tools

4. **Obsidian Integration (New)**
   - Uses Obsidian Local REST API plugin
   - Bidirectional communication: read vault structure, write recaps
   - Automatic note creation with proper formatting

5. **Configuration Management (New)**
   - User preferences storage
   - Model selection and parameters
   - Folder path management
   - API key management

---

## Development Phases

### Phase 1: Foundation Setup (Weeks 1-2)

**Objectives**:
- Choose UI framework (Tauri recommended for performance/size)
- Set up project structure
- Establish Python-to-UI communication bridge

**Tasks**:
1. Initialize Tauri or Electron project
2. Configure Python sidecar or subprocess integration
3. Create basic project folder structure
4. Set up development environment with hot-reload
5. Verify Python scripts can be called from UI

**Deliverables**:
- Working skeleton app that can launch and call a simple Python function
- Project structure with organized directories
- Development documentation

---

### Phase 2: Backend Integration (Weeks 3-4)

**Objectives**:
- Wrap existing Python scripts as callable modules
- Implement process management and monitoring
- Handle file I/O and path management

**Tasks**:
1. Refactor batch scripts into Python module functions
2. Create Python API layer for UI communication
3. Implement progress tracking and status reporting
4. Add error handling and logging
5. Create file watcher for recording folder

**Deliverables**:
- Python backend module with clean API surface
- JSON-based communication protocol
- Logging system for debugging
- Progress reporting mechanism

---

### Phase 3: UI Implementation (Weeks 5-7)

**Objectives**:
- Build intuitive user interface
- Implement drag-and-drop file handling
- Create real-time progress visualization

**Tasks**:
1. Design UI mockups and user flows
2. Implement main application window
3. Build file upload/drag-and-drop interface
4. Create progress bar with stage indicators
5. Build settings/preferences panel
6. Implement result viewer with syntax highlighting

**Deliverables**:
- Functional desktop application UI
- File management interface
- Settings configuration screen
- Progress monitoring dashboard

---

### Phase 4: Obsidian Integration (Weeks 8-9)

**Objectives**:
- Connect to Obsidian Local REST API
- Implement automatic note creation
- Handle vault navigation and file placement

**Tasks**:
1. Install and configure Obsidian Local REST API plugin
2. Implement API client in application
3. Create vault browser to select target folders
4. Build note template system
5. Implement automatic note creation with metadata
6. Add vault structure caching for performance

**Deliverables**:
- Working Obsidian integration
- Template system for generated notes
- Vault navigation UI
- Automatic note creation workflow

---

### Phase 5: Local API Server (Weeks 10-11)

**Objectives**:
- Expose application functions as REST API
- Enable third-party tool integration
- Implement security and authentication

**Tasks**:
1. Design REST API endpoints following best practices
2. Implement FastAPI or Flask server in Python backend
3. Create API key generation and management
4. Build request/response validation
5. Implement rate limiting and error handling
6. Create API documentation (OpenAPI/Swagger)

**Deliverables**:
- Local REST API server running on localhost
- API documentation
- Authentication system
- Example integration scripts

---

### Phase 6: Preset Management (Week 12)

**Objectives**:
- Allow users to save workflow configurations
- Enable quick switching between analysis types
- Support custom prompt templates

**Tasks**:
1. Design preset data structure
2. Build preset management UI
3. Implement preset save/load/delete functions
4. Create default presets (meeting, D&D, interview, etc.)
5. Add prompt template editor
6. Implement preset import/export

**Deliverables**:
- Preset management system
- Pre-configured templates for common use cases
- Import/export functionality
- Custom prompt editor

---

### Phase 7: Testing & Polish (Weeks 13-14)

**Objectives**:
- Comprehensive testing across workflows
- Bug fixes and performance optimization
- Documentation and user guide

**Tasks**:
1. Test all workflows end-to-end
2. Performance profiling and optimization
3. Error handling improvements
4. Create user documentation
5. Build installer/packager
6. Prepare distribution builds (Windows, Mac, Linux)

**Deliverables**:
- Tested, stable application
- User documentation and guides
- Installation packages for target platforms
- Release notes

---

## Technical Integration Points

### Python Backend → UI Communication

**Method**: JSON-RPC over stdin/stdout or HTTP
- UI sends commands as JSON objects
- Python processes and returns JSON responses
- Progress updates streamed via callbacks or polling

**Example Flow**:
```json
// UI → Python
{
  "command": "transcribe",
  "file": "/path/to/recording.mp4",
  "model": "large-v3",
  "settings": {...}
}

// Python → UI (progress)
{
  "status": "processing",
  "stage": "transcription",
  "progress": 45,
  "message": "Transcribing audio..."
}

// Python → UI (complete)
{
  "status": "complete",
  "transcript_path": "/path/to/transcript.txt",
  "duration": "8m 34s"
}
```

### Obsidian REST API Integration

**Endpoint Usage**:
- `GET /vault/` - List vault contents
- `POST /vault/[path]` - Create new note
- `PATCH /vault/[path]` - Update existing note
- `GET /vault/[path]` - Read note content

**Authentication**: Bearer token stored in app settings

**Example Integration**:
```javascript
// Create recap note in Obsidian
const response = await fetch('http://localhost:27123/vault/D&D/Session 42 Recap.md', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + apiKey,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    content: recapContent,
    frontmatter: {
      date: '2025-10-27',
      session: 42,
      type: 'recap'
    }
  })
});
```

### Local API Server Design

**Base URL**: `http://localhost:8765` (configurable)

**Core Endpoints**:
- `POST /api/transcribe` - Upload and transcribe audio
- `POST /api/analyze` - Analyze existing transcript
- `POST /api/recap` - Generate D&D recap
- `GET /api/status/{job_id}` - Check job status
- `GET /api/results/{job_id}` - Retrieve results

**Authentication**: API key in header: `X-API-Key: {key}`

---

## Folder Structure

```
meeting-recap-app/
├── src-tauri/              # Tauri backend (Rust)
│   ├── src/
│   │   └── main.rs         # Tauri main process
│   ├── Cargo.toml          # Rust dependencies
│   └── tauri.conf.json     # App configuration
├── python scripts/         # Python backend (existing scripts)
│   ├── local_processor.py      # Whisper transcription (RTX 5090 optimized)
│   ├── transcript_analyzer.py  # Ollama/Gemma3n analysis module
│   └── recap_generator.py      # D&D recap generation
├── src-python/             # Python backend (app integration layer)
│   ├── main.py             # Entry point for Python processes
│   ├── file_handler.py     # File I/O operations
│   ├── api_server.py       # Local REST API server
│   └── obsidian_client.py  # Obsidian API integration
├── src/                    # Frontend (JS/HTML/CSS)
│   ├── index.html          # Main window
│   ├── main.js             # Application logic
│   ├── renderer.js         # UI interactions
│   ├── styles.css          # Styling
│   └── components/         # Reusable UI components
│       ├── FileUpload.jsx
│       ├── ProgressBar.jsx
│       ├── SettingsPanel.jsx
│       └── ResultsViewer.jsx
├── config/                 # Configuration files
│   ├── defaults.json       # Default settings
│   └── presets/            # Preset configurations
├── Workflow/               # Development workflow documentation
│   ├── 00_main_app_workflow.md
│   ├── 01_ui_framework_setup.md
│   ├── 02_backend_integration.md
│   ├── 03_file_progress.md
│   ├── 04_obsidian_integration.md
│   └── 05_local_api_server.md
└── package.json            # Node.js dependencies
```

---

## Technology Stack

### Desktop Framework
**Option A: Tauri (Recommended)**
- Rust-based, extremely lightweight (< 10MB)
- Native performance
- Smaller memory footprint
- Python integration via sidecar

**Option B: Electron**
- Node.js-based, mature ecosystem
- Larger but more JavaScript-native
- Extensive community support

### Frontend
- **HTML/CSS/JavaScript** (vanilla) or **React/Svelte**
- CSS framework: Tailwind CSS or native styling

### Backend
- **Python 3.10+** (existing scripts)
- **FastAPI** (REST API server)
- **Whisper** (transcription)
- **Ollama** (LLM inference)

### Integrations
- **Obsidian Local REST API** (vault integration)
- **Python-shell** or **Tauri sidecar** (Python communication)

---

## Security Considerations

1. **API Keys**: Store securely, never in plaintext
   - Use system keychain (Windows Credential Manager, macOS Keychain)
   - Encrypt configuration files

2. **Local API**: 
   - Bind only to localhost (127.0.0.1)
   - Require API key authentication
   - Implement rate limiting

3. **File Access**:
   - Validate all file paths
   - Prevent directory traversal attacks
   - Sandbox Python process permissions

4. **Obsidian Integration**:
   - Validate API tokens before use
   - Handle vault permissions properly
   - Never expose vault contents to external networks

---

## Performance Optimization

1. **GPU Utilization**: Ensure Python processes can access RTX 5090
2. **Async Operations**: Use async/await for file I/O and API calls
3. **Progress Streaming**: Update UI without blocking main thread
4. **Caching**: Cache Obsidian vault structure, model configurations
5. **Resource Management**: Properly cleanup Python processes and temp files

---

## Testing Strategy

### Unit Tests
- Python module functions
- API endpoint validation
- File handling operations

### Integration Tests
- Full transcription → analysis → output workflow
- Obsidian API communication
- Preset loading and execution

### End-to-End Tests
- Complete user workflows from recording upload to Obsidian note creation
- Multi-file batch processing
- Error recovery scenarios

### User Acceptance Testing
- Usability testing with non-technical users
- Performance testing with large files
- Cross-platform compatibility validation

---

## Distribution

### Build Process
1. Bundle Python dependencies with app
2. Include Ollama models or download on first run
3. Sign application binaries (code signing)
4. Create installers for each platform

### Platform Targets
- **Windows**: .exe installer (NSIS or WiX)
- **macOS**: .dmg or .app bundle
- **Linux**: .AppImage or .deb package

### Updates
- Implement auto-update mechanism (Tauri updater)
- Version checking on startup
- Optional update notifications

---

## Future Enhancements

1. **Cloud Sync** (optional): Backup recaps to cloud storage
2. **Multi-Vault Support**: Work with multiple Obsidian vaults
3. **Plugin System**: Allow community extensions
4. **Mobile Companion**: View recaps on mobile devices
5. **Collaboration**: Share recaps with team members
6. **Advanced Analytics**: Session statistics, speaker identification
7. **Real-Time Transcription**: Live capture during meetings

---

## Success Metrics

- Application launches successfully on all platforms
- Transcription accuracy matches or exceeds current batch process
- Processing time equivalent to current workflow
- Obsidian notes created automatically with proper formatting
- Local API successfully integrates with third-party tools
- User can complete full workflow without command-line interaction

---

## Resources & References

- **Tauri Documentation**: https://tauri.app/
- **Obsidian Local REST API**: https://github.com/coddingtonbear/obsidian-local-rest-api
- **FastAPI**: https://fastapi.tiangolo.com/
- **Whisper**: https://github.com/openai/whisper
- **Ollama**: https://ollama.ai/
- **REST API Best Practices**: https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design

---

## Contact & Support

- Developer: [Your Name]
- Repository: [GitHub URL]
- Issues: [Issue Tracker URL]
- Documentation: [Docs URL]
