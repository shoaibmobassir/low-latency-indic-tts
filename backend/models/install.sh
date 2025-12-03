#!/bin/bash
# Installation script for Phase 1 model testing dependencies

set -e

echo "🚀 Installing Phase 1 Dependencies"
echo "=================================="

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Virtual environment not activated"
    echo "   Activate with: source ../../venv/bin/activate"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Detect CUDA version
CUDA_VERSION=""
if command -v nvcc &> /dev/null; then
    CUDA_VERSION=$(nvcc --version | grep "release" | sed 's/.*release \([0-9]\+\.[0-9]\+\).*/\1/')
    echo "✅ Detected CUDA version: $CUDA_VERSION"
fi

# Install PyTorch with CUDA support
echo ""
echo "📦 Installing PyTorch with CUDA support..."
if [ -n "$CUDA_VERSION" ]; then
    if [[ "$CUDA_VERSION" == 12.* ]]; then
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    elif [[ "$CUDA_VERSION" == 11.* ]]; then
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    else
        pip install torch torchvision torchaudio
    fi
else
    echo "⚠️  No CUDA detected, installing CPU-only PyTorch"
    pip install torch torchvision torchaudio
fi

# Install TTS (Coqui XTTS-v2)
echo ""
echo "📦 Installing Coqui TTS..."
pip install TTS

# Install ONNX Runtime GPU
echo ""
echo "📦 Installing ONNX Runtime GPU..."
pip install onnxruntime-gpu

# Install other dependencies
echo ""
echo "📦 Installing other dependencies..."
pip install soundfile numpy

# Verify installations
echo ""
echo "✅ Verifying installations..."
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
python -c "import TTS; print(f'TTS: {TTS.__version__}')"
python -c "import onnxruntime as ort; print(f'ONNX Runtime Providers: {ort.get_available_providers()}')"

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Download Piper models (if needed): https://github.com/rhasspy/piper/releases"
echo "  2. Test XTTS: python test_xtts.py --text 'નમસ્તે' --lang gu"
echo "  3. Test Piper: python test_piper.py --text 'નમસ્તે' --lang gu --model /path/to/model/"

