#!/usr/bin/env python3
"""
Remote Whisper Client - HTTP client for communicating with remote Whisper transcription server.
Follows the same pattern as OllamaTranscriptAnalyzer for consistency.
"""

import requests
import sys
from pathlib import Path


class RemoteWhisperClient:
    """HTTP client for remote Whisper transcription server using faster-whisper-server API."""

    def __init__(self, whisper_host="http://192.168.68.10:9000"):
        """
        Initialize the remote Whisper client.

        Args:
            whisper_host (str): Base URL of the remote Whisper server
                               Default: http://192.168.68.10:9000
        """
        self.whisper_host = whisper_host.rstrip('/')
        self.timeout = 600  # 10 minutes timeout for large files

    def check_connection(self):
        """
        Check if the Whisper server is available and responding.

        Returns:
            bool: True if server is reachable, False otherwise
        """
        try:
            response = requests.get(
                f"{self.whisper_host}/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"[RemoteWhisperClient] Connection check failed: {e}", file=sys.stderr)
            return False

    def get_available_models(self):
        """
        Get list of available models on the remote server.

        Returns:
            list: List of available model names, or empty list if unavailable
        """
        try:
            response = requests.get(
                f"{self.whisper_host}/models",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('models', [])
            return []
        except Exception as e:
            print(f"[RemoteWhisperClient] Failed to get models: {e}", file=sys.stderr)
            return []

    def transcribe_file(self, file_path, model="medium", language="en"):
        """
        Send an audio/video file to the remote server for transcription.

        Args:
            file_path (str): Path to the audio/video file to transcribe
            model (str): Whisper model size (tiny, base, small, medium, large)
            language (str): Language code (e.g., 'en', 'fr', 'de')

        Returns:
            dict: Transcription result with 'text' key, or None if failed

        Raises:
            FileNotFoundError: If the input file doesn't exist
            requests.RequestException: If the HTTP request fails
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        print(f"[RemoteWhisperClient] Transcribing via {self.whisper_host}", file=sys.stderr)
        print(f"[RemoteWhisperClient] File: {file_path}", file=sys.stderr)
        print(f"[RemoteWhisperClient] Model: {model}", file=sys.stderr)
        print(f"[RemoteWhisperClient] Language: {language}", file=sys.stderr)

        try:
            # Prepare multipart file upload
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'model': model,
                    'language': language
                }

                print(f"[RemoteWhisperClient] Sending request to server...", file=sys.stderr)

                response = requests.post(
                    f"{self.whisper_host}/transcribe",
                    files=files,
                    data=data,
                    timeout=self.timeout
                )

                print(f"[RemoteWhisperClient] Response status: {response.status_code}", file=sys.stderr)

                if response.status_code == 200:
                    result = response.json()
                    print(f"[RemoteWhisperClient] Transcription successful", file=sys.stderr)
                    return result
                else:
                    error_msg = f"Server error ({response.status_code}): {response.text}"
                    print(f"[RemoteWhisperClient] {error_msg}", file=sys.stderr)
                    return None

        except requests.Timeout:
            error_msg = f"Request timed out after {self.timeout} seconds"
            print(f"[RemoteWhisperClient] {error_msg}", file=sys.stderr)
            return None
        except requests.ConnectionError as e:
            error_msg = f"Failed to connect to server at {self.whisper_host}: {e}"
            print(f"[RemoteWhisperClient] {error_msg}", file=sys.stderr)
            return None
        except requests.RequestException as e:
            error_msg = f"Request failed: {e}"
            print(f"[RemoteWhisperClient] {error_msg}", file=sys.stderr)
            return None
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(f"[RemoteWhisperClient] {error_msg}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return None

    def transcribe_and_save(self, input_file, output_file, model="medium", language="en"):
        """
        Transcribe audio file and save result to output file.

        This method matches the interface of WhisperProcessor.transcribe_file()
        for seamless integration.

        Args:
            input_file (str): Path to the audio/video file
            output_file (str): Path to save the transcription text
            model (str): Whisper model size
            language (str): Language code

        Returns:
            str: Path to the output file if successful, None if failed
        """
        output_path = Path(output_file)

        try:
            # Get transcription from remote server
            result = self.transcribe_file(input_file, model=model, language=language)

            if result is None:
                print(f"[RemoteWhisperClient] Transcription returned None", file=sys.stderr)
                return None

            # Extract text from result
            transcript_text = result.get('text', '')

            if not transcript_text:
                print(f"[RemoteWhisperClient] Empty transcription result", file=sys.stderr)
                return None

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save transcription to file
            print(f"[RemoteWhisperClient] Saving to {output_path}", file=sys.stderr)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(transcript_text)

            print(f"[RemoteWhisperClient] Saved {output_path.stat().st_size} bytes", file=sys.stderr)
            return str(output_path)

        except Exception as e:
            print(f"[RemoteWhisperClient] Failed to save transcription: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return None


def test_connection(host="http://192.168.68.10:9000"):
    """
    Test connection to a Whisper server.
    Useful for debugging connection issues.

    Args:
        host (str): Whisper server URL
    """
    client = RemoteWhisperClient(whisper_host=host)
    print(f"Testing connection to {host}...")

    if client.check_connection():
        print("✅ Connection successful!")
        models = client.get_available_models()
        if models:
            print(f"Available models: {', '.join(models)}")
        else:
            print("Models endpoint not available or empty")
    else:
        print("❌ Connection failed - server is not reachable")


if __name__ == "__main__":
    # Test the client
    test_connection()
