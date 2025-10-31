# Transcription Setup Instructions

## FFmpeg Installation

FFmpeg is required for audio processing in the transcription workflow. Here's how to properly install it in your project:

1. Download FFmpeg to your project directory:
```bash
# Create bin directory in your project
mkdir -p ~/bin

# Download FFmpeg directly to project bin directory
curl -L https://evermeet.cx/ffmpeg/ffmpeg-7.1.zip -o ~/bin/ffmpeg.zip
cd ~/bin 
unzip ffmpeg.zip
chmod +x ffmpeg
```

2. Add the bin directory to your PATH:
```bash
export PATH="$HOME/bin:$PATH"
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
# or for zsh users
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
```

3. Verify installation:
```bash
ffmpeg -version
```

## Ollama Integration

The app connects to an Ollama service at 192.168.68.10 which you confirmed is already running with the correct models installed.

## Running the App

After installing FFmpeg, you should be able to run the transcription in your app. If you encounter issues with the Python script path in the Tauri app, check:

1. That the Python script path in `src-tauri/src/main.rs` is correct
2. That Python dependencies (torch, whisper) are properly installed in your environment
3. That the Python path is set correctly within the Tauri app context

## Debugging the Tauri App

If issues persist:

1. Run with verbose output:
```bash
npm run tauri:dev -- --verbose
```

2. Add logging to your Python code to see exactly which step is failing (I already updated the Python files with additional debug output)

3. Try running the transcription manually:
```bash
python src-python/whisper_processor.py --check
```