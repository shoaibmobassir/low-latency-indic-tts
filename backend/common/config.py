"""
Model Configuration for TTS Engine
Defines model paths and configuration constants.
"""

from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"

# MMS-TTS Model Paths (HuggingFace)
MMS_TTS_GU_MODEL = "facebook/mms-tts-guj"
MMS_TTS_MR_MODEL = "facebook/mms-tts-mar"

# IndicTTS Configuration
INDICTTS_FALLBACK = True  # Use gTTS as fallback

# Audio Configuration
DEFAULT_SAMPLE_RATE = 16000  # Hz
DEFAULT_CHUNK_SIZE_MS = 60  # milliseconds (optimized via experiments)
DEFAULT_CHUNK_SIZE_SAMPLES = int(DEFAULT_SAMPLE_RATE * DEFAULT_CHUNK_SIZE_MS / 1000)

# Low Latency Configuration (<100ms perceived latency)
# Optimized via experiments: 60ms provides best latency/stability balance
FIRST_CHUNK_SIZE_MS = 60  # Optimized: Best balance of latency and stability
SUBSEQUENT_CHUNK_SIZE_MS = 60  # Optimized: Consistent chunk size for stability
LOW_LATENCY_MODE = True  # Enable low-latency optimizations
USE_FP16_ON_CUDA = True  # Use FP16 mixed precision on CUDA for 1.5-2x speedup
USE_TORCH_COMPILE = True  # Use torch.compile for faster inference (PyTorch 2.0+)
OPTIMIZE_CHUNK_SIZE = 5  # Smaller chunks for faster first response (words)

# Chunk Size Optimization
AUTO_TUNE_CHUNK_SIZE = False  # Enable automatic chunk size tuning (experimental)
CHUNK_SIZE_MS = 60  # Default chunk size (optimized via experiments - see experiments/FINAL_CHUNK_SIZE_REPORT.md)
CHUNK_SIZE_CANDIDATES = [10, 15, 20, 30, 40, 50, 60, 80, 100]  # Candidate sizes for testing
ENABLE_CHUNK_METADATA = True  # Send chunk metadata with timestamps for latency measurement

# Model Selection
MODEL_MMS_TTS = "mms_tts"
MODEL_INDICTTS = "indictts"

# Use Case Routing
USE_CASE_WEB_UI = "web_ui"  # High quality - use MMS-TTS
USE_CASE_TELECOM = "telecom"  # Low latency - use MMS-TTS (fallback to IndicTTS)
USE_CASE_FALLBACK = "fallback"  # Use IndicTTS

# Default Model Selection by Use Case
USE_CASE_MODEL_MAP = {
    USE_CASE_WEB_UI: MODEL_MMS_TTS,
    USE_CASE_TELECOM: MODEL_MMS_TTS,  # Use MMS-TTS for telecom
    USE_CASE_FALLBACK: MODEL_INDICTTS,
}

