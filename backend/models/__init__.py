"""
TTS Model Testing Package
Contains offline testing scripts for XTTS-v2 and Piper TTS models.
"""

from pathlib import Path

__version__ = "1.0.0"

# Output directory for test results
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

__all__ = ["OUTPUT_DIR"]

