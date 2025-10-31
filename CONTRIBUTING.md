# Contributing to Meeting Recap App

Thanks for interest in contributing! This document provides guidelines and instructions.

## Code of Conduct

Be respectful and constructive. We welcome contributions from everyone regardless of experience level.

## Ways to Contribute

### 1. Report Bugs 🐛

Found a bug? Open an issue with:
- **Clear title**: What's broken
- **Steps to reproduce**: How you found it
- **Expected behavior**: What should happen
- **Actual behavior**: What does happen
- **Environment**: OS, Python version, GPU info

**Example:**
```
Title: FFmpeg not found error on Windows

Steps:
1. Run setup.ps1 on clean Windows install
2. Click "Start Processing"

Expected: App processes file
Actual: Error "FFmpeg command not found"

Environment: Windows 11, Python 3.11, no GPU
```

### 2. Suggest Features 💡

Have an idea? Open an issue with:
- **Clear description**: What and why
- **Use case**: Who benefits and when
- **Implementation notes**: How you'd approach it (optional)

**Example:**
```
Title: Add batch processing for multiple files

Description: Allow users to queue multiple files
and process them sequentially overnight.

Use case: Developers with many recordings
to process without manual clicking.

Implementation: Add file queue UI,
background job processing...
```

### 3. Submit Code 👨‍💻

Interested in coding? Follow these steps:

#### Setup Development Environment

```bash
# 1. Fork and clone
git clone https://github.com/melomba2/meeting-recap-app.git
cd meeting-recap-app

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Run setup script
./scripts/setup.sh  # macOS/Linux
# or
.\scripts\setup.ps1  # Windows

# 4. Install Node dependencies
npm install

# 5. Start development
npm run dev  # In one terminal
npm run tauri:dev  # In another terminal
```

#### Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/short-description
   # Examples: feature/batch-processing, fix/gpu-detection
   ```

2. **Make your changes**:
   - Keep commits focused and atomic
   - Follow the existing code style
   - Test your changes thoroughly

3. **Test locally**:
   ```bash
   # Frontend: Right-click in app → Inspect → Console for errors
   # Backend: Check terminal output for Python/Rust errors

   # Build for production
   npm run tauri:build
   ```

4. **Push and create Pull Request**:
   ```bash
   git push origin feature/your-feature
   ```
   Then open PR on GitHub with:
   - Clear title
   - Description of what changed and why
   - How to test it
   - Any breaking changes

#### Code Style Guidelines

**JavaScript/Frontend:**
- Use const/let, not var
- Camel case for variables: `myVariable`
- 2-space indentation
- Descriptive variable names: `transcriptionModelSelect` not `ts`

**Python Backend:**
- Follow PEP 8 guidelines
- Type hints where practical
- Docstrings for functions
- 4-space indentation

**Rust Backend:**
- Use `cargo fmt` before committing
- Follow Rust naming conventions
- Document public functions

### 4. Improve Documentation 📚

Good docs help everyone! You can:
- Fix typos
- Clarify confusing sections
- Add examples
- Translate to other languages

## Project Structure

```
meeting-recap-app/
├── src/                    # Frontend (HTML/CSS/JavaScript)
│   ├── index.html         # Main UI
│   ├── main.js            # App logic & event handlers
│   └── styles.css         # Styling
│
├── src-tauri/             # Rust backend
│   ├── src/
│   │   ├── main.rs        # Tauri commands & Python bridge
│   │   └── lib.rs         # Library code
│   ├── Cargo.toml         # Rust dependencies
│   └── tauri.conf.json    # App configuration
│
├── src-python/            # Python processing modules
│   ├── main.py            # Entry point
│   ├── whisper_processor.py    # Transcription
│   ├── transcript_analyzer.py  # Analysis
│   ├── recap_generator.py      # Recap generation
│   └── remote_whisper_client.py # Remote transcription
│
├── scripts/               # Utility scripts
│   ├── setup.sh          # macOS/Linux setup
│   └── setup.ps1         # Windows setup
│
└── config/                # Configuration
    └── defaults.json      # Default settings
```

## Key Technologies

- **Frontend**: Vanilla JavaScript, HTML, CSS
- **Desktop**: Tauri v2 (lightweight Electron alternative)
- **Backend**: Rust (Tauri commands)
- **Processing**: Python 3.10+
- **Build**: npm, Cargo

## Common Development Tasks

### Adding a New Feature

1. **Update UI** (`src/index.html`):
   ```html
   <div id="my-feature">
     <input type="text" id="my-input" />
     <button id="my-button">Do Something</button>
   </div>
   ```

2. **Add event handler** (`src/main.js`):
   ```javascript
   const myButton = document.getElementById('my-button');
   myButton.addEventListener('click', async () => {
     const value = document.getElementById('my-input').value;
     try {
       const result = await invoke('my_command', { value });
       console.log(result);
     } catch (error) {
       console.error('Error:', error);
     }
   });
   ```

3. **Add Tauri command** (`src-tauri/src/main.rs`):
   ```rust
   #[tauri::command]
   fn my_command(value: String) -> Result<String, String> {
       println!("Got value: {}", value);
       Ok(format!("Processed: {}", value))
   }
   ```

4. **Register command** in `main.rs`:
   ```rust
   .invoke_handler(tauri::generate_handler![
       test_python,
       transcribe_audio,
       analyze_transcript,
       generate_recap,
       check_whisper_health,
       check_ollama_health,
       my_command  // Add here
   ])
   ```

### Adding Python Processing

1. **Create module** in `src-python/`:
   ```python
   # src-python/my_processor.py
   class MyProcessor:
       def __init__(self):
           pass

       def process(self, data):
           """Process data and return result"""
           return result
   ```

2. **Import in main.py**:
   ```python
   from my_processor import MyProcessor

   elif cmd_type == "my_process":
       processor = MyProcessor()
       result = processor.process(data)
       send_response("success", data={"result": result})
   ```

3. **Call from frontend** (`src/main.js`):
   ```javascript
   const result = await invoke('call_python', {
       command: "my_process",
       data: inputData
   });
   ```

### Building for Production

```bash
# Build Tauri app for your platform
npm run tauri:build

# Find executable in:
# macOS: src-tauri/target/release/bundle/macos/Meeting\ Recap\ Processor.app
# Windows: src-tauri/target/release/Meeting Recap Processor.exe
# Linux: src-tauri/target/release/meeting-recap-app
```

## Testing

### Manual Testing

1. **Test transcription**:
   - Use a short audio file (30 seconds)
   - Test with different model sizes
   - Verify output file is created

2. **Test analysis**:
   - Verify Ollama is running
   - Check that analysis completes
   - Review output for quality

3. **Test recap**:
   - Verify different styles work
   - Check output formatting

### Before Submitting PR

- [ ] Code works locally
- [ ] No console errors (F12 DevTools)
- [ ] No Rust compiler warnings (`cargo check`)
- [ ] No Python errors
- [ ] Existing features still work

## Debugging Tips

### Frontend Issues

```javascript
// Use console for debugging
console.log('Value:', myVariable);
console.error('Error occurred:', errorObject);

// Check localStorage
localStorage.getItem('whisper_host')
```

**Browser DevTools:**
- F12 or Right-click → Inspect
- Console tab: See errors and logs
- Network tab: Check API calls
- Application tab: Check localStorage

### Backend (Python) Issues

```python
# Add debug output
print(f"DEBUG: value={value}", file=sys.stderr, flush=True)

# Import traceback for stack traces
import traceback
traceback.print_exc()
```

Output appears in terminal running `npm run tauri:dev`.

### Rust Issues

```rust
// Use println! for debugging
println!("DEBUG: value={}", value);

// Check compiler warnings
cargo check
```

## Performance Considerations

1. **Keep UI responsive**: Don't block on heavy operations
2. **Optimize Python**: Profile slow sections
3. **Cache models**: Don't reload models unnecessarily
4. **Limit file sizes**: Warn if file > 2GB

## Adding Dependencies

**Python packages:**
1. Add to `requirements.txt`
2. Run `pip install -r requirements.txt`
3. Test thoroughly

**Node packages:**
1. `npm install package-name`
2. Test with `npm run tauri:dev`

**Rust crates:**
1. Update `src-tauri/Cargo.toml`
2. Run `cargo build`
3. Test compilation

## Commit Guidelines

Write clear commit messages:

```bash
# Good
git commit -m "Add batch processing for multiple files"

# Also good
git commit -m "
Fix GPU detection on Windows

- Check CUDA availability with nvidia-smi
- Show helpful error if CUDA not found
- Fallback to CPU mode gracefully
"

# Avoid
git commit -m "fix"
git commit -m "update stuff"
```

## Pull Request Process

1. **Create feature branch** from `main`
2. **Make focused commits** (one feature per branch)
3. **Test thoroughly** before pushing
4. **Create pull request** with clear description
5. **Respond to feedback** professionally
6. **Maintainer reviews** and merges when ready

## Release Process

1. Update version in `src-tauri/tauri.conf.json`
2. Update `CHANGELOG.md` (if you create one)
3. Create git tag: `git tag v0.2.0`
4. Push: `git push origin v0.2.0`
5. GitHub Actions builds automatically
6. Artifacts upload to GitHub Releases

## Getting Help

- **Questions?** Open a Discussion (if available)
- **Stuck?** Open a Draft PR and ask for help
- **Need guidance?** Comment on an issue

## Recognition

Contributors will be acknowledged in:
- README.md (if desired)
- Release notes
- Project credits

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thanks for contributing! 🎉**

Questions? Open an issue or start a discussion!
