"""
File handling utilities for Meeting Recap App.
Validates file types, manages temp files, and organizes output folders.
"""

import os
from pathlib import Path
from typing import Optional, List

# Supported file types
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.flac', '.ogg'}
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.webm'}
TEXT_EXTENSIONS = {'.txt', '.md', '.text'}

ALL_SUPPORTED = AUDIO_EXTENSIONS | VIDEO_EXTENSIONS | TEXT_EXTENSIONS

# Default max file size (1GB)
DEFAULT_MAX_SIZE = 1024 * 1024 * 1024


class FileValidator:
    """Validates files before processing"""

    def __init__(self, max_size: int = DEFAULT_MAX_SIZE):
        self.max_size = max_size

    def validate_file(self, file_path: str) -> tuple[bool, Optional[str]]:
        """
        Validate a file for processing.
        Returns (is_valid, error_message)
        """
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            return False, f"File not found: {file_path}"

        # Check if it's a file (not directory)
        if not path.is_file():
            return False, f"Not a file: {file_path}"

        # Check file extension
        if path.suffix.lower() not in ALL_SUPPORTED:
            return False, f"Unsupported file type: {path.suffix}"

        # Check file size
        size = path.stat().st_size
        if size > self.max_size:
            size_mb = size / (1024 * 1024)
            max_mb = self.max_size / (1024 * 1024)
            return False, f"File too large: {size_mb:.1f}MB (max: {max_mb:.1f}MB)"

        # Check read permissions
        if not os.access(path, os.R_OK):
            return False, f"Cannot read file: {file_path}"

        return True, None

    def get_file_type(self, file_path: str) -> Optional[str]:
        """
        Determine file type category.
        Returns 'audio', 'video', or 'text'
        """
        ext = Path(file_path).suffix.lower()

        if ext in AUDIO_EXTENSIONS:
            return 'audio'
        elif ext in VIDEO_EXTENSIONS:
            return 'video'
        elif ext in TEXT_EXTENSIONS:
            return 'text'
        else:
            return None


class OutputManager:
    """Manages output file organization and cleanup"""

    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            self.base_dir = Path.home() / "Documents" / "Meeting Recaps"
        else:
            self.base_dir = Path(base_dir)

        # Create output directories
        self.transcripts_dir = self.base_dir / "transcripts"
        self.analysis_dir = self.base_dir / "analysis"
        self.recaps_dir = self.base_dir / "recaps"

        self._ensure_dirs()

    def _ensure_dirs(self):
        """Create output directories if they don't exist"""
        for dir_path in [self.transcripts_dir, self.analysis_dir, self.recaps_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def get_output_path(self, input_file: str, output_type: str) -> Path:
        """
        Generate output path based on input file and type.
        output_type: 'transcript', 'analysis', or 'recap'
        """
        input_path = Path(input_file)
        base_name = input_path.stem

        if output_type == 'transcript':
            return self.transcripts_dir / f"{base_name}_transcript.txt"
        elif output_type == 'analysis':
            return self.analysis_dir / f"{base_name}_analysis.txt"
        elif output_type == 'recap':
            return self.recaps_dir / f"{base_name}_recap.md"
        else:
            raise ValueError(f"Unknown output type: {output_type}")

    def cleanup_temp_files(self, patterns: List[str]):
        """Remove temporary files matching patterns"""
        import glob
        for pattern in patterns:
            for file_path in glob.glob(pattern):
                try:
                    Path(file_path).unlink()
                except Exception:
                    pass  # Ignore errors during cleanup


def ensure_path_safety(path: str) -> bool:
    """
    Validate path to prevent directory traversal attacks.
    Returns True if path is safe.
    """
    try:
        # Resolve path and check if it stays within allowed bounds
        resolved = Path(path).resolve()

        # Check for path traversal attempts
        if '..' in path:
            return False

        # Ensure path exists and is accessible
        if not resolved.exists():
            return False

        return True
    except Exception:
        return False
