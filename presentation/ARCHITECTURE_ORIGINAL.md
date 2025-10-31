# Meeting Recap Processor - Architecture & Workflow Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Technology Stack](#technology-stack)
3. [Component Architecture](#component-architecture)
4. [Data Flow & Processing Pipeline](#data-flow--processing-pipeline)
5. [Frontend UI Workflow](#frontend-ui-workflow)
6. [Tauri Bridge (IPC)](#tauri-bridge-ipc)
7. [Python Backend Processing](#python-backend-processing)
8. [AI Prompt Instructions by Style](#ai-prompt-instructions-by-style)
9. [Configuration & Settings](#configuration--settings)
10. [Remote GPU Transcription](#remote-gpu-transcription)
11. [Error Handling & Debugging](#error-handling--debugging)

---

## System Overview

The Meeting Recap Processor is a desktop application that transforms audio/video recordings into three sequential outputs:

1. **Transcript** - Complete text transcription of the recording
2. **Analysis** - Structured analysis with key points, decisions, and action items
3. **Recap** - Narrative "Previously on..." style recap in the selected style

The system is designed as a multi-tier architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Desktop UI (Tauri)                   │
│            HTML/CSS/JavaScript Frontend                 │
└──────────────────┬──────────────────────────────────────┘
                   │ JSON over stdin/stdout
                   ▼
┌─────────────────────────────────────────────────────────┐
│            Rust Backend (main.rs)                       │
│    Command Processing & Python Bridge Management        │
└──────────────────┬──────────────────────────────────────┘
                   │ Process spawn with environment setup
                   ▼
┌─────────────────────────────────────────────────────────┐
│         Python Backend (src-python/main.py)             │
│    Orchestration & Processing Command Router            │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┼──────────┬──────────┐
        ▼          ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐
   │Whisper │ │Ollama  │ │Remote  │ │Recap     │
   │Local   │ │LLM     │ │Whisper │ │Generator │
   │GPU     │ │Analysis│ │Server  │ │          │
   └────────┘ └────────┘ └────────┘ └──────────┘
```

---

## Technology Stack

### Frontend
- **Framework**: Tauri (Rust + WebView)
- **UI**: HTML5 + CSS3 + Vanilla JavaScript
- **Build Tool**: Vite (dev server) + Tauri (packaging)
- **File Handling**: Tauri dialog API + HTML5 drag-and-drop
- **Storage**: localStorage for preferences

### Backend (Rust - Tauri)
- **Language**: Rust (Tauri framework)
- **Process Management**: std::process::Command for spawning Python
- **Serialization**: serde_json for command/response handling
- **IPC**: stdin/stdout JSON protocol

### Backend (Python)
- **Language**: Python 3.10+
- **Transcription**: Whisper (OpenAI) with CUDA/GPU acceleration
- **Remote Transcription**: HTTP client for remote Whisper servers
- **Analysis**: Ollama with Gemma3n LLM
- **Web**: requests library for HTTP APIs
- **Paths**: pathlib for cross-platform path handling

### External Services
- **Ollama**: LLM inference engine (runs locally on 192.168.x.x:11434)
- **Remote Whisper**: Optional remote transcription server (HTTP API)
- **FFmpeg**: Audio extraction from video files

### Dependencies
```
Python:
  - openai-whisper >= 20230314
  - torch >= 2.0 (with CUDA 12.1 support)
  - torchvision, torchaudio
  - requests
  - pathlib (stdlib)
  - json (stdlib)
  - subprocess (stdlib)

Rust:
  - serde_json
  - tauri
  - tauri-plugin-dialog
  - tauri-plugin-opener

System:
  - CUDA Toolkit 12.1+
  - cuDNN 9.1+ (for GPU acceleration)
  - FFmpeg (audio extraction)
```

---

## Component Architecture

### 1. Frontend Components (index.html + main.js + styles.css)

#### HTML Structure
```html
Header
  ├─ Application title and description

Main Content Sections
  ├─ File Upload Section
  │   ├─ Drag-and-drop area
  │   └─ File picker button
  │
  ├─ Processing Options Section
  │   ├─ Whisper Model selector
  │   ├─ Transcription Mode selector (Local/Remote)
  │   ├─ Remote Server Configuration (conditional)
  │   │   ├─ Host URL input
  │   │   └─ Test Connection button
  │   ├─ Recap Style selector
  │   └─ Feature toggles (Analysis, Recap generation)
  │
  ├─ Processing Section
  │   ├─ Start Button
  │   ├─ Progress Bar & Stage Display
  │   └─ Results Display (conditional)
  │
Footer
  └─ Attribution
```

#### JavaScript State Management (main.js)
```javascript
Global State
  ├─ selectedFile          // Path to the uploaded file
  ├─ localStorage settings // Persisted user preferences
  │  ├─ transcription_mode (local/remote)
  │  └─ whisper_host (remote server URL)

Event Listeners
  ├─ Upload area
  │   ├─ click          → File dialog
  │   ├─ dragover       → Visual feedback
  │   ├─ dragleave      → Clear visual feedback
  │   └─ drop           → File selection
  │
  ├─ Transcription mode selector
  │   └─ change         → Toggle remote config visibility
  │
  ├─ Start button
  │   └─ click          → Initiate processing pipeline
  │
  ├─ Remote connection test button
  │   └─ click          → Health check of remote server
  │
  └─ Settings recovery   → Restore preferences on load
```

#### CSS Structure
- CSS variables for theming
- Grid layout for responsive design
- Card-based UI components
- Progress bar animation
- Drag-over visual states

### 2. Rust Backend (src-tauri/src/main.rs)

#### Key Functions

**`get_python_executable()`**
- Detects Python 3.12 from virtual environment
- Falls back to system python3 if venv not found
- Path: `~/.venv-py312/bin/python3`

**`get_python_script_path()`**
- Resolves Python script path in development and production
- Checks app bundle Resources (macOS)
- Walks up directory tree to find src-python/main.py
- Critical for both dev and bundled app scenarios

**Tauri Commands**

| Command | Purpose | Input | Output |
|---------|---------|-------|--------|
| `test_python` | Verify Python bridge works | - | Python version string |
| `transcribe_audio` | Start transcription | file_path, model, mode, whisper_host | transcript_file_path |
| `analyze_transcript` | Start analysis | file_path, model | analysis_file_path |
| `generate_recap` | Start recap generation | file_path, style | recap_file_path |
| `check_whisper_health` | Test remote server | whisper_host | {status, models} |

#### Command Processing Flow
```
User clicks "Start Processing"
  │
  ├─ JavaScript prepares options
  │
  ├─ invoke('transcribe_audio', options)
  │   │
  │   ├─ Rust builds JSON command
  │   │   {"command": "transcribe", "file": "...", "model": "...", ...}
  │   │
  │   ├─ Spawns Python process
  │   │   - Sets LD_LIBRARY_PATH for cuDNN
  │   │   - Sets HOME environment variable
  │   │
  │   ├─ Pipes JSON to stdin
  │   │
  │   ├─ Captures stdout/stderr
  │   │
  │   └─ Parses JSON response
  │       {"status": "success", "data": {"transcript_path": "..."}}
  │
  └─ Returns result to JavaScript
```

#### Error Handling
- JSON serialization uses `serde_json::json!()` macro for safe escaping
- Process exit codes checked
- stderr captured and logged for debugging
- Timeout errors propagated to frontend

### 3. Python Backend (src-python/)

#### main.py - Command Router
```python
Main Loop
  │
  ├─ Listen for JSON commands on stdin
  │
  ├─ Parse JSON command
  │
  ├─ Route to handler:
  │   ├─ "transcribe"          → transcribe handler
  │   ├─ "analyze"             → analysis handler
  │   ├─ "recap"               → recap handler
  │   └─ "check_whisper_health" → health check handler
  │
  └─ Send JSON response on stdout
     {"status": "success", "data": {...}}
     or
     {"status": "error", "error": "..."}
```

#### Module Imports
```python
from whisper_processor import WhisperProcessor
from remote_whisper_client import RemoteWhisperClient
from transcript_analyzer import OllamaTranscriptAnalyzer
from recap_generator import DNDRecapGenerator
```

#### Response Format
```python
Success Response:
{
  "status": "success",
  "data": {
    "transcript_path": "/path/to/file",
    "message": "..."
  }
}

Error Response:
{
  "status": "error",
  "error": "Error description"
}

Progress Update (stderr):
{
  "type": "progress",
  "stage": "transcription",
  "progress": 45,
  "message": "..."
}
```

#### Key Processing Modules

**whisper_processor.py**
```python
WhisperProcessor
  ├─ __init__(model_name, device)
  ├─ load_model()              → Load Whisper model to GPU
  ├─ transcribe_file()         → Process audio file
  │   ├─ Extract audio with FFmpeg
  │   ├─ Run Whisper inference
  │   └─ Save transcript to file
  └─ check_system()            → Verify GPU availability
```

**remote_whisper_client.py**
```python
RemoteWhisperClient
  ├─ __init__(whisper_host)
  ├─ check_connection()        → GET /health
  ├─ get_available_models()    → GET /models
  └─ transcribe_and_save()     → POST /transcribe with file
```

**transcript_analyzer.py**
```python
OllamaTranscriptAnalyzer
  ├─ __init__(ollama_host)
  ├─ check_ollama_connection() → GET /api/tags
  ├─ chunk_transcript()        → Split large transcripts
  └─ analyze_transcript()      → Send to Ollama LLM
      ├─ Creates analysis prompt
      ├─ Sends to Ollama API
      └─ Saves analysis to file
```

**recap_generator.py**
```python
DNDRecapGenerator
  ├─ __init__(ollama_host)
  ├─ generate_recap()          → Create narrative recap
  │   ├─ Reads analysis file
  │   ├─ Creates style-specific prompt
  │   ├─ Sends to Ollama API
  │   └─ Returns generated recap
  ├─ save_recap()              → Write recap to file
  └─ _create_recap_prompt()    → Build LLM instruction prompt
```

---

## Data Flow & Processing Pipeline

### Complete Processing Workflow

```
User Action: File Selected → Processing Options Configured → Start Button Clicked
    │
    ▼
┌─────────────────────────────────────────────┐
│ STAGE 1: TRANSCRIPTION                      │
└─────────────────────────────────────────────┘
    │
    ├─ Input:  Audio/Video file path
    ├─ Mode:   Local GPU or Remote GPU
    │
    ├─ Local Mode Flow:
    │   ├─ FFmpeg: Extract audio stream
    │   ├─ Whisper: Load model from CUDA
    │   ├─ Whisper: Inference (GPU-accelerated)
    │   └─ Save:  transcript.txt
    │
    └─ Remote Mode Flow:
        ├─ HTTP: POST /transcribe with file
        ├─ Remote: Model inference on GPU
        └─ Save:  transcript.txt locally
    │
    └─ Output: /path/to/file_model_transcript.txt
    │
    ▼
┌─────────────────────────────────────────────┐
│ STAGE 2: ANALYSIS (Optional)                │
│ Only runs if "Run content analysis" checked │
└─────────────────────────────────────────────┘
    │
    ├─ Input:  transcript.txt
    │
    ├─ Process:
    │   ├─ Chunk transcript if > 25KB
    │   ├─ Create analysis prompt
    │   ├─ Send to Ollama API
    │   │   POST /api/generate
    │   │   Model: gemma3n:latest
    │   ├─ Parse LLM response
    │   └─ Save to file
    │
    └─ Output: /path/to/file_analysis.txt
    │
    ▼
┌─────────────────────────────────────────────┐
│ STAGE 3: RECAP GENERATION (Optional)        │
│ Only runs if "Generate narrative recap"     │
│ AND analysis was run                        │
└─────────────────────────────────────────────┘
    │
    ├─ Input:  analysis.txt
    ├─ Style:  epic | dramatic | narrative | casual
    │
    ├─ Process:
    │   ├─ Read analysis file
    │   ├─ Create style-specific prompt
    │   ├─ Send to Ollama API
    │   │   Model: gemma3n:latest
    │   ├─ Parse LLM response
    │   └─ Save recap to file
    │
    └─ Output: /path/to/file_recap.txt
    │
    ▼
Results displayed to user with file paths
```

### File Naming Convention

```
Input file: meeting.mp4

After Transcription:
  meeting_medium_transcript.txt

After Analysis:
  meeting_medium_analysis.txt

After Recap Generation:
  meeting_medium_recap.txt
```

### Output Directories

Default location (configurable):
```
~/Documents/Meeting Recaps/
├─ transcripts/
│  └─ meeting_medium_transcript.txt
├─ analysis/
│  └─ meeting_medium_analysis.txt
└─ recaps/
   └─ meeting_medium_recap.txt
```

---

## Frontend UI Workflow

### 1. Application Initialization

```javascript
On Page Load:
  ├─ Load Tauri API modules
  ├─ Cache DOM element references
  ├─ Restore user preferences from localStorage
  │   ├─ transcription_mode
  │   └─ whisper_host
  ├─ Show/hide remote config based on mode
  ├─ Attach event listeners to all UI elements
  └─ Set initial button states
```

### 2. File Selection Flow

**Option A: Click Upload Area**
```
User clicks upload area
  ↓
invoke('dialog.open', {
  multiple: false,
  filters: [{ name: 'Media Files', extensions: [...] }]
})
  ↓
User selects file in native file picker
  ↓
handleFileSelect() updates UI:
  ├─ Hide "Drop here" message
  ├─ Show selected filename
  ├─ Enable "Start Processing" button
  └─ Store file path in selectedFile variable
```

**Option B: Drag & Drop**
```
User drags file over upload area
  ↓
uploadArea fires 'dragover' event
  ├─ Add CSS class "drag-over" for visual feedback
  └─ Prevent default browser behavior

User drops file
  ↓
uploadArea fires 'drop' event
  ├─ Prevent default behavior
  ├─ Extract file path from DataTransfer
  └─ handleFileSelect() with file path
```

### 3. Options Configuration

**Whisper Model Selection**
- Available options: tiny, base, small, medium (default), large
- Larger models = higher accuracy but slower processing
- Selection persisted in UI state (not saved to localStorage)

**Transcription Mode Selection**
```javascript
transcriptionModeSelect.addEventListener('change', (e) => {
  const mode = e.target.value;

  if (mode === 'remote') {
    remoteWhisperConfig.style.display = 'block';
    // Load saved host from localStorage
    const savedHost = localStorage.getItem('whisper_host');
    if (savedHost) {
      whisperHostInput.value = savedHost;
    }
  } else {
    remoteWhisperConfig.style.display = 'none';
  }

  // Save preference for next session
  localStorage.setItem('transcription_mode', mode);
});
```

**Remote Server Configuration**
```javascript
testWhisperConnectionBtn.addEventListener('click', async () => {
  const host = whisperHostInput.value;

  try {
    const result = await invoke('check_whisper_health', {
      whisperHost: host
    });

    // Display: ✅ Connected, Models: tiny, base, small, ...
    // Or: ❌ Connection failed

    localStorage.setItem('whisper_host', host);
  } catch (error) {
    // Handle error
  }
});
```

**Recap Style Selection**
- Available styles: epic, dramatic, narrative, casual
- Each style has different AI prompt instructions
- Selection persists in UI state

**Feature Toggles**
```html
<input type="checkbox" id="run-analysis" checked />
  → If unchecked, skip Stage 2 (Analysis)

<input type="checkbox" id="generate-recap" checked />
  → If unchecked, skip Stage 3 (Recap Generation)
  → Automatically skipped if analysis is disabled
```

### 4. Processing Execution Flow

```javascript
startBtn.addEventListener('click', async () => {
  // 1. Validate file is selected
  if (!selectedFile) {
    alert('Please select a file first');
    return;
  }

  // 2. Reset UI
  progressSection.style.display = 'block';
  resultsSection.style.display = 'none';
  startBtn.disabled = true;

  // 3. Gather options
  const options = {
    file: selectedFile,
    whisperModel: whisperModelSelect.value,
    transcriptionMode: transcriptionModeSelect.value,
    whisperHost: whisperHostInput.value || 'http://192.168.68.10:9000',
    recapStyle: recapStyleSelect.value,
    runAnalysis: runAnalysisCheckbox.checked,
    generateRecap: generateRecapCheckbox.checked,
  };

  try {
    // STAGE 1: Transcription
    updateProgress('Transcription', 0, 'Starting transcription...');

    const transcriptResult = await invoke('transcribe_audio', {
      filePath: options.file,
      model: options.whisperModel,
      mode: options.transcriptionMode,
      whisperHost: options.whisperHost,
    });

    addResult(`📝 Transcript: ${transcriptResult}`);
    updateProgress('Transcription', 100, 'Transcription complete!');

    // STAGE 2: Analysis (if enabled)
    if (options.runAnalysis) {
      updateProgress('Analysis', 0, 'Analyzing transcript...');

      const analysisResult = await invoke('analyze_transcript', {
        filePath: transcriptResult,
      });

      addResult(`📊 Analysis: ${analysisResult}`);
      updateProgress('Analysis', 100, 'Analysis complete!');

      // STAGE 3: Recap (if enabled and analysis succeeded)
      if (options.generateRecap) {
        updateProgress('Recap Generation', 0, 'Generating recap...');

        const recapResult = await invoke('generate_recap', {
          filePath: analysisResult,
          style: options.recapStyle,
        });

        addResult(`🎬 Recap: ${recapResult}`);
        updateProgress('Recap Generation', 100, 'Recap complete!');
      }
    }

    // Display results
    resultsSection.style.display = 'block';

  } catch (error) {
    alert(`Error: ${error}`);
  } finally {
    startBtn.disabled = false;
  }
});
```

### 5. Progress Updates

```javascript
// Updates from Tauri commands
function updateProgress(stage, percent, message) {
  currentStageSpan.textContent = stage;
  progressPercentSpan.textContent = `${percent}%`;
  progressFill.style.width = `${percent}%`;
  progressMessage.textContent = message;
}

// Optional: Listen for real-time progress events
listen('progress', (event) => {
  const { stage, progress, message } = event.payload;
  updateProgress(stage, progress, message);
});
```

---

## Tauri Bridge (IPC)

### Communication Protocol

**Format**: JSON over stdin/stdout

**Command Example** (JavaScript → Rust → Python):
```json
{
  "command": "transcribe",
  "file": "/path/to/recording.mp4",
  "model": "medium",
  "mode": "local",
  "whisper_host": "http://192.168.68.10:9000"
}
```

**Response Example** (Python → Rust → JavaScript):
```json
{
  "status": "success",
  "data": {
    "transcript_path": "/Users/user/file_medium_transcript.txt",
    "message": "Transcription completed successfully"
  }
}
```

**Error Response**:
```json
{
  "status": "error",
  "error": "Cannot connect to Whisper server at http://..."
}
```

### Rust Command Handler Pattern

```rust
#[tauri::command]
async fn transcribe_audio(
  file_path: String,      // Required
  model: String,          // Required
  mode: Option<String>,   // Optional, default: "local"
  whisper_host: Option<String>  // Optional, default: "http://192.168.68.10:9000"
) -> Result<String, String> {

  // 1. Build Python script path
  let python_script = get_python_script_path();

  // 2. Create command JSON with safe escaping
  let command = serde_json::json!({
    "command": "transcribe",
    "file": file_path,
    "model": model,
    "mode": mode.unwrap_or_else(|| "local".to_string()),
    "whisper_host": whisper_host.unwrap_or_else(|| "http://192.168.68.10:9000".to_string())
  });

  // 3. Spawn Python process
  let mut child = Command::new(get_python_executable())
    .arg(python_script)
    .stdin(Stdio::piped())
    .stdout(Stdio::piped())
    .stderr(Stdio::piped())
    .env("LD_LIBRARY_PATH", format!("{}/cudnn/lib", home))
    .spawn()?;

  // 4. Send command to stdin
  if let Some(mut stdin) = child.stdin.take() {
    stdin.write_all(command.to_string().as_bytes())?;
    stdin.write_all(b"\n")?;
  }

  // 5. Capture and parse output
  let output = child.wait_with_output()?;
  let stdout = String::from_utf8_lossy(&output.stdout);

  // 6. Parse JSON response
  if output.status.success() {
    if let Some(line) = stdout.lines().last() {
      if let Ok(json) = serde_json::from_str::<serde_json::Value>(line) {
        if json["status"] == "success" {
          if let Some(path) = json["data"]["transcript_path"].as_str() {
            return Ok(path.to_string());
          }
        }
      }
    }
  }

  Err("Processing failed".to_string())
}
```

### Environment Variables

The Rust backend sets up critical environment variables before spawning Python:

```rust
.env("LD_LIBRARY_PATH", format!("{}/cudnn/lib", home))
```

This ensures that CUDA libraries are found when Python loads torch.

---

## Python Backend Processing

### Transcription Handler

```python
def handle_transcribe(command):
    file_path = command.get("file")
    model = command.get("model", "medium")
    mode = command.get("mode", "local")
    whisper_host = command.get("whisper_host")

    # Generate output path
    input_path = Path(file_path)
    output_path = input_path.parent / f"{input_path.stem}_{model}_transcript.txt"

    if mode == "remote":
        # Use remote server
        from remote_whisper_client import RemoteWhisperClient

        send_progress("transcription", 0, "Connecting to remote server...")
        client = RemoteWhisperClient(whisper_host=whisper_host)

        if not client.check_connection():
            send_response("error", error="Cannot connect to remote server")
            return

        send_progress("transcription", 15, "Sending to remote server...")
        result = client.transcribe_and_save(
          str(file_path),
          str(output_path),
          model=model,
          language="en"
        )
    else:
        # Use local Whisper
        from whisper_processor import WhisperProcessor

        send_progress("transcription", 0, "Initializing...")
        processor = WhisperProcessor(model_name=model)

        send_progress("transcription", 15, "Loading model...")
        processor.load_model()

        send_progress("transcription", 30, "Transcribing...")
        result = processor.transcribe_file(str(file_path), str(output_path))

    if result:
        send_progress("transcription", 100, "Complete!")
        send_response("success", data={
            "transcript_path": str(output_path),
            "message": "Transcription completed successfully"
        })
    else:
        send_response("error", error="Transcription failed")
```

### Analysis Handler

```python
def handle_analyze(command):
    from transcript_analyzer import OllamaTranscriptAnalyzer

    file_path = command.get("file")
    model = command.get("model", "gemma3n:latest")

    # Generate output path
    input_path = Path(file_path)
    base_name = input_path.stem.replace('_transcript', '', 1)
    output_path = input_path.parent / f"{base_name}_analysis.txt"

    send_progress("analysis", 0, "Initializing analyzer...")
    analyzer = OllamaTranscriptAnalyzer()

    send_progress("analysis", 30, "Analyzing transcript...")
    result = analyzer.analyze_transcript(
      str(file_path),
      model=model,
      output_path=str(output_path)
    )

    if result:
        send_progress("analysis", 100, "Complete!")
        send_response("success", data={
            "analysis_path": str(result),
            "message": "Analysis completed successfully"
        })
    else:
        send_response("error", error="Analysis failed")
```

### Recap Generation Handler

```python
def handle_recap(command):
    from recap_generator import DNDRecapGenerator

    file_path = command.get("file")
    style = command.get("style", "epic")
    model = command.get("model", "gemma3n:latest")

    # Generate output path
    input_path = Path(file_path)
    base_name = input_path.stem.replace('_analysis', '', 1)
    output_path = input_path.parent / f"{base_name}_recap.txt"

    send_progress("recap", 0, "Initializing generator...")
    generator = DNDRecapGenerator()

    send_progress("recap", 30, f"Generating {style} style recap...")
    result = generator.generate_recap(
      str(file_path),
      model=model,
      style=style,
      output_path=str(output_path)
    )

    if result:
        send_progress("recap", 100, "Complete!")
        send_response("success", data={
            "recap_path": str(result),
            "message": "Recap generated successfully"
        })
    else:
        send_response("error", error="Recap generation failed")
```

---

## AI Prompt Instructions by Style

### Overview

The recap generation prompt is style-aware. The same analysis content is transformed into different narrative styles through custom LLM instructions. The base prompt is defined in `recap_generator.py` method `_create_recap_prompt()`.

### Style Instruction Templates

#### 1. **EPIC** (Default)

**Instructions to AI Model**:
```
Create an epic, grand-scale recap in the style of a fantasy novel opening.
- Use rich, descriptive language
- Emphasize the stakes and scale of events
- Heroic and legendary tone
- Build anticipation for what's to come
```

**Characteristics**:
- Grandiose, fantasy-novel opening
- Emphasis on stakes and scale
- Heroic tone
- Rich descriptive language
- Builds anticipation
- TTS-optimized with natural pacing

**Example Output**:
```
Previously on [Campaign]...

In the halls of power, where kingdoms rise and fall like waves upon
the shore, a gathering of heroes found themselves entangled in
machinations of destiny itself. The shadows deepened as ancient
powers stirred, and the very fabric of reality trembled with
foreboding...
```

---

#### 2. **DRAMATIC**

**Instructions to AI Model**:
```
Create a dramatic, engaging recap in the style of a TV show's "Previously on..." segment.
- Use present tense for immediacy
- Build tension and drama
- Focus on cliffhangers and key moments
- Use vivid, cinematic language
```

**Characteristics**:
- Present tense for immediacy
- TV show "Previously on..." style
- Emphasis on tension and cliffhangers
- Cinematic, vivid language
- Fast-paced
- Builds to dramatic conclusion

**Example Output**:
```
Previously...

Tensions rise as the group discovers a crucial betrayal from
within their trusted circle. The stakes have never been higher.
They race against time to prevent a catastrophic event.
In a shocking turn of events, an ancient enemy resurfaces,
and the final confrontation awaits...
```

---

#### 3. **NARRATIVE**

**Instructions to AI Model**:
```
Create a storytelling-focused recap as if a narrator is recounting the tale.
- Use past tense
- Focus on character development and story progression
- Maintain an epic fantasy tone
- Emphasize emotional beats
```

**Characteristics**:
- Past tense (traditional storytelling)
- Character development focus
- Story progression emphasized
- Emotional beats highlighted
- Epic fantasy tone
- Chronological narrative flow

**Example Output**:
```
Previously on [Campaign]...

The heroes had assembled for a great purpose. Over the course of
their journey, bonds were forged and tested. They discovered that
one among them carried a dark secret. Through trials and tribulations,
they grew stronger, but at great cost. Now, as the next chapter
unfolds, their true purpose finally revealed itself...
```

---

#### 4. **CASUAL**

**Instructions to AI Model**:
```
Create a brief, punchy recap hitting only the most essential story beats.
- Keep it under 200 words
- Focus on major plot developments
- Clear and straightforward language
```

**Characteristics**:
- Concise (< 200 words)
- Essential plot beats only
- Clear, straightforward language
- Punchy tone
- Minimal embellishment
- Quick reference format

**Example Output**:
```
Previously...

The team discovered they've been working against a hidden enemy.
One member made a critical discovery about the artifact they were
seeking. They lost an ally but gained unexpected help. Now they're
heading toward a final confrontation with higher stakes than before.
```

---

### Complete Prompt Template

All styles use the following base prompt structure:

```python
prompt = f"""You are creating a "Previously on..." recap for a Dungeons & Dragons campaign session. This will be read aloud by a text-to-speech AI voice.

STYLE: {style_guide}

CRITICAL REQUIREMENTS:
1. **Story Only** - Focus ONLY on narrative events, character moments, and plot developments
2. **Ignore Mechanics** - Do NOT mention: dice rolls, skill checks, ability scores, combat mechanics, game rules
3. **TTS Optimized**:
   - Use short to medium sentences
   - Avoid complex punctuation
   - Write numbers as words (three, not 3)
   - Use clear pacing with periods for pauses
   - Include natural breaks between major beats
4. **Character Focus** - Emphasize what the characters did, felt, discovered, and experienced
5. **Narrative Flow** - Tell the story in chronological order with smooth transitions

FORMAT:
Start with "Previously on [Campaign Name if mentioned]..." or just "Previously..."
Then deliver the recap in 3-5 paragraphs
End with a cliffhanger or hook for the next session

LENGTH: Aim for 250-400 words (about 90-150 seconds when read aloud)

Here is the session analysis to work from:

{analysis_content}

Now create the "Previously on..." recap following all requirements above:"""
```

### Key Prompt Constraints

1. **Story-Only Focus**: Excludes game mechanics like dice rolls, ability checks, character stats
2. **TTS Optimization**:
   - Short to medium sentences for natural speech
   - Avoids complex punctuation
   - Numbers spelled out (three vs 3)
   - Periods create natural pauses
3. **Length Target**: 250-400 words ≈ 90-150 seconds of speech
4. **Narrative Structure**:
   - Opens with "Previously on..."
   - 3-5 story paragraphs
   - Closes with cliffhanger/hook
5. **Character Emphasis**: Focuses on what characters did, felt, discovered

### Model Configuration

```python
payload = {
    "model": "gemma3n:latest",
    "prompt": recap_prompt,
    "stream": False,
    "options": {
        "temperature": 0.7,    # Balanced creativity
        "top_p": 0.9,          # Reasonable sampling diversity
        "num_ctx": 32768,      # Large context window
        "num_predict": 2048,   # Sufficient output length
    }
}
```

**Model Settings Rationale**:
- **temperature 0.7**: Higher than default (0.5) for more creative storytelling, but not too high to lose coherence
- **top_p 0.9**: Allows diverse vocabulary while maintaining quality
- **num_ctx 32768**: Large analysis files require adequate context window
- **num_predict 2048**: Allows full recap generation (250-400 words)

---

## Configuration & Settings

### Configuration File (config/defaults.json)

```json
{
  "whisper": {
    "mode": "local",                          // or "remote"
    "model": "medium",                        // tiny, base, small, medium, large
    "device": "cuda",                         // cuda or cpu
    "language": "en",
    "remoteHost": "http://192.168.68.10:9000"
  },
  "ollama": {
    "host": "http://192.168.68.10:11434",
    "model": "gemma3n:latest"
  },
  "recap": {
    "defaultStyle": "epic",
    "styles": ["epic", "casual", "dramatic", "narrative"]
  },
  "output": {
    "baseDir": "~/Documents/Meeting Recaps",
    "transcriptsDir": "transcripts",
    "analysisDir": "analysis",
    "recapsDir": "recaps"
  },
  "files": {
    "maxSizeMB": 1024,
    "supportedAudioFormats": [".mp3", ".wav", ".m4a", ".flac", ".ogg"],
    "supportedVideoFormats": [".mp4", ".mkv", ".avi", ".mov", ".webm"]
  },
  "obsidian": {
    "enabled": false,
    "apiUrl": "http://localhost:27123",
    "vaultPath": "",
    "apiToken": ""
  }
}
```

### Runtime Settings (localStorage)

User preferences persisted in browser localStorage:

```javascript
// Transcription Settings
localStorage.setItem('transcription_mode', 'local' | 'remote');
localStorage.setItem('whisper_host', 'http://192.168.68.10:9000');

// Recap Style
// (Not persisted, uses dropdown default)

// Whisper Model
// (Not persisted, uses dropdown selection)
```

### Environment Variables (Tauri)

Set by Rust backend before spawning Python:

```rust
.env("LD_LIBRARY_PATH", format!("{}/cudnn/lib", home))
  // Tells Python where to find cuDNN libraries for CUDA
  // Required for torch GPU acceleration
```

### Python Path Configuration

```rust
// Virtual environment path (checked first)
~/.venv-py312/bin/python3

// Fallback
python3  // Uses system PATH
```

### Network Configuration

```
Ollama Server
  │
  └─ Address: 192.168.68.10:11434
     Models: gemma3n:latest, llama3:latest, etc.

Remote Whisper Server (Optional)
  │
  └─ Default: http://192.168.68.10:9000
     Endpoints:
       - GET /health       → Check server status
       - GET /models       → List available models
       - POST /transcribe  → Send audio file
```

---

## Remote GPU Transcription

### Architecture

The app supports offloading transcription to a remote machine with a more powerful GPU via HTTP API.

```
macOS App                           Windows Machine (RTX 5090)
    │                                     │
    ├─ Tauri Frontend                    │
    ├─ Rust Backend                      │
    └─ Python Backend                    │
        │                                │
        └─ RemoteWhisperClient ─────────────► FastAPI Server
            HTTP POST /transcribe       │     (faster-whisper)
                                        │
                                        ├─ Model Loading
                                        ├─ CUDA Inference
                                        └─ Transcription
```

### RemoteWhisperClient Implementation

```python
class RemoteWhisperClient:
    def __init__(self, whisper_host="http://192.168.68.10:9000"):
        self.whisper_host = whisper_host
        self.timeout = 600  # 10 minutes

    def check_connection(self) -> bool:
        """Test if server is reachable"""
        try:
            response = requests.get(
                f"{self.whisper_host}/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

    def get_available_models(self) -> list:
        """Get list of available models on server"""
        try:
            response = requests.get(
                f"{self.whisper_host}/models",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('models', [])
            return []
        except:
            return []

    def transcribe_and_save(self, file_path, output_path, model="medium", language="en"):
        """Send file to remote server and save result"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'model': model, 'language': language}

            response = requests.post(
                f"{self.whisper_host}/transcribe",
                files=files,
                data=data,
                timeout=self.timeout
            )

        if response.status_code == 200:
            result = response.json()
            text = result.get('text', '')

            with open(output_path, 'w') as f:
                f.write(text)

            return output_path

        return None
```

### Remote Server Setup

**Required Software on Remote Machine**:
- Python 3.10+ with faster-whisper
- CUDA Toolkit 12.1+
- cuDNN 9.1+
- FastAPI + uvicorn

**DIY Server Implementation** (`whisper_server.py`):
```python
from fastapi import FastAPI
from faster_whisper import WhisperModel
import torch

app = FastAPI()
current_model = {"model": None, "name": None}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/models")
def get_models():
    return {
        "models": ["tiny", "base", "small", "medium", "large"]
    }

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...), model: str = Form("medium")):
    # Load model if different from current
    if model != current_model["name"]:
        current_model["model"] = WhisperModel(
            model,
            device="cuda",
            compute_type="float16"
        )
        current_model["name"] = model

    # Save uploaded file
    with open(f"/tmp/{file.filename}", "wb") as f:
        f.write(await file.read())

    # Transcribe
    segments, info = current_model["model"].transcribe(f"/tmp/{file.filename}")

    text = " ".join(segment.text for segment in segments)

    return {"text": text}
```

### UI Flow for Remote Mode

```javascript
// User selects "Remote GPU" from dropdown
transcriptionModeSelect.value = "remote";

// Remote configuration section appears
remoteWhisperConfig.style.display = 'block';

// User enters remote server URL
whisperHostInput.value = "http://192.168.x.x:5000";

// User clicks "Test Connection"
// → Rust calls check_whisper_health
// → Python creates RemoteWhisperClient
// → HTTP GET /health
// → HTTP GET /models
// → Display: ✅ Connected, Models: tiny, base, small, medium, large

// User clicks "Start Processing"
// → Rust sends transcribe_audio command with mode="remote"
// → Python creates RemoteWhisperClient
// → HTTP POST /transcribe with file
// → Saves result locally
```

### Error Handling for Remote

```python
if mode == "remote":
    client = RemoteWhisperClient(whisper_host=whisper_host)

    if not client.check_connection():
        error_msg = f"Cannot connect to remote Whisper server at {whisper_host}"
        send_response("error", error=error_msg)
        return

    try:
        result = client.transcribe_and_save(file_path, output_path, model=model)
    except requests.Timeout:
        send_response("error", error="Remote transcription timed out")
    except requests.ConnectionError:
        send_response("error", error="Lost connection to remote server")
    except Exception as e:
        send_response("error", error=f"Remote transcription failed: {str(e)}")
```

---

## Error Handling & Debugging

### Error Sources & Handling

#### 1. File Not Found / Inaccessible
```
Frontend:
  User selects file that doesn't exist or is unreadable

Rust:
  File passed to Python command

Python:
  os.path.exists() check fails
  → send_response("error", error="File not found: ...")

Frontend:
  Display error in alert
```

#### 2. GPU Not Available
```
Python (WhisperProcessor):
  torch.cuda.is_available() returns False

Options:
  a) Fall back to CPU (slow)
  b) Require GPU for local mode
  c) Auto-switch to remote mode (if available)

Current behavior: Attempt CPU fallback with warning
```

#### 3. Ollama Not Running
```
Python (OllamaTranscriptAnalyzer):
  requests.get(f"{ollama_host}/api/tags") times out
  → send_response("error", error="Ollama not running")

Solution: Start Ollama service and retry
  ollama serve
```

#### 4. Remote Server Unreachable
```
Python (RemoteWhisperClient):
  requests.get(f"{server}/health") fails

Error propagated through:
  check_whisper_health() → UI shows ❌ Connection failed

During transcription:
  client.check_connection() returns False
  → send_response("error", error="Cannot connect to remote server")
```

#### 5. JSON Serialization Errors
```
Rust:
  Uses serde_json::json!() macro for safe escaping
  Prevents "Unterminated string" errors in file paths

Python:
  json.loads() catches malformed JSON
  → send_response("error", error="Invalid JSON")
```

#### 6. Python Module Import Errors
```
Python (main.py):
  from whisper_processor import WhisperProcessor  # ImportError

sys.path includes:
  - PROJECT_ROOT / "python scripts"
  - Current directory
  - Standard library paths

Debug: Print sys.path at startup
```

### Debug Output

#### Rust Console Output
```
When running `npm run tauri:dev`, see:

=== PYTHON STDERR ===
[Python error messages, debug output]
=== END STDERR ===

=== PYTHON STDOUT ===
[JSON response, progress updates]
=== END STDOUT ===
```

#### Python Debug Logging
```python
# Send to stderr for visibility
print(f"DEBUG: {message}", file=sys.stderr, flush=True)

# Progress updates during long operations
send_progress("stage", 45, "Processing chunk 3 of 5...")

# Exception tracing
import traceback
traceback.print_exc(file=sys.stderr)
```

#### Frontend Console (DevTools)
```javascript
// Right-click in app → Inspect to open DevTools
// Console tab shows:

console.log('main.js loading...');
console.log('Dialog API loaded successfully');
console.log('Tauri API available:', true);

// Error logs
console.error('Error loading dialog API:', error);
```

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Python not found" | Venv missing | Install Python 3.12 or create venv |
| "CUDA not available" | GPU drivers missing | Install NVIDIA drivers + CUDA 12.1 |
| "Cannot load cuDNN" | cuDNN not in LD_LIBRARY_PATH | Download cuDNN, add to ~/.bashrc |
| "FFmpeg not found" | System dependency missing | `brew install ffmpeg` |
| "Ollama not running" | Service not started | Run `ollama serve` |
| "Model not found" | Whisper model not downloaded | First run auto-downloads model |
| "Remote connection failed" | Server unreachable | Check IP, port, firewall, WSL port forwarding |
| "JSON parse error" | Malformed path in command | Use serde_json::json!() macro in Rust |

### Enable Verbose Logging

```rust
// In main.rs, uncomment or add:
eprintln!("=== SECTION START ===");
eprintln!("Value: {:?}", variable);
eprintln!("=== SECTION END ===");
```

```python
# In Python, add:
print(f">>> Debug point: {value}", file=sys.stderr, flush=True)
```

```javascript
// In main.js:
console.log('Checkpoint:', variable);
console.error('Error state:', error);
```

---

## Summary

The Meeting Recap Processor is a sophisticated multi-layer application that combines:

1. **Frontend** - Intuitive Tauri-based UI for file selection and options
2. **IPC Bridge** - Efficient JSON-over-stdin/stdout communication
3. **Processing Pipeline** - Three sequential stages (transcription, analysis, recap)
4. **AI Integration** - Ollama LLM with style-specific prompts for recap generation
5. **GPU Support** - Local CUDA acceleration or remote GPU via HTTP
6. **Error Resilience** - Comprehensive error handling and debugging capabilities

The architecture prioritizes **modularity**, **clarity**, and **extensibility**, making it straightforward to add new features, styles, or processing stages in the future.

