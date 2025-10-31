
# Create Component 1: UI Framework - Fixed

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

---

### Step 3: Configure Python Integration

**Add Python Sidecar Support**:

```bash
# Add Python plugin to Tauri
npx @tauri-apps/cli add python
```

This creates Python integration directories and configuration.

---

### Step 4: Development Workflow

**Run Development Server**:

```bash
# Terminal 1: Start frontend dev server
npm run dev

# Terminal 2: Start Tauri in dev mode
npm run tauri dev
```

**Hot Reload**: 
- Frontend changes reload automatically
- Rust changes require rebuild (automatic with tauri dev)
- Python changes require restarting Tauri

**Debugging**:
- Frontend: Use browser DevTools (right-click → Inspect)
- Rust: Check terminal output
- Python: Check log files or stderr output

---

### Step 5: Building for Distribution

**Create Production Build**:

```bash
# Build for current platform
npm run tauri build
```

---

## Troubleshooting

### Python Not Found
- Verify Python is in system PATH
- Check tauri.conf.json has correct Python path
- Try absolute path to Python executable

### GPU Not Detected in App
- Verify CUDA drivers installed
- Check app has permission to access GPU
- Test with nvidia-smi command

### File Access Denied
- Check tauri.conf.json allowlist includes required paths
- Verify user has read/write permissions
- Test with different file locations

### Build Fails
- Clear build cache: cargo clean
- Update dependencies: npm update and cargo update
- Check error messages for missing system dependencies

---

## Next Steps

After completing this component:
1. Verify app launches and UI displays correctly
2. Confirm Python backend communication works
3. Test file selection and basic workflows
4. Proceed to Component 2: Backend Integration

---

## Resources

- Tauri Docs: https://tauri.app/v1/guides/
- Tauri Python Plugin: https://github.com/tauri-apps/tauri-plugin-python
- Rust Book: https://doc.rust-lang.org/book/
- Serde JSON: https://docs.rs/serde_json/

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
