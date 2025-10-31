import sys
from pathlib import Path

# Add project root to the path
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

from src_python.whisper_processor import WhisperProcessor

print("WhisperProcessor imported successfully!")
