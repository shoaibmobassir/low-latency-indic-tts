#!/usr/bin/env python3
"""
Patch script to fix PyTorch 2.9+ weights_only issue with XTTS-v2.
This adds safe globals before loading the model.
"""

import torch
import sys

def patch_torch_load():
    """Add safe globals for XTTS model loading."""
    try:
        from TTS.tts.configs.xtts_config import XttsConfig
        from TTS.tts.models.xtts import XttsAudioConfig
        torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig])
        print("✅ Added safe globals for XTTS model loading")
        return True
    except ImportError as e:
        print(f"⚠️  Could not import XTTS configs: {e}")
        return False

if __name__ == "__main__":
    if patch_torch_load():
        sys.exit(0)
    else:
        sys.exit(1)

