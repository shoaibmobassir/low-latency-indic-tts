#!/usr/bin/env python3
"""
Download Piper TTS models for Gujarati and Marathi.
"""

import os
import sys
import json
import tarfile
import urllib.request
from pathlib import Path

MODELS_DIR = Path(__file__).parent / "piper_models"
MODELS_DIR.mkdir(exist_ok=True)

# Piper model URLs (from HuggingFace or GitHub releases)
PIPER_MODELS = {
    "gu": {
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/gu/gu_IN/medium/gu_IN-medium.onnx",
        "config_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/gu/gu_IN/medium/gu_IN-medium.onnx.json",
        "name": "gu_IN-medium"
    },
    "mr": {
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/mr/mr_IN/medium/mr_IN-medium.onnx",
        "config_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/mr/mr_IN/medium/mr_IN-medium.onnx.json",
        "name": "mr_IN-medium"
    }
}


def download_file(url: str, output_path: Path):
    """Download a file from URL."""
    print(f"Downloading {url}...")
    try:
        urllib.request.urlretrieve(url, output_path)
        print(f"✅ Downloaded: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return False


def download_piper_model(language: str):
    """Download Piper model for a language."""
    if language not in PIPER_MODELS:
        print(f"❌ Unknown language: {language}")
        return False
    
    model_info = PIPER_MODELS[language]
    model_dir = MODELS_DIR / model_info["name"]
    model_dir.mkdir(exist_ok=True)
    
    model_file = model_dir / "model.onnx"
    config_file = model_dir / "config.json"
    
    # Download model file
    if not model_file.exists():
        if not download_file(model_info["url"], model_file):
            return False
    else:
        print(f"✅ Model file already exists: {model_file}")
    
    # Download config file
    if not config_file.exists():
        if not download_file(model_info["config_url"], config_file):
            # Try to create a basic config if download fails
            print("⚠️  Config download failed, creating basic config...")
            basic_config = {
                "audio": {
                    "sample_rate": 22050
                },
                "espeak": {
                    "voice": f"{language}_IN"
                }
            }
            with open(config_file, 'w') as f:
                json.dump(basic_config, f, indent=2)
            print(f"✅ Created basic config: {config_file}")
    else:
        print(f"✅ Config file already exists: {config_file}")
    
    print(f"✅ Model ready: {model_dir}")
    return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Download Piper TTS models")
    parser.add_argument(
        "--lang",
        type=str,
        choices=["gu", "mr", "all"],
        default="all",
        help="Language to download (default: all)"
    )
    
    args = parser.parse_args()
    
    languages = ["gu", "mr"] if args.lang == "all" else [args.lang]
    
    print("🚀 Downloading Piper TTS models...")
    print(f"   Output directory: {MODELS_DIR}\n")
    
    success = True
    for lang in languages:
        print(f"\n📦 Downloading {lang.upper()} model...")
        if not download_piper_model(lang):
            success = False
    
    if success:
        print("\n✅ All models downloaded successfully!")
        print(f"\nModel directories:")
        for lang in languages:
            model_name = PIPER_MODELS[lang]["name"]
            print(f"   {lang}: {MODELS_DIR / model_name}")
    else:
        print("\n⚠️  Some downloads failed. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

