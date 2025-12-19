import os
import sys
import logging

# Add current dir to path
sys.path.insert(0, os.path.abspath("."))

from bot import voice_utils

def test_ffmpeg():
    print("Testing FFmpeg configuration...")
    print(f"PATH: {os.environ['PATH']}")
    
    # Check if we can find ffmpeg in path
    import shutil
    ffmpeg_bin = shutil.which("ffmpeg")
    if ffmpeg_bin:
        print(f"SUCCESS: Found ffmpeg at {ffmpeg_bin}")
    else:
        print("FAILURE: ffmpeg not found in PATH")

    # Try to load whisper (this might take a while, so maybe just check import)
    try:
        import whisper
        print("SUCCESS: Whisper imported")
    except ImportError as e:
        print(f"FAILURE: Whisper import failed: {e}")

if __name__ == "__main__":
    test_ffmpeg()
