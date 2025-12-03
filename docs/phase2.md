# Phase 2: GPU TTS Runtime Layer

## Overview

Phase 2 implements the core GPU-accelerated TTS inference engine that serves as the foundation for all TTS operations in the system.

## Responsibilities

1. **Unified TTS Engine** - Single interface for all TTS models
2. **GPU Optimization** - Automatic device detection and optimization
3. **Model Loading** - Dynamic loading of MMS-TTS, Piper, and IndicTTS
4. **Audio Processing** - Chunking, normalization, format conversion
5. **Streaming Support** - Real-time chunk generation for WebSocket streaming

## Architecture

### TTSEngine Class

The `TTSEngine` class provides a unified interface for all TTS operations:

```
TTSEngine
├── Device Detection (CUDA/MPS/CPU)
├── Model Loading
│   ├── load_mms_tts() - High quality neural TTS
│   ├── load_piper() - Low latency ONNX model
│   └── load_indictts() - gTTS fallback
├── Inference
│   ├── infer_wav() - Complete audio generation
│   └── infer_chunked() - Streaming chunk generation
└── Audio Processing
    ├── Normalization
    ├── Silence trimming
    └── Format conversion
```

### Model Routing Logic

Models are selected based on use case:

- **Web UI** → MMS-TTS (high quality)
- **Telecom** → Piper TTS (low latency)
- **Fallback** → IndicTTS (gTTS)

### Device Detection

Automatic device detection with priority:

1. **CUDA** (NVIDIA H100) - Production deployment
2. **MPS** (Apple Silicon) - Local development
3. **CPU** - Fallback

## GPU Optimization Strategies

### MMS-TTS Optimization

- **FP16 Precision**: Automatic FP16 conversion for CUDA devices
- **Device Placement**: Automatic tensor movement to GPU
- **Memory Management**: GPU cache clearing after operations

### Piper TTS Optimization

- **ONNX Runtime Providers**: CUDA execution provider when available
- **CPU Fallback**: Automatic fallback if CUDA unavailable

### IndicTTS Optimization

- **CPU-only**: gTTS runs on CPU (no GPU support)

## Audio Processing

### Chunking

- **Default Chunk Size**: 40ms
- **Configurable**: Can be adjusted per use case
- **Real-time Ready**: Chunks are ready for WebSocket streaming

### Format Conversion

- **PCM 16kHz**: Standard format for Web UI
- **PCM 8kHz**: Telecom standard
- **G.711 µ-law**: Compressed format for telecom

### Normalization

- Automatic audio normalization to [-1, 1] range
- Silence trimming from beginning and end
- Sample rate conversion when needed

## Benchmarks Target

### Latency Targets

- **Web UI Generation**: <100ms (text → audio)
- **Telecom Chunk Generation**: <50ms per chunk
- **Model Loading**: <5 seconds (cold start)

### Performance Expectations

#### Local Development (M1 Mac)
- MMS-TTS: ~200-500ms per sentence (MPS)
- Piper TTS: ~50-100ms per sentence (CPU)
- IndicTTS: ~500-1000ms per sentence (CPU)

#### Production Deployment (H100 GPU)
- MMS-TTS: ~50-100ms per sentence (CUDA)
- Piper TTS: ~20-50ms per sentence (CUDA)
- IndicTTS: ~500-1000ms per sentence (CPU)

## Known Limitations

### Model-Specific Limitations

1. **MMS-TTS**
   - Requires GPU for optimal performance
   - FP16 conversion may fail on some models (falls back to FP32)
   - MPS support is experimental

2. **Piper TTS**
   - Requires model files to be present locally
   - ONNX Runtime CUDA provider must be installed
   - Command-line interface dependency

3. **IndicTTS**
   - Currently uses gTTS (requires internet)
   - No GPU acceleration
   - Quality may vary

### Device Limitations

1. **MPS (Apple Silicon)**
   - Not all operations are optimized
   - Some models may fall back to CPU
   - Performance varies by model

2. **CUDA (NVIDIA)**
   - Requires CUDA-compatible GPU
   - ONNX Runtime CUDA provider must be installed
   - Memory constraints on smaller GPUs

## File Structure

```
backend/common/
├── tts_engine.py      # Core TTS engine
├── streaming.py       # Chunking and format conversion
├── config.py          # Model configuration
└── device_utils.py    # Device detection (from Phase 1)
```

## Usage Example

```python
from backend.common.tts_engine import TTSEngine, USE_CASE_WEB_UI, USE_CASE_TELECOM

# Initialize engine
engine = TTSEngine()

# Generate complete audio (Web UI)
waveform, sample_rate = engine.infer_wav(
    text="નમસ્તે",
    language="gu",
    use_case=USE_CASE_WEB_UI
)

# Generate streaming chunks (Telecom)
for chunk in engine.infer_chunked(
    text="નમસ્તે",
    language="gu",
    use_case=USE_CASE_TELECOM,
    chunk_ms=40
):
    # Send chunk via WebSocket
    pass
```

## Next Steps

Phase 2 provides the foundation for:
- **Phase 3**: Web TTS FastAPI Server (uses `infer_wav()`)
- **Phase 5**: Telecom TTS WebSocket Server (uses `infer_chunked()`)

---

**Status:** ✅ Complete  
**Last Updated:** November 22, 2025

