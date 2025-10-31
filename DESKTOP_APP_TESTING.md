# Desktop Application Testing Guide

## Current Status

✅ **Vite Dev Server**: Running on http://localhost:5173/
✅ **API Server**: Running on http://127.0.0.1:8765
✅ **Python Backend**: Tested and functional
⏳ **Tauri Desktop App**: Ready to launch

---

## Starting the Desktop Application

The Vite frontend server is already running in the background. Now you need to start the Tauri desktop application.

### In a New Terminal Window:

```bash
cd /Users/michaellombard/ai-projects/meetings-app
npm run tauri:dev
```

Or if that doesn't work:
```bash
source ~/.cargo/env && tauri dev
```

This will:
1. Compile the Rust backend
2. Open the desktop application window
3. Load the UI from the Vite server (http://localhost:5173)

**Note**: The first build may take a few minutes. Subsequent launches will be much faster.

---

## Testing Checklist

### 1. Test Python Connection ✓

**Location**: Scroll to bottom of the app window

**Steps**:
1. Find the "Debug: Test Python Bridge" section
2. Click the "Test Python Connection" button
3. You should see: "Python bridge is working! Python 3.9.6"

**What this tests**: Communication between Rust (Tauri) and Python backend

---

### 2. Test File Upload

**Location**: Top section "1. Select Recording"

**Steps**:
1. Click the upload area or drag-and-drop a file
2. Supported formats: MP4, MP3, WAV, M4A, MKV
3. File name should appear with an × remove button
4. "Start Processing" button should become enabled

**Test files you can use**:
- Any audio/video file in your Downloads folder
- Create a test file: `ffmpeg -f lavfi -i sine=frequency=1000:duration=5 test.mp3`

**What this tests**: File selection and UI state management

---

### 3. Test Processing Options

**Location**: Section "2. Processing Options"

**Available Settings**:
- **Whisper Model**: Choose processing speed vs accuracy
  - Tiny: Fastest, lowest accuracy
  - Small: Good for testing
  - Medium: Recommended (default)
  - Large: Best accuracy, slowest

- **Recap Style**: Choose narrative tone
  - Epic: Dramatic storytelling (default)
  - Casual: Conversational tone
  - Dramatic: Intense narration
  - Narrative: Story-focused

- **Checkboxes**:
  - Run content analysis (via Ollama)
  - Generate narrative recap (D&D style)

**What this tests**: Configuration UI elements

---

### 4. Test Preset Management

**Location**: Section "5. Preset Management"

**Steps**:
1. Configure your preferred settings above
2. Enter a preset name (e.g., "Quick Test")
3. Click "Save Preset"
4. Preset should appear in the dropdown
5. Change settings to something different
6. Select your preset from the dropdown
7. Settings should restore to saved values
8. Click "Delete Preset" to remove it

**What this tests**: PresetManager Python module and Tauri commands

---

### 5. Test Full Processing Pipeline

**Prerequisites**:
- Small audio/video file (< 100MB for testing)
- CUDA GPU available (or be patient with CPU)
- Ollama running on http://192.168.68.10:11434 (if using analysis/recap)

**Steps**:
1. Select a file
2. Choose "Small" or "Tiny" Whisper model for faster testing
3. **Uncheck** "Run content analysis" and "Generate narrative recap" for first test
4. Click "Start Processing"
5. Watch the progress bar and status messages:
   - "Initializing Whisper processor..."
   - "Transcribing [filename]..."
   - Progress: 0% → 100%
6. Results should appear showing transcript path

**Expected Results**:
- Transcript file created in same directory as input file
- Format: `[original_name]_transcript_[timestamp].txt`
- File should contain readable transcription

**What this tests**: End-to-end transcription pipeline

---

### 6. Test with Analysis and Recap

**Prerequisites**:
- Completed transcription from step 5
- Ollama running: `ollama serve`
- Model installed: `ollama pull gemma3n:latest`

**Steps**:
1. Select another file (or the same one)
2. Keep "Medium" Whisper model
3. **Check** both "Run content analysis" and "Generate narrative recap"
4. Click "Start Processing"
5. Watch for multiple stages:
   - Stage 1: Transcription
   - Stage 2: Analysis
   - Stage 3: Recap Generation
6. Results should show paths to all three output files

**Expected Output Files**:
- `[name]_transcript_[timestamp].txt` - Raw transcription
- `[name]_analysis_[timestamp].txt` - Structured analysis
- `[name]_recap_[timestamp].txt` - Narrative recap

**What this tests**: Complete workflow integration

---

### 7. Test Obsidian Integration (Optional)

**Prerequisites**:
- Obsidian installed with Local REST API plugin
- Plugin enabled (Settings → Community plugins → Local REST API)
- API token generated (Plugin settings → Copy token)

**Steps**:
1. Scroll to "4. Obsidian Integration"
2. Paste your API token
3. Select a vault from the dropdown
4. Process a file (follow step 5 or 6)
5. After completion, a note should be created in your vault

**Expected Result**:
- New note in Obsidian with YAML frontmatter
- Contains transcript, analysis, or recap content
- Format: `Meeting Recap - [date] - [timestamp].md`

**What this tests**: Obsidian API client integration

---

## Common Issues and Solutions

### Issue: "Python error: ModuleNotFoundError"

**Solution**:
```bash
pip3 install torch whisper requests
# For CUDA support:
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

---

### Issue: "Ollama connection refused"

**Solution**:
```bash
# Start Ollama service
ollama serve

# In another terminal, verify it's running:
curl http://192.168.68.10:11434/api/tags

# Pull the model if not already installed:
ollama pull gemma3n:latest
```

---

### Issue: "CUDA not available" or very slow processing

**Check**:
```bash
# Verify GPU is available
nvidia-smi

# Check PyTorch can see GPU
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

**Solution**:
- If no GPU, processing will use CPU (much slower)
- Use "tiny" or "small" Whisper models for CPU
- Consider cloud GPU or reducing file length

---

### Issue: Tauri window is blank

**Solution**:
1. Check Vite is running: `curl http://localhost:5173`
2. Restart Vite: `lsof -ti:5173 | xargs kill; npx vite &`
3. Restart Tauri: `npm run tauri:dev`
4. Check browser console in Tauri (right-click → Inspect)

---

### Issue: "cargo: command not found"

**Solution**:
```bash
# Install Rust if not installed:
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Source cargo environment:
source ~/.cargo/env

# Then try again:
npm run tauri:dev
```

---

## Inspecting the Application

### Open DevTools (Chrome-style)

**Mac**: Right-click in the app window → "Inspect"
**Windows/Linux**: Right-click → "Inspect Element"

This opens Chrome DevTools where you can:
- View console logs
- Inspect network requests
- Debug JavaScript errors
- Monitor Tauri command calls

### View Rust Backend Logs

All Rust/Tauri logs appear in the terminal where you ran `npm run tauri:dev`. Look for:
- Python command execution
- File path validation
- Errors from Tauri commands

### View Python Logs

Python stderr/stdout will appear in the Tauri terminal output. Add debug prints in `src-python/main.py` if needed:
```python
print(f"DEBUG: Processing {file_path}", file=sys.stderr, flush=True)
```

---

## Performance Notes

### Transcription Speed (Medium model on RTX 5090)

- 1 min audio → ~10-15 seconds
- 10 min audio → ~1-2 minutes
- 60 min audio → ~8-12 minutes

### Analysis Speed (Gemma3n on remote server)

- Short transcript (< 1k words) → 10-20 seconds
- Medium transcript (1k-5k words) → 30-60 seconds
- Long transcript (> 5k words) → 1-3 minutes

### Recap Generation Speed

- Similar to analysis (depends on transcript length)
- Typically 20-60 seconds per recap

---

## Next Steps After Testing

1. **Customize Styling**: Edit `styles.css` for UI appearance
2. **Add Features**: Implement additional Tauri commands in `src-tauri/src/main.rs`
3. **Configure Presets**: Create presets for different meeting types
4. **Integrate Tools**: Use the REST API to connect external tools
5. **Build Production**: `npm run tauri:build` to create installer

---

## Build for Distribution

When ready to create a production build:

```bash
# Build optimized binary
npm run tauri:build

# Output location:
# Mac: src-tauri/target/release/bundle/dmg/
# Windows: src-tauri/target/release/bundle/msi/
# Linux: src-tauri/target/release/bundle/appimage/
```

The installer will include:
- Compiled Rust backend
- Bundled frontend assets
- Python integration (requires Python installed on target system)

---

## Stopping the Servers

When you're done testing:

```bash
# Stop Vite dev server
lsof -ti:5173 | xargs kill

# Stop API server
lsof -ti:8765 | xargs kill

# Stop Tauri
# Just close the application window or press Ctrl+C in the terminal
```

---

## Questions?

- **File issues**: https://github.com/anthropics/claude-code/issues
- **Tauri docs**: https://tauri.app/v2/guide/
- **Project docs**: See CLAUDE.md for architecture details
- **API docs**: See API_EXAMPLES.md for REST API usage
