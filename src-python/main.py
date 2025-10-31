#!/usr/bin/env python3
"""
Main entry point for Meeting Recap App Python backend.
Handles communication between Tauri frontend and Python processing scripts.
"""

import sys
import json
import os
from pathlib import Path

# Add parent directory to path to import existing scripts
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.append(str(PROJECT_ROOT / "python scripts"))


def send_response(status, data=None, error=None):
    """Send JSON response to frontend via stdout"""
    response = {"status": status}
    if data:
        response["data"] = data
    if error:
        response["error"] = error

    print(json.dumps(response), flush=True)


def send_progress(stage, progress, message):
    """Send progress update to frontend"""
    response = {
        "type": "progress",
        "stage": stage,
        "progress": progress,
        "message": message
    }
    print(json.dumps(response), flush=True)


def process_command(command):
    """Process incoming command from frontend"""
    cmd_type = command.get("command")

    if cmd_type == "transcribe":
        # Import and call transcription script
        try:
            from datetime import datetime

            file_path = command.get("file")
            model = command.get("model", "medium")
            mode = command.get("mode", "local")  # "local" or "remote"
            whisper_host = command.get("whisper_host", "http://localhost:9000")

            if not file_path:
                send_response("error", error="File path is required")
                return

            # Use both stdout and stderr for debugging
            print(f"\n=== TRANSCRIPTION DEBUG START ===", file=sys.stderr, flush=True)
            print(f"Mode: {mode}", file=sys.stderr, flush=True)
            print(f"File: {file_path}", file=sys.stderr, flush=True)
            print(f"Model: {model}", file=sys.stderr, flush=True)
            print(f"File exists: {os.path.exists(file_path)}", file=sys.stderr, flush=True)

            # Generate output path for transcript (same for both local and remote)
            input_path = Path(file_path)
            output_path = input_path.parent / f"{input_path.stem}_{model}_transcript.txt"

            print(f"Output: {output_path}", file=sys.stderr, flush=True)

            if mode == "remote":
                # Use remote Whisper server
                print(f"Using remote Whisper server at {whisper_host}", file=sys.stderr, flush=True)
                from remote_whisper_client import RemoteWhisperClient

                send_progress("transcription", 0, "Connecting to remote Whisper server...")

                client = RemoteWhisperClient(whisper_host=whisper_host)

                # Check connection
                if not client.check_connection():
                    error_msg = f"Cannot connect to remote Whisper server at {whisper_host}. Server may be offline or unreachable."
                    print(f"Connection check failed: {error_msg}", file=sys.stderr, flush=True)
                    send_response("error", error=error_msg)
                    return

                print(f"Remote server connection successful", file=sys.stderr, flush=True)
                send_progress("transcription", 15, f"Sending to remote server at {whisper_host}...")

                # Transcribe using remote server
                print(f"Calling remote transcribe_and_save...", file=sys.stderr, flush=True)
                result = client.transcribe_and_save(str(file_path), str(output_path), model=model, language="en")

                print(f"Remote transcribe result: {result}", file=sys.stderr, flush=True)

            else:
                # Use local Whisper (original behavior)
                print(f"Using local Whisper processor", file=sys.stderr, flush=True)
                from whisper_processor import WhisperProcessor

                send_progress("transcription", 0, "Initializing Whisper processor...")

                processor = WhisperProcessor(model_name=model)
                print(f"Processor initialized", file=sys.stderr, flush=True)

                send_progress("transcription", 15, "Loading Whisper model (this may take a minute)...")
                print(f"Loading model {model}...", file=sys.stderr, flush=True)

                try:
                    model_loaded = processor.load_model()
                    print(f"Model load_model() returned: {model_loaded}", file=sys.stderr, flush=True)
                    if not model_loaded:
                        send_response("error", error="Failed to load Whisper model - load_model() returned False")
                        return
                except Exception as load_err:
                    print(f"Exception during load_model(): {load_err}", file=sys.stderr, flush=True)
                    import traceback
                    traceback.print_exc(file=sys.stderr)
                    send_response("error", error=f"Failed to load model: {str(load_err)}")
                    return

                print(f"Model loaded successfully", file=sys.stderr, flush=True)
                send_progress("transcription", 30, f"Transcribing {Path(file_path).name}...")

                print(f"Input: {input_path}", file=sys.stderr, flush=True)

                # Transcribe the file
                print(f"Calling transcribe_file...", file=sys.stderr, flush=True)
                result = processor.transcribe_file(str(file_path), str(output_path))

                print(f"Transcribe result: {result}", file=sys.stderr, flush=True)

            if result and output_path.exists():
                print(f"Output file created, size: {output_path.stat().st_size} bytes", file=sys.stderr, flush=True)
            else:
                print(f"Result is None or output file not created", file=sys.stderr, flush=True)

            print(f"=== TRANSCRIPTION DEBUG END ===\n", file=sys.stderr, flush=True)

            if result:
                send_progress("transcription", 100, "Transcription complete!")
                send_response("success", data={
                    "transcript_path": str(result),
                    "message": "Transcription completed successfully"
                })
            else:
                send_response("error", error="Transcription returned None - check terminal output for details")

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"=== EXCEPTION ===\n{error_trace}\n=== END EXCEPTION ===", file=sys.stderr, flush=True)
            send_response("error", error=f"{type(e).__name__}: {str(e)}")

    elif cmd_type == "analyze":
        # Import and call analyzer script
        try:
            from transcript_analyzer import OllamaTranscriptAnalyzer
            from datetime import datetime

            file_path = command.get("file")
            model = command.get("model", "gemma3n:latest")
            ollama_host = command.get("ollama_host", "http://localhost:11434")

            if not file_path:
                send_response("error", error="File path is required")
                return

            send_progress("analysis", 0, "Initializing analyzer...")

            analyzer = OllamaTranscriptAnalyzer(ollama_host=ollama_host)

            send_progress("analysis", 30, "Analyzing transcript...")

            # Generate output path for analysis
            # Extract base name from transcript (remove _transcript suffix)
            input_path = Path(file_path)
            transcript_stem = input_path.stem  # e.g., 'meeting_medium_transcript'
            base_name = transcript_stem.replace('_transcript', '', 1)  # e.g., 'meeting_medium'
            output_path = input_path.parent / f"{base_name}_analysis.txt"

            # Analyze the transcript file
            result = analyzer.analyze_transcript(str(file_path), model=model, output_path=str(output_path))

            if result:
                send_progress("analysis", 100, "Analysis complete!")
                send_response("success", data={
                    "analysis_path": str(result),
                    "message": "Analysis completed successfully"
                })
            else:
                send_response("error", error="Analysis failed")

        except Exception as e:
            send_response("error", error=str(e))

    elif cmd_type == "recap":
        # Import and call recap generator
        try:
            from recap_generator import DNDRecapGenerator
            from datetime import datetime

            file_path = command.get("file")
            style = command.get("style", "epic")
            model = command.get("model", "gemma3n:latest")
            ollama_url = command.get("ollama_url", "http://192.168.68.10:11434")

            if not file_path:
                send_response("error", error="File path is required")
                return

            send_progress("recap", 0, "Initializing recap generator...")

            generator = DNDRecapGenerator(ollama_host=ollama_url)

            send_progress("recap", 30, f"Generating {style} style recap...")

            # Generate output path for recap
            # Extract base name from analysis (remove _analysis suffix)
            input_path = Path(file_path)
            analysis_stem = input_path.stem  # e.g., 'meeting_medium_analysis'
            base_name = analysis_stem.replace('_analysis', '', 1)  # e.g., 'meeting_medium'
            output_path = input_path.parent / f"{base_name}_recap.txt"

            # Generate recap from analysis file
            result = generator.generate_recap(str(file_path), model=model, style=style, output_path=str(output_path))

            if result:
                send_progress("recap", 100, "Recap generation complete!")
                send_response("success", data={
                    "recap_path": str(result),
                    "message": "Recap generated successfully"
                })
            else:
                send_response("error", error="Recap generation failed")

        except Exception as e:
            send_response("error", error=str(e))

    elif cmd_type == "check_whisper_health":
      # Check health of remote Whisper server
      try:
          whisper_host = command.get("whisper_host", "http://localhost:9000")
          print(f"DEBUG: check_whisper_health called with host: {whisper_host}", file=sys.stderr, flush=True)

          from remote_whisper_client import RemoteWhisperClient

          client = RemoteWhisperClient(whisper_host=whisper_host)
          print(f"DEBUG: Client created", file=sys.stderr, flush=True)

          if client.check_connection():
              print(f"DEBUG: Connection check passed", file=sys.stderr, flush=True)
              # Try to get available models
              models = client.get_available_models()
              print(f"DEBUG: Got models: {models}", file=sys.stderr, flush=True)
              send_response("success", data={
                  "status": "online",
                  "host": whisper_host,
                  "models": models
              })
          else:
              print(f"DEBUG: Connection check failed", file=sys.stderr, flush=True)
              send_response("error", error=f"Cannot connect to Whisper server at {whisper_host}")
      except Exception as e:
          print(f"DEBUG: Exception in check_whisper_health: {e}", file=sys.stderr, flush=True)
          import traceback
          traceback.print_exc(file=sys.stderr)
          send_response("error", error=str(e))

    elif cmd_type == "check_ollama_health":
      # Check health of remote Ollama server
      try:
          ollama_host = command.get("ollama_host", "http://localhost:11434")
          print(f"DEBUG: check_ollama_health called with host: {ollama_host}", file=sys.stderr, flush=True)

          import requests

          # Check if Ollama server is running by calling the tags endpoint
          try:
              response = requests.get(f"{ollama_host}/api/tags", timeout=5)
              print(f"DEBUG: Ollama health check response: {response.status_code}", file=sys.stderr, flush=True)

              if response.status_code == 200:
                  data = response.json()
                  models = [model['name'] for model in data.get('models', [])]
                  print(f"DEBUG: Got models: {models}", file=sys.stderr, flush=True)
                  send_response("success", data={
                      "status": "online",
                      "host": ollama_host,
                      "models": models
                  })
              else:
                  send_response("error", error=f"Ollama server returned status {response.status_code}")
          except requests.exceptions.Timeout:
              send_response("error", error=f"Timeout connecting to Ollama server at {ollama_host}")
          except requests.exceptions.ConnectionError:
              send_response("error", error=f"Cannot connect to Ollama server at {ollama_host}")

      except Exception as e:
          print(f"DEBUG: Exception in check_ollama_health: {e}", file=sys.stderr, flush=True)
          import traceback
          traceback.print_exc(file=sys.stderr)
          send_response("error", error=str(e))

def main():
    """Main loop - read commands from stdin and process them"""
    try:
        # Debug: verify imports work
        print(f"=== PYTHON BACKEND STARTED ===", file=sys.stderr, flush=True)
        print(f"Python version: {sys.version}", file=sys.stderr, flush=True)
        print(f"Working directory: {os.getcwd()}", file=sys.stderr, flush=True)
        print(f"sys.path:", file=sys.stderr, flush=True)
        for p in sys.path:
            print(f"  - {p}", file=sys.stderr, flush=True)
        print(f"=== WAITING FOR COMMANDS ===", file=sys.stderr, flush=True)

        # Read command from stdin
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            print(f"\n>>> Received command: {line[:100]}", file=sys.stderr, flush=True)

            try:
                command = json.loads(line)
                process_command(command)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}", file=sys.stderr, flush=True)
                send_response("error", error=f"Invalid JSON: {str(e)}")
            except Exception as e:
                print(f"Unexpected error: {e}", file=sys.stderr, flush=True)
                import traceback
                traceback.print_exc(file=sys.stderr)
                send_response("error", error=f"Unexpected error: {str(e)}")

    except KeyboardInterrupt:
        print(f"Keyboard interrupt received", file=sys.stderr, flush=True)
        send_response("info", data={"message": "Python backend shutting down"})


if __name__ == "__main__":
    main()