#!/usr/bin/env python3
"""
Create a default speaker reference audio for XTTS-v2.
This generates a simple reference audio that can be used for voice cloning.
"""

import sys
from pathlib import Path
import torch
import torchaudio

# Monkey-patch torch.load
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

from TTS.api import TTS

def create_default_speaker(output_path: Path):
    """Create a default speaker reference audio using XTTS-v2."""
    print("Loading XTTS-v2 model...")
    import os
    os.environ['COQUI_TOS_AGREED'] = '1'
    
    tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
    
    # Generate a simple reference audio in English (most compatible)
    ref_text = "Hello, this is a reference audio for text to speech synthesis."
    print(f"Generating reference audio: {ref_text}")
    
    tts.tts_to_file(
        text=ref_text,
        file_path=str(output_path),
        language="en"
    )
    
    print(f"✅ Default speaker reference created: {output_path}")

if __name__ == "__main__":
    output_path = Path(__file__).parent / "default_speaker.wav"
    create_default_speaker(output_path)

