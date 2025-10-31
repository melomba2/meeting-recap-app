#!/usr/bin/env python3
"""
Quick debugging script to test transcription components
"""
import sys
import os
from pathlib import Path

# Add the project directory to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

print("Testing transcription components...")
print(f"Python path: {sys.path[:3]}")

try:
    # Test 1: Check basic imports
    print("1. Testing imports...")
    import torch
    import whisper
    print("✅ PyTorch and Whisper imported successfully")
    
    # Test 2: Check CUDA availability  
    print("2. Checking CUDA availability...")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    
    # Test 3: Check system tools
    print("3. Checking system tools...")
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg found")
        else:
            print("❌ FFmpeg not found")
    except FileNotFoundError:
        print("❌ FFmpeg not installed")
    
    # Test 4: Load Whisper model
    print("4. Testing Whisper model...")
    try:
        model = whisper.load_model("medium")
        print("✅ Whisper model loaded successfully")
    except Exception as e:
        print(f"❌ Whisper model loading failed: {e}")
        
    print("\nAll basic tests completed!")

except Exception as e:
    print(f"Error during testing: {e}")
    import traceback
    traceback.print_exc()