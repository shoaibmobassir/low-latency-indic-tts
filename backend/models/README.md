# Model Testing Scripts

This directory contains offline testing scripts for TTS models used in the Gujarati & Marathi TTS System.

## Scripts

### `test_mms_tts.py` ⭐ (Facebook MMS-TTS for Gujarati/Marathi)
Tests Facebook MMS-TTS (VITS) model for Gujarati and Marathi TTS generation.
- Uses `facebook/mms-tts-guj` for Gujarati
- Uses `facebook/mms-tts-mar` for Marathi
- High-quality neural TTS with VITS architecture
- GPU-accelerated inference

### `test_indictts.py` (Alternative for Gujarati/Marathi)
Tests IndicTTS for Gujarati and Marathi TTS generation.
- Uses gTTS (Google TTS) as fallback for immediate testing
- Supports both Gujarati and Marathi
- Ready for AI4Bharat Indic-TTS model integration

### `test_xtts.py`
Tests Coqui XTTS-v2 model for high-quality Web UI TTS.
- **Note:** XTTS-v2 supports Hindi but NOT Gujarati/Marathi
- Use for Hindi/English TTS only

### `test_piper.py`
Tests Piper TTS model for low-latency Telecom API TTS.

## Installation

### 1. Activate Virtual Environment

```bash
cd /Users/adityabisen/Desktop/tts_service
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### 2. Install XTTS-v2 Dependencies

```bash
pip install TTS torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
```

**Note:** Replace `cu121` with your CUDA version if different:
- CUDA 11.8: `cu118`
- CUDA 12.1: `cu121`
- CPU only: Remove `--extra-index-url` flag

### 3. Install Piper TTS Dependencies

```bash
pip install onnxruntime-gpu soundfile numpy
```

**Note:** For CPU-only systems, use `onnxruntime` instead of `onnxruntime-gpu`.

### 4. Install All Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### MMS-TTS Testing (Gujarati/Marathi) ⭐

```bash
# Test Gujarati
python test_mms_tts.py --text "નમસ્તે, હું ગુજરાતી ભાષામાં બોલું છું." --lang gu

# Test Marathi
python test_mms_tts.py --text "नमस्कार, मी मराठी भाषेत बोलतो." --lang mr

# Custom output filename
python test_mms_tts.py --text "નમસ્તે" --lang gu --output custom_name.wav
```

**Note:** MMS-TTS provides high-quality neural TTS. Models are downloaded from HuggingFace on first use.

### IndicTTS Testing (Alternative for Gujarati/Marathi)

```bash
# Test Gujarati
python test_indictts.py --text "નમસ્તે" --lang gu

# Test Marathi
python test_indictts.py --text "नमस्कार" --lang mr
```

**Note:** Currently uses gTTS (Google TTS) as fallback. For production, integrate AI4Bharat Indic-TTS models.

### XTTS-v2 Testing (Hindi/English only)

```bash
# Test Hindi (Gujarati/Marathi NOT supported)
python test_xtts.py --text "नमस्ते" --lang hi

# With voice cloning (optional)
python test_xtts.py --text "Hello" --lang en --speaker /path/to/reference.wav
```

### Piper TTS Testing

**First, download Piper models:**

```bash
# Download Gujarati model (example - adjust URL as needed)
# Models available at: https://github.com/rhasspy/piper/releases
# Or use piper download tool if available
```

```bash
# Test Gujarati
python test_piper.py --text "નમસ્તે" --lang gu --model /path/to/piper_gu_model/

# Test Marathi
python test_piper.py --text "नमस्कार" --lang mr --model /path/to/piper_mr_model/
```

## Output

All generated WAV files are saved to `backend/models/output/`:
- `mms_tts_gu.wav` - MMS-TTS Gujarati output
- `mms_tts_mr.wav` - MMS-TTS Marathi output
- `indictts_gu.wav` - IndicTTS Gujarati output
- `indictts_mr.wav` - IndicTTS Marathi output
- `piper_gu.wav` - Piper Gujarati output
- `piper_mr.wav` - Piper Marathi output

## Model Paths

### MMS-TTS
- Default: Downloads from HuggingFace automatically
- Gujarati model: `facebook/mms-tts-guj`
- Marathi model: `facebook/mms-tts-mar`
- Cache location: `~/.cache/huggingface/hub/`

### XTTS-v2
- Default: Downloads from HuggingFace automatically
- Model name: `tts_models/multilingual/multi-dataset/xtts_v2`
- Cache location: `~/.local/share/tts/`

### Piper TTS
- Download from: https://github.com/rhasspy/piper/releases
- Or use: `python -m piper.download` (if piper-tts package installed)
- Required files per model:
  - `model.onnx`
  - `config.json`

## GPU Requirements

### Development Environment (Mac)
- **MMS-TTS**: Supports Apple Silicon GPU via MPS (Metal Performance Shaders)
- **XTTS-v2**: Uses CPU on Mac (TTS library limitation, but works)
- **Piper**: Uses CPU on Mac (ONNX Runtime MPS support limited)

### Production Deployment (H100 GPU)
- **MMS-TTS**: Supports NVIDIA GPU via CUDA for faster inference
- **XTTS-v2**: Requires CUDA-capable GPU (H100) for optimal performance
- **Piper**: Supports GPU via ONNX Runtime CUDA provider

**Note:** Device detection is automatic. The system will use:
1. **CUDA** (NVIDIA GPU) - for production deployment on H100
2. **MPS** (Apple Silicon) - for local testing on Mac
3. **CPU** - as fallback

See [Deployment Guide](../../docs/DEPLOYMENT.md) for details.

## Troubleshooting

### CUDA Not Available
- Check CUDA installation: `nvidia-smi`
- Verify PyTorch CUDA: `python -c "import torch; print(torch.cuda.is_available())"`
- For ONNX Runtime: Check providers: `python -c "import onnxruntime as ort; print(ort.get_available_providers())"`

### Model Download Issues
- XTTS-v2: Check internet connection and HuggingFace access
- Piper: Manually download models from GitHub releases

### Audio Generation Fails
- Verify model files are complete
- Check text encoding (UTF-8)
- Ensure output directory is writable

