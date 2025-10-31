## Transcription Issue Debugging Guide

Based on the code analysis, here are potential issues and debugging steps for the transcription part of the app:

### 1. Python Dependencies Missing
The Whisper and Torch dependencies might not be installed in the system where the app is running.

Check installation:
```bash
# In the project directory, verify Python dependencies exist
python -c "import torch; import whisper; print('Dependencies OK')"
```

Install required packages:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install openai-whisper
```

### 2. FFmpeg Missing or Not Installed
FFmpeg is required for audio processing. Check if it's working:
```bash
ffmpeg -version
```

If missing, install:
- Windows: `winget install FFmpeg`
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

### 3. Ollama Service Not Running
For the analysis part, Ollama must be running:
```bash
# Check if Ollama is running:
ollama list

# If not, start it:
ollama serve
```

### 4. Model Availability
Check if the required models are installed:
```bash
ollama list

# Install required models if missing:
ollama pull gemma3n:latest
ollama pull llama3:latest
ollama pull llama3.2:3b
```

### 5. GPU/CUDA Issues
If the system has an RTX 5090, make sure CUDA is working:
```bash
# Check CUDA availability:
python -c "import torch; print(torch.cuda.is_available())"

# If CUDA is missing, install appropriate drivers.
```

### 6. File Handling Issues
The transcription process might fail due to incorrect file paths or permissions. Try:
```bash
# Debug file path issues by modifying whisper_processor.py:
# Add the following lines to your transcription file:
print(f"DEBUG: Processing file path: {file_path}")
print(f"DEBUG: File exists: {os.path.exists(file_path)}")
print(f"DEBUG: File size: {os.path.getsize(file_path) if os.path.exists(file_path) else 'N/A'}")
```

### 7. Progress Tracking In Tauri
Check that the Tauri app is correctly sending messages to Python. You can:
- Run the app with debug output: `npm run tauri:dev -- --verbose`
- Monitor progress updates in the UI
- Check if you can manually call the Python functions via command line

### 8. Direct Testing
Try running the transcription script independently:
```bash
python src-python/whisper_processor.py --check
python src-python/whisper_processor.py <path-to-media-file>
```

### 9. Error Checking
Add these debugging lines to your Python code in whisper_processor.py around line 182:
```python
print(f"DEBUG: transcribe - audio_path: {audio_path}", file=sys.stderr, flush=True)
print(f"DEBUG: File exists: {os.path.exists(audio_path)}", file=sys.stderr, flush=True)
if audio_path.exists():
    print(f"DEBUG: File size: {audio_path.stat().st_size}", file=sys.stderr, flush=True)
```

The transcription process starts with the Tauri desktop app frontend (index.html), which sends commands to Python through `main.py`, which then calls `whisper_processor.py` for transcription and `transcript_analyzer.py` for analysis.

The most likely issues are:
1. Missing/incorrect Python dependencies
2. Missing FFmpeg
3. Ollama service not running or models not installed
4. File access permissions