# Getting Started with Meeting Recap App

Welcome! This guide will help you get the Meeting Recap App up and running in about **10-15 minutes**.

## What is Meeting Recap App?

It's a desktop application that automatically:
1. 🎙️ **Transcribes** your meeting or gaming session recordings into text
2. 📊 **Analyzes** the content to extract key points and decisions
3. 📖 **Generates** narrative-style recaps (perfect for D&D sessions!)

Everything runs locally on your computer—no cloud uploads needed.

## Before You Start

Make sure you have:
- **macOS 11+**, **Windows 10/11**, or **Ubuntu 20.04+**
- **Python 3.10** or higher ([check your version](https://www.python.org/downloads/))
- **8GB RAM** minimum (16GB+ recommended)

**Optional but recommended:**
- NVIDIA GPU for faster transcription
- Ollama for AI-powered analysis

## Step 1: Download the App

Visit the [releases page](https://github.com/melomba2/meeting-recap-app/releases) and download the version for your operating system:

- **macOS**: Download the `.dmg` file
- **Windows**: Download the `.msi` installer
- **Linux**: Download the `.AppImage` file

Install it like any other application.

## Step 2: Run the Setup Script (First Time Only)

**macOS/Linux:**
```bash
cd ~/Downloads  # or wherever you cloned the repository
bash scripts/setup.sh
```

**Windows (PowerShell):**
```powershell
cd Downloads  # or wherever you cloned the repository
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

This script will:
- ✅ Verify Python 3.10+ is installed
- ✅ Install FFmpeg (needed for audio processing)
- ✅ Create a Python virtual environment
- ✅ Install all required Python libraries

**Takes 2-5 minutes depending on your internet speed.**

### Troubleshooting Setup

**Error: "Python not found"**
- Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

**Error: "FFmpeg not found"**
- **macOS**: `brew install ffmpeg`
- **Windows**: `winget install FFmpeg`
- **Linux**: `sudo apt install ffmpeg`

## Step 3: Optional - Set Up Ollama (For AI Analysis)

To enable transcript analysis and recap generation, you'll need Ollama running.

### Quick Setup

1. **Install Ollama**: Visit https://ollama.ai and download for your OS
2. **Start Ollama**: Run the app (it should start automatically)
3. **Download a model**:
   ```bash
   ollama pull gemma3n:latest
   # or try: ollama pull llama2:latest
   ```

**That's it!** Ollama will run in the background on `http://localhost:11434`

### Want a Smaller Model?

Try `ollama pull orca-mini:latest` (faster, lighter, still good quality)

---

## Now You're Ready!

### Launch the App

Click the Meeting Recap App icon to start the application.

### Basic Workflow

1. **Upload a Recording**
   - Click the upload area or drag-and-drop an audio/video file
   - Supported formats: MP3, WAV, M4A, MP4, MKV

2. **Choose Your Settings**
   - **Transcription Model**: Start with `small` or `medium` (faster, good quality)
   - **Analysis Model**: Leave as default if you just installed Ollama
   - **Recap Style**: Choose from Epic, Casual, Dramatic

3. **Click "Process"**
   - Watch the progress bar (3 stages: transcription → analysis → recap)
   - Takes 2-10 minutes depending on file length and your hardware

4. **View Results**
   - Results are saved to the `output/` folder in your home directory
   - Files are organized by date and time
   - Open `.txt` files in any text editor

---

## Tips for Best Results

### 🎤 Audio Quality Matters

- Use recordings with clear audio (minimize background noise)
- Use recent audio format files (MP3, WAV, M4A preferred)
- MP4 videos work great for meetings

### 🚀 Performance Tips

- **First time running**: The first transcription will be slower (model downloads)
- **Faster results**: Use the `tiny` or `base` model if speed matters more than accuracy
- **Better quality**: Use `medium` or `large` model for meetings with technical discussions
- **GPU acceleration**: If you have an NVIDIA GPU, transcription will be 3-10x faster

### 💾 Output

All results are saved to:
- **macOS/Linux**: `~/meeting-recap-app-output/` (or set custom path in settings)
- **Windows**: `C:\Users\[YourUsername]\meeting-recap-app-output\`

### 🔧 Settings

Click the **Settings** button to:
- Change output directory
- Adjust server URLs if using remote servers
- Change default models
- Test connections

---

## Common Questions

**Q: Is my data private?**
A: Yes! Everything runs locally on your computer. No cloud uploads. 🔒

**Q: Can I process very long recordings?**
A: Yes, but very large files (>2GB) may take a while. Transcription time varies with file length.

**Q: Can I use this without Ollama?**
A: Yes! You can transcribe without analysis/recap generation. Just upload a file and transcribe.

**Q: What if transcription takes too long?**
A: Try using a smaller model (`tiny` or `base`). You can always re-process with a better model later.

**Q: Where are my files saved?**
A: By default, in a folder in your home directory. See Settings to change this.

---

## Getting Help

If something goes wrong:

1. **Check the Settings** → Test Connection buttons
2. **See [Troubleshooting](README.md#troubleshooting)** in the full README
3. **Report a bug**: [GitHub Issues](https://github.com/melomba2/meeting-recap-app/issues)
4. **Ask questions**: [GitHub Discussions](https://github.com/melomba2/meeting-recap-app/discussions)

---

## What's Next?

Once you're comfortable with the basics:

- 📖 Check out [README.md](README.md) for advanced features
- 🔗 Learn about [remote GPU transcription](SETUP_SERVERS.md)
- 💻 Integrate with other tools using the [REST API](README.md#local-rest-api-server)
- 🤝 See [CONTRIBUTING.md](CONTRIBUTING.md) if you want to help develop

---

**Happy transcribing! 🎙️**

Questions? Join our [Discussions](https://github.com/melomba2/meeting-recap-app/discussions) or [open an issue](https://github.com/melomba2/meeting-recap-app/issues).
