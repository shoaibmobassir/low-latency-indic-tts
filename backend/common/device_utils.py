"""
Device Detection Utilities
Supports both MPS (Apple Silicon) for local testing and CUDA (NVIDIA) for deployment.
"""

import logging
from typing import Literal

import torch

logger = logging.getLogger(__name__)

DeviceType = Literal["cuda", "mps", "cpu"]


def get_optimal_device() -> tuple[DeviceType, str]:
    """
    Detect and return the optimal device for PyTorch operations.
    
    Priority:
    1. CUDA (NVIDIA GPU) - for deployment (H100, etc.)
    2. MPS (Apple Silicon) - for local testing (M1/M2/M3 Mac)
    3. CPU - fallback
    
    Returns:
        Tuple of (device_type, device_string)
        - device_type: "cuda", "mps", or "cpu"
        - device_string: PyTorch device string (e.g., "cuda:0", "mps", "cpu")
    """
    # Check for CUDA (NVIDIA GPU) - Priority 1 (for deployment)
    if torch.cuda.is_available():
        device_count = torch.cuda.device_count()
        device_name = torch.cuda.get_device_name(0) if device_count > 0 else "Unknown"
        logger.info(f"✅ CUDA available: {device_name} ({device_count} device(s))")
        return "cuda", "cuda:0"
    
    # Check for MPS (Apple Silicon) - Priority 2 (for local testing)
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        logger.info("✅ MPS available: Apple Silicon GPU (for local testing)")
        return "mps", "mps"
    
    # Fallback to CPU
    logger.warning("⚠️  No GPU available. Using CPU (slower performance).")
    return "cpu", "cpu"


def get_device_info() -> dict:
    """
    Get detailed information about available devices.
    
    Returns:
        Dictionary with device information
    """
    info = {
        "cuda_available": torch.cuda.is_available(),
        "mps_available": hasattr(torch.backends, "mps") and torch.backends.mps.is_available() if hasattr(torch.backends, "mps") else False,
        "optimal_device": None,
        "device_type": None,
        "device_details": {}
    }
    
    if torch.cuda.is_available():
        info["optimal_device"] = "cuda:0"
        info["device_type"] = "cuda"
        info["device_details"] = {
            "device_count": torch.cuda.device_count(),
            "device_name": torch.cuda.get_device_name(0),
            "cuda_version": torch.version.cuda,
        }
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        info["optimal_device"] = "mps"
        info["device_type"] = "mps"
        info["device_details"] = {
            "platform": "Apple Silicon",
            "metal_support": True,
        }
    else:
        info["optimal_device"] = "cpu"
        info["device_type"] = "cpu"
        info["device_details"] = {
            "platform": "CPU only",
        }
    
    return info


def log_device_info():
    """Log device information for debugging."""
    info = get_device_info()
    logger.info("=" * 50)
    logger.info("Device Detection Results:")
    logger.info(f"  CUDA Available: {info['cuda_available']}")
    logger.info(f"  MPS Available: {info['mps_available']}")
    logger.info(f"  Optimal Device: {info['optimal_device']}")
    logger.info(f"  Device Type: {info['device_type']}")
    if info["device_details"]:
        logger.info(f"  Details: {info['device_details']}")
    logger.info("=" * 50)

