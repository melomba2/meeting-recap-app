# Meeting Recap Processor - Architecture & Workflow Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Technology Stack](#technology-stack)
3. [Component Architecture](#component-architecture)
4. [Data Flow & Processing Pipeline](#data-flow--processing-pipeline)
5. [Remote GPU Transcription](#remote-gpu-transcription)
6. [Summary](#summary)


---

## System Overview

The Meeting Recap Processor is a desktop application that transforms audio/video recordings into three sequential outputs:

1. **Transcript** - Complete text transcription of the recording
2. **Analysis** - Structured analysis with key points, decisions, and action items
3. **Recap** - Narrative recap in the selected style

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

### Frontend UI Workflow

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
prompt = f"""You are creating a "Previously on..." recap for a Dungeons & Dragons campaign session. This could be read aloud by a text-to-speech AI voice.

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


### Network Configuration

```
Ollama Server
  │
  └─ Address: 192.168.x.x:11434
     Models: gemma3n:latest, llama3:latest, etc.

Remote Whisper Server (Optional)
  │
  └─ Default: http://192.168.x.x:5000
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
    │                                    │
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

## Summary

The Meeting Recap Processor is a sophisticated multi-layer application that combines:

1. **Frontend** - Intuitive Tauri-based UI for file selection and options
2. **IPC Bridge** - Efficient JSON-over-stdin/stdout communication
3. **Processing Pipeline** - Three sequential stages (transcription, analysis, recap)
4. **AI Integration** - Ollama LLM with style-specific prompts for recap generation
5. **GPU Support** - Local CUDA acceleration or remote GPU via HTTP
6. **Error Resilience** - Comprehensive error handling and debugging capabilities

The architecture prioritizes **modularity**, **clarity**, and **extensibility**, making it straightforward to add new features, styles, or processing stages in the future.

