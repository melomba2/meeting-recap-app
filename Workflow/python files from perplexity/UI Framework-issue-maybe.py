
# Create Component 1: UI Framework

ui_framework = """# Component 1: UI Framework Setup

## Overview

This component establishes the desktop application framework that will host your meeting recap processing workflow. The UI framework provides the window management, file system access, and bridge between the Python backend and user interface.

---

## Framework Decision: Tauri vs Electron

### Recommended: Tauri

**Why Tauri for This Project**:
- **Performance**: 3-10x smaller memory footprint than Electron
- **Size**: Final app size ~10MB vs 120MB+ for Electron
- **Security**: Rust-based backend with process isolation
- **Python Integration**: Built-in sidecar support for Python executables
- **GPU Access**: Better hardware access for RTX 5090 utilization
- **Native Feel**: Uses system WebView instead of bundling Chromium

**Trade-offs**:
- Smaller ecosystem than Electron
- Requires Rust toolchain for development
- Fewer existing UI component libraries specific to Tauri

### Alternative: Electron

**When to Choose Electron**:
- Team already experienced with Node.js
- Need specific Node.js native modules
- Want maximum cross-platform UI consistency
- Prioritize development speed over binary size

---

## Implementation Workflow

### Step 1: Environment Setup

**Install Required Tools**:

```bash
# Install Rust (required for Tauri)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install Node.js and npm (if not already installed)
# Download from: https://nodejs.org/

# Install Tauri CLI
npm install -g @tauri-apps/cli

# Verify installations
rustc --version
npm --version
cargo --version
```

**For Windows Users**:
- Install Visual Studio Build Tools (C++ development tools)
- Install WebView2 (usually pre-installed on Windows 10+)

---

### Step 2: Initialize Tauri Project

```bash
# Create new Tauri app
npm create tauri-app@latest

# Follow prompts:
# - App name: meeting-recap-app
# - Window title: Meeting Recap Processor
# - UI template: Vanilla (or React if preferred)
# - TypeScript: Yes (recommended)
# - Package manager: npm

cd meeting-recap-app

# Install dependencies
npm install
```

**Project Structure Created**:
```
meeting-recap-app/
├── src/                    # Frontend code
│   ├── index.html
│   ├── main.js
│   └── styles.css
├── src-tauri/              # Rust backend
│   ├── src/
│   │   └── main.rs
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   └── icons/
├── package.json
└── README.md
```

---

### Step 3: Configure Python Integration

**Add Python Sidecar Support**:

```bash
# Add Python plugin to Tauri
npx @tauri-apps/cli add python
```

This creates:
- `src-tauri/src-python/` directory for Python code
- Configuration in `tauri.conf.json` for Python integration
- Build process to bundle Python with app

**Configure Python Environment** (`src-tauri/src-python/requirements.txt`):
```txt
openai-whisper==20230314
torch>=2.0.0
torchaudio>=2.0.0
pydub>=0.25.1
python-dotenv>=1.0.0
fastapi>=0.104.0
uvicorn>=0.24.0
requests>=2.31.0
```

---

### Step 4: Configure Tauri Settings

**Edit `src-tauri/tauri.conf.json`**:

```json
{
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devPath": "http://localhost:1420",
    "distDir": "../dist"
  },
  "package": {
    "productName": "Meeting Recap Processor",
    "version": "0.1.0"
  },
  "tauri": {
    "allowlist": {
      "all": false,
      "fs": {
        "readFile": true,
        "writeFile": true,
        "readDir": true,
        "exists": true,
        "scope": ["$APPDATA/**", "$HOME/**"]
      },
      "path": {
        "all": true
      },
      "dialog": {
        "open": true,
        "save": true
      },
      "shell": {
        "execute": true,
        "sidecar": true,
        "scope": [
          { "name": "python", "sidecar": true }
        ]
      },
      "http": {
        "request": true,
        "scope": ["http://localhost:*", "https://localhost:*"]
      }
    },
    "bundle": {
      "active": true,
      "identifier": "com.yourname.meeting-recap",
      "icon": [
        "icons/32x32.png",
        "icons/128x128.png",
        "icons/128x128@2x.png",
        "icons/icon.icns",
        "icons/icon.ico"
      ],
      "externalBin": ["src-python/main"],
      "resources": ["src-python/**"]
    },
    "windows": [
      {
        "title": "Meeting Recap Processor",
        "width": 1200,
        "height": 800,
        "resizable": true,
        "fullscreen": false,
        "center": true,
        "minWidth": 800,
        "minHeight": 600
      }
    ]
  }
}
```

**Key Configuration Sections**:
- **allowlist.fs**: Enable file system access for reading/writing recordings
- **allowlist.dialog**: Enable file picker dialogs
- **allowlist.shell**: Allow executing Python sidecar
- **bundle.externalBin**: Bundle Python scripts with app
- **bundle.resources**: Include Python dependencies

---

### Step 5: Create Python Bridge

**Create Python Entry Point** (`src-tauri/src-python/main.py`):

```python
import sys
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(__name__)

# List of functions callable from UI
_tauri_plugin_functions = [
    "transcribe_audio",
    "analyze_transcript",
    "generate_recap",
    "get_status"
]

def transcribe_audio(file_path: str, model: str = "base") -> dict:
    """
    Transcribe audio file using Whisper.
    
    Args:
        file_path: Path to audio/video file
        model: Whisper model size (tiny, base, small, medium, large)
    
    Returns:
        dict with transcript_path and status
    """
    try:
        logger.info(f"Starting transcription for: {file_path}")
        
        # Import your existing transcription code
        from transcriber import WhisperTranscriber
        
        transcriber = WhisperTranscriber(model_size=model)
        transcript_path = transcriber.transcribe(file_path)
        
        logger.info(f"Transcription complete: {transcript_path}")
        
        return {
            "status": "success",
            "transcript_path": str(transcript_path),
            "message": "Transcription completed successfully"
        }
    
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }

def analyze_transcript(transcript_path: str, analysis_type: str = "meeting") -> dict:
    """
    Analyze transcript using Ollama/Gemma3n.
    
    Args:
        transcript_path: Path to transcript file
        analysis_type: Type of analysis (meeting, dnd, interview)
    
    Returns:
        dict with analysis_path and status
    """
    try:
        logger.info(f"Starting analysis for: {transcript_path}")
        
        # Import your existing analysis code
        from analyzer import TranscriptAnalyzer
        
        analyzer = TranscriptAnalyzer(analysis_type=analysis_type)
        analysis_path = analyzer.analyze(transcript_path)
        
        logger.info(f"Analysis complete: {analysis_path}")
        
        return {
            "status": "success",
            "analysis_path": str(analysis_path),
            "message": "Analysis completed successfully"
        }
    
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }

def generate_recap(transcript_path: str, session_number: int = 1) -> dict:
    """
    Generate D&D style recap from transcript.
    
    Args:
        transcript_path: Path to transcript file
        session_number: Session number for naming
    
    Returns:
        dict with recap_path and status
    """
    try:
        logger.info(f"Generating recap for: {transcript_path}")
        
        # Import your existing recap generation code
        from recap_generator import RecapGenerator
        
        generator = RecapGenerator()
        recap_path = generator.generate(transcript_path, session_number)
        
        logger.info(f"Recap generated: {recap_path}")
        
        return {
            "status": "success",
            "recap_path": str(recap_path),
            "message": "Recap generated successfully"
        }
    
    except Exception as e:
        logger.error(f"Recap generation error: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }

def get_status() -> dict:
    """Get system status and configuration."""
    import torch
    
    return {
        "status": "ready",
        "cuda_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "python_version": sys.version
    }

# Main entry point for Tauri plugin system
if __name__ == "__main__":
    logger.info("Python backend initialized")
    
    # Keep process alive for Tauri communication
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            # Parse command from Tauri
            command = json.loads(line.strip())
            func_name = command.get("function")
            args = command.get("args", [])
            kwargs = command.get("kwargs", {})
            
            # Call requested function
            if func_name in _tauri_plugin_functions:
                result = globals()[func_name](*args, **kwargs)
                print(json.dumps(result), flush=True)
            else:
                print(json.dumps({
                    "status": "error",
                    "message": f"Unknown function: {func_name}"
                }), flush=True)
        
        except Exception as e:
            logger.error(f"Main loop error: {str(e)}", exc_info=True)
            print(json.dumps({
                "status": "error",
                "message": str(e)
            }), flush=True)
```

---

### Step 6: Create Rust-Python Bridge

**Edit `src-tauri/src/main.rs`**:

```rust
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::command;
use serde::{Deserialize, Serialize};
use std::process::{Command, Stdio};
use std::io::{BufRead, BufReader, Write};

#[derive(Debug, Serialize, Deserialize)]
struct PythonCommand {
    function: String,
    args: Vec<serde_json::Value>,
    kwargs: serde_json::Map<String, serde_json::Value>,
}

#[derive(Debug, Serialize, Deserialize)]
struct PythonResponse {
    status: String,
    message: Option<String>,
    transcript_path: Option<String>,
    analysis_path: Option<String>,
    recap_path: Option<String>,
}

#[command]
async fn call_python(function: String, args: Vec<serde_json::Value>) -> Result<PythonResponse, String> {
    // Get path to bundled Python
    let python_path = "src-python/main.py"; // Will be bundled with app
    
    // Spawn Python process
    let mut child = Command::new("python")
        .arg(python_path)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to spawn Python: {}", e))?;
    
    // Send command to Python
    let command = PythonCommand {
        function,
        args,
        kwargs: serde_json::Map::new(),
    };
    
    let command_json = serde_json::to_string(&command)
        .map_err(|e| format!("Failed to serialize command: {}", e))?;
    
    if let Some(mut stdin) = child.stdin.take() {
        stdin.write_all(command_json.as_bytes())
            .map_err(|e| format!("Failed to write to Python stdin: {}", e))?;
        stdin.write_all(b"\n")
            .map_err(|e| format!("Failed to write newline: {}", e))?;
    }
    
    // Read response from Python
    if let Some(stdout) = child.stdout.take() {
        let reader = BufReader::new(stdout);
        if let Some(Ok(line)) = reader.lines().next() {
            let response: PythonResponse = serde_json::from_str(&line)
                .map_err(|e| format!("Failed to parse Python response: {}", e))?;
            return Ok(response);
        }
    }
    
    Err("No response from Python".to_string())
}

#[command]
fn select_file() -> Result<Option<String>, String> {
    use tauri::api::dialog::FileDialogBuilder;
    
    let (tx, rx) = std::sync::mpsc::channel();
    
    FileDialogBuilder::new()
        .add_filter("Media Files", &["mp4", "mp3", "wav", "m4a"])
        .pick_file(move |file_path| {
            tx.send(file_path).unwrap();
        });
    
    rx.recv()
        .map_err(|e| format!("Failed to receive file path: {}", e))
        .map(|path| path.map(|p| p.display().to_string()))
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![call_python, select_file])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

---

### Step 7: Create Frontend UI

**Basic HTML Structure** (`src/index.html`):

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Meeting Recap Processor</title>
    <link rel="stylesheet" href="styles.css" />
</head>
<body>
    <div id="app">
        <header>
            <h1>Meeting Recap Processor</h1>
            <div id="status">Ready</div>
        </header>
        
        <main>
            <section class="upload-section">
                <div id="drop-zone" class="drop-zone">
                    <p>Drag & drop recording here or click to select</p>
                    <button id="select-file-btn">Select File</button>
                </div>
                
                <div id="file-info" class="file-info hidden">
                    <p>Selected: <span id="file-name"></span></p>
                </div>
            </section>
            
            <section class="controls-section">
                <div class="control-group">
                    <label for="process-type">Process Type:</label>
                    <select id="process-type">
                        <option value="meeting">Meeting Notes</option>
                        <option value="dnd">D&D Recap</option>
                        <option value="interview">Interview Analysis</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <label for="model-size">Whisper Model:</label>
                    <select id="model-size">
                        <option value="base">Base (Fast)</option>
                        <option value="small">Small (Balanced)</option>
                        <option value="medium">Medium (Accurate)</option>
                        <option value="large">Large (Most Accurate)</option>
                    </select>
                </div>
                
                <button id="process-btn" class="primary-btn" disabled>
                    Start Processing
                </button>
            </section>
            
            <section id="progress-section" class="progress-section hidden">
                <h2>Processing...</h2>
                <div class="progress-bar">
                    <div id="progress-fill" class="progress-fill"></div>
                </div>
                <p id="progress-message">Initializing...</p>
            </section>
            
            <section id="results-section" class="results-section hidden">
                <h2>Results</h2>
                <div class="result-item">
                    <h3>Transcript</h3>
                    <button class="view-btn" data-file="transcript">View</button>
                    <button class="copy-btn" data-file="transcript">Copy Path</button>
                </div>
                <div class="result-item">
                    <h3>Analysis</h3>
                    <button class="view-btn" data-file="analysis">View</button>
                    <button class="copy-btn" data-file="analysis">Copy Path</button>
                </div>
            </section>
        </main>
    </div>
    
    <script type="module" src="main.js"></script>
</body>
</html>
```

**JavaScript Logic** (`src/main.js`):

```javascript
const { invoke } = window.__TAURI__.tauri;

let selectedFile = null;
let currentResults = {};

// File selection
document.getElementById('select-file-btn').addEventListener('click', async () => {
    try {
        const filePath = await invoke('select_file');
        if (filePath) {
            selectedFile = filePath;
            document.getElementById('file-name').textContent = filePath.split(/[\\/]/).pop();
            document.getElementById('file-info').classList.remove('hidden');
            document.getElementById('process-btn').disabled = false;
        }
    } catch (error) {
        console.error('Error selecting file:', error);
        alert('Failed to select file: ' + error);
    }
});

// Drag and drop
const dropZone = document.getElementById('drop-zone');

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', async (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        selectedFile = files[0].path;
        document.getElementById('file-name').textContent = files[0].name;
        document.getElementById('file-info').classList.remove('hidden');
        document.getElementById('process-btn').disabled = false;
    }
});

// Process button
document.getElementById('process-btn').addEventListener('click', async () => {
    if (!selectedFile) return;
    
    const processType = document.getElementById('process-type').value;
    const modelSize = document.getElementById('model-size').value;
    
    // Show progress section
    document.getElementById('progress-section').classList.remove('hidden');
    document.getElementById('results-section').classList.add('hidden');
    document.getElementById('process-btn').disabled = true;
    
    try {
        // Step 1: Transcribe
        updateProgress(30, 'Transcribing audio...');
        const transcriptResult = await invoke('call_python', {
            function: 'transcribe_audio',
            args: [selectedFile, modelSize]
        });
        
        if (transcriptResult.status !== 'success') {
            throw new Error(transcriptResult.message);
        }
        
        currentResults.transcript = transcriptResult.transcript_path;
        
        // Step 2: Analyze
        updateProgress(70, 'Analyzing transcript...');
        const analysisResult = await invoke('call_python', {
            function: 'analyze_transcript',
            args: [transcriptResult.transcript_path, processType]
        });
        
        if (analysisResult.status !== 'success') {
            throw new Error(analysisResult.message);
        }
        
        currentResults.analysis = analysisResult.analysis_path;
        
        // Step 3: Generate recap (if D&D)
        if (processType === 'dnd') {
            updateProgress(90, 'Generating recap...');
            const recapResult = await invoke('call_python', {
                function: 'generate_recap',
                args: [transcriptResult.transcript_path, 1]
            });
            
            if (recapResult.status === 'success') {
                currentResults.recap = recapResult.recap_path;
            }
        }
        
        // Complete
        updateProgress(100, 'Processing complete!');
        setTimeout(() => {
            document.getElementById('progress-section').classList.add('hidden');
            document.getElementById('results-section').classList.remove('hidden');
            document.getElementById('process-btn').disabled = false;
        }, 1000);
        
    } catch (error) {
        console.error('Processing error:', error);
        alert('Processing failed: ' + error);
        document.getElementById('progress-section').classList.add('hidden');
        document.getElementById('process-btn').disabled = false;
    }
});

function updateProgress(percent, message) {
    document.getElementById('progress-fill').style.width = percent + '%';
    document.getElementById('progress-message').textContent = message;
}

// Check Python backend status on startup
window.addEventListener('DOMContentLoaded', async () => {
    try {
        const status = await invoke('call_python', {
            function: 'get_status',
            args: []
        });
        
        if (status.cuda_available) {
            document.getElementById('status').textContent = `Ready (GPU: ${status.gpu_name})`;
            document.getElementById('status').classList.add('status-gpu');
        }
    } catch (error) {
        console.error('Failed to get status:', error);
        document.getElementById('status').textContent = 'Backend not ready';
        document.getElementById('status').classList.add('status-error');
    }
});
```

---

### Step 8: Development Workflow

**Run Development Server**:

```bash
# Terminal 1: Start frontend dev server
npm run dev

# Terminal 2: Start Tauri in dev mode
npm run tauri dev
```

**Hot Reload**: 
- Frontend changes reload automatically
- Rust changes require rebuild (automatic with `tauri dev`)
- Python changes require restarting Tauri

**Debugging**:
- Frontend: Use browser DevTools (right-click → Inspect)
- Rust: Check terminal output from `tauri dev`
- Python: Check `app.log` file or stderr output

---

### Step 9: Testing

**Test Python Integration**:

```javascript
// Test calling Python from DevTools console
await invoke('call_python', {
    function: 'get_status',
    args: []
});
```

**Test File Selection**:
- Click "Select File" button
- Verify file picker opens
- Select a test MP4 file
- Confirm filename displays correctly

**Test Process Flow**:
- Select a short test recording
- Click "Start Processing"
- Verify progress updates appear
- Confirm results section shows after completion

---

### Step 10: Building for Distribution

**Create Production Build**:

```bash
# Build for current platform
npm run tauri build

# Output locations:
# Windows: src-tauri/target/release/bundle/nsis/*.exe
# macOS: src-tauri/target/release/bundle/dmg/*.dmg
# Linux: src-tauri/target/release/bundle/appimage/*.AppImage
```

**Build Configuration**:
- Ensure all Python dependencies are bundled
- Include Whisper models or implement download-on-first-run
- Test on clean machine without development tools

---

## Troubleshooting

### Python Not Found
- Verify Python is in system PATH
- Check `tauri.conf.json` has correct Python path
- Try absolute path to Python executable

### GPU Not Detected in App
- Verify CUDA drivers installed
- Check app has permission to access GPU
- Test with `nvidia-smi` command

### File Access Denied
- Check `tauri.conf.json` allowlist includes required paths
- Verify user has read/write permissions
- Test with different file locations

### Build Fails
- Clear build cache: `cargo clean`
- Update dependencies: `npm update` and `cargo update`
- Check error messages for missing system dependencies

---

## Next Steps

After completing this component:
1. Verify app launches and UI displays correctly
2. Confirm Python backend communication works
3. Test file selection and basic workflows
4. Proceed to **Component 2: Backend Integration**

---

## Resources

- **Tauri Docs**: https://tauri.app/v1/guides/
- **Tauri Python Plugin**: https://github.com/tauri-apps/tauri-plugin-python
- **Rust Book**: https://doc.rust-lang.org/book/
- **Serde JSON**: https://docs.rs/serde_json/

---

## Validation Checklist

- [ ] Tauri project initialized and runs
- [ ] Python sidecar configured and callable
- [ ] File picker works and returns paths
- [ ] Basic UI renders correctly
- [ ] Can call Python functions from frontend
- [ ] Progress UI updates during processing
- [ ] Results display after completion
- [ ] Development hot-reload works
- [ ] Production build completes successfully
- [ ] App runs on clean test machine
"""

with open('01_ui_framework_setup.md', 'w', encoding='utf-8') as f:
    f.write(ui_framework)

print("✓ Created: 01_ui_framework_setup.md")
