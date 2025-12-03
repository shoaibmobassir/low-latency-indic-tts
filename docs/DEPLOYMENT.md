# 🚀 Deployment Guide

## Environment Overview

This project supports **dual-environment deployment**:

1. **Local Development/Testing:** Apple Silicon Mac (M1/M2/M3) with MPS acceleration
2. **Production Deployment:** NVIDIA H100 GPU with CUDA acceleration

---

## Local Development Environment (Mac)

### Hardware
- **Device:** Apple Silicon Mac (M1/M2/M3)
- **GPU:** Integrated Apple GPU (Metal Performance Shaders)
- **Acceleration:** MPS (Metal Performance Shaders) via PyTorch

### Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (CPU/MPS compatible)
pip install -r backend/models/requirements.txt

# Test device detection
python -c "from backend.common.device_utils import log_device_info; log_device_info()"
```

### Device Detection
The system automatically detects and uses:
- **MPS** (Apple Silicon GPU) when available
- **CPU** as fallback

### Testing
All test scripts automatically use MPS when available:
```bash
# MMS-TTS test (uses MPS on Mac)
python backend/models/test_mms_tts.py --text "નમસ્તે" --lang gu

# XTTS-v2 test (uses MPS on Mac)
python backend/models/test_xtts.py --text "Hello" --lang en
```

---

## Production Deployment Environment (H100 GPU)

### Hardware
- **Device:** NVIDIA H100 GPU
- **CUDA:** Latest CUDA version
- **Acceleration:** CUDA via PyTorch

### Setup
```bash
# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install other dependencies
pip install -r backend/models/requirements.txt

# Verify CUDA availability
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

### Device Detection
The system automatically detects and uses:
- **CUDA** (NVIDIA GPU) when available (priority)
- **MPS** (Apple Silicon) if CUDA not available
- **CPU** as final fallback

### Deployment Configuration

#### Docker Deployment
```dockerfile
# Use NVIDIA CUDA base image
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Install Python and dependencies
RUN apt-get update && apt-get install -y python3.11 python3-pip

# Install PyTorch with CUDA support
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install project dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . /app
WORKDIR /app

# Expose ports
EXPOSE 8050 3050
```

#### Environment Variables
```bash
# GPU device selection (optional, auto-detected)
CUDA_VISIBLE_DEVICES=0

# Model paths
MMS_TTS_MODEL_PATH=/models/mms-tts
PIPER_MODEL_PATH=/models/piper
```

---

## Device Detection Priority

The system uses the following priority order:

1. **CUDA** (NVIDIA GPU) - Highest priority for production
2. **MPS** (Apple Silicon) - For local development
3. **CPU** - Fallback option

This ensures:
- **Local testing** works seamlessly on Mac with MPS
- **Production deployment** automatically uses CUDA on H100
- **No code changes** needed between environments

---

## Performance Expectations

### Local Development (M1 Mac)
- **MMS-TTS:** ~200-500ms per sentence (MPS)
- **Piper TTS:** ~50-100ms per sentence (CPU)
- **XTTS-v2:** ~500-1000ms per sentence (MPS)

### Production (H100 GPU)
- **MMS-TTS:** ~50-100ms per sentence (CUDA)
- **Piper TTS:** ~20-50ms per sentence (CUDA)
- **XTTS-v2:** ~100-200ms per sentence (CUDA)

---

## Verification

### Check Device Detection
```python
from backend.common.device_utils import get_device_info, log_device_info

# Get device information
info = get_device_info()
print(f"Optimal Device: {info['optimal_device']}")
print(f"Device Type: {info['device_type']}")

# Log detailed info
log_device_info()
```

### Test GPU Acceleration
```bash
# Test MMS-TTS with device detection
python backend/models/test_mms_tts.py --text "Test" --lang gu

# Check logs for device type
# Should show: "Using NVIDIA GPU (CUDA)" on H100
# Should show: "Using Apple Silicon GPU (MPS)" on Mac
```

---

## Troubleshooting

### CUDA Not Detected on H100
1. Verify CUDA installation: `nvidia-smi`
2. Check PyTorch CUDA build: `python -c "import torch; print(torch.cuda.is_available())"`
3. Verify CUDA version compatibility

### MPS Not Available on Mac
1. Check macOS version (MPS requires macOS 12.3+)
2. Verify PyTorch MPS support: `python -c "import torch; print(torch.backends.mps.is_available())"`
3. Update PyTorch if needed

### Performance Issues
- **Local (Mac):** MPS provides good acceleration, but expect slower than H100
- **Production (H100):** Should see significant speedup with CUDA
- **CPU Fallback:** Much slower, use only if GPU unavailable

---

## Notes

- **No code changes** needed when switching between Mac and H100
- Device detection is **automatic** and **transparent**
- All models work with both MPS and CUDA
- CPU fallback ensures compatibility even without GPU

---

**Last Updated:** November 22, 2025

