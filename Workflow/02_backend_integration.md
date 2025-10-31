# Component 2: Backend Integration Workflow

## Overview
Refactor batch and Python scripts into a modular backend for UI and API compatibility.

---

## Steps

### 1. Audit Existing Scripts
- List all batch and Python modules (transcriber, analyzer, recap generator).
- Document folder dependencies, required packages, and input/output files.

### 2. Refactor Into Python Modules
- Existing scripts are in "python scripts/" directory (local_processor.py, transcript_analyzer.py, recap_generator.py).
- Create integration layer in src-python/ to wrap existing scripts (file_handler.py for I/O, main.py for orchestration).
- Each function should take arguments, perform the task, and return structured output via dict/JSON.

### 3. Create a Unified API Surface
- Expose functions for: transcription, analysis, recap generation, file listing, and status reporting.
- Design simple Python methods callable from UI or REST API.

### 4. Implement Progress & Logging
- Use Python's logging module; store log files per job.
- Add progress callbacks to update UI or API status.

### 5. Error Handling
- Wrap major functions in try/except blocks, returning status and error info.

### 6. Documentation
- Write docstrings and developer READMEs for all public functions.

---

## Module Structure

**Existing Scripts** (in "python scripts/" directory):
- local_processor.py (Whisper transcription, RTX 5090 optimized)
- transcript_analyzer.py (Ollama/Gemma3n integration)
- recap_generator.py (D&D-style story recap synthesis)

**Integration Layer** (to be created in src-python/):
- main.py (orchestrates workflow and calls existing scripts)
- file_handler.py (I/O management, file validation)
- api_server.py (REST endpoints wrapping existing scripts)
- obsidian_client.py (vault interaction)

---

## Testing Strategy
- Unit test each module in isolation with known inputs/outputs.
- Integration test complete pipeline: audio file → transcript → analysis → recap → file export.

---

## Completion Criteria
- All workflows run from backend entry point with structured results.
- Can be called via Tauri/Electron bridge or REST API.
- Logging and error management robust for all jobs.
