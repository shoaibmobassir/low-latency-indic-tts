"""
ONNX Runtime Optimization for TTS Models
Converts PyTorch models to ONNX for faster inference with <100ms latency.
"""

import logging
import os
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import torch

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    logging.warning("[ONNX] onnxruntime not available")

logger = logging.getLogger(__name__)


class ONNXOptimizer:
    """
    Optimizes TTS models using ONNX Runtime for faster inference.
    
    Provides:
    - Model conversion to ONNX format
    - GPU-accelerated inference via ONNX Runtime
    - Batch processing support
    - Lower latency than standard PyTorch
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize ONNX optimizer.
        
        Args:
            cache_dir: Directory to cache ONNX models
        """
        self.cache_dir = cache_dir or Path.home() / ".cache" / "tts_onnx"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.onnx_sessions: dict[str, ort.InferenceSession] = {}
        
        if not ONNX_AVAILABLE:
            logger.warning("[ONNX] ONNX Runtime not available, using PyTorch")
    
    def get_providers(self) -> list[str]:
        """
        Get available ONNX Runtime providers.
        
        Returns:
            List of available providers (CUDA, CPU, etc.)
        """
        if not ONNX_AVAILABLE:
            return []
        
        providers = ort.get_available_providers()
        logger.info(f"[ONNX] Available providers: {providers}")
        return providers
    
    def optimize_model(
        self,
        model: torch.nn.Module,
        model_name: str,
        input_shape: Tuple[int, ...],
        device: str = "cpu"
    ) -> Optional[ort.InferenceSession]:
        """
        Convert PyTorch model to ONNX and create inference session.
        
        Args:
            model: PyTorch model to convert
            model_name: Name for caching
            input_shape: Input tensor shape
            device: Device to use ('cpu', 'cuda', 'mps')
            
        Returns:
            ONNX Runtime inference session or None if conversion fails
        """
        if not ONNX_AVAILABLE:
            return None
        
        onnx_path = self.cache_dir / f"{model_name}.onnx"
        
        # Check if ONNX model already exists
        if onnx_path.exists():
            logger.info(f"[ONNX] Loading cached model: {onnx_path}")
            return self._load_session(onnx_path, device)
        
        # Convert to ONNX
        try:
            logger.info(f"[ONNX] Converting {model_name} to ONNX...")
            model.eval()
            
            # Create dummy input
            dummy_input = torch.randn(input_shape)
            if device == "cuda" and torch.cuda.is_available():
                dummy_input = dummy_input.cuda()
                model = model.cuda()
            elif device == "mps" and torch.backends.mps.is_available():
                dummy_input = dummy_input.to("mps")
                model = model.to("mps")
            
            # Export to ONNX
            torch.onnx.export(
                model,
                dummy_input,
                str(onnx_path),
                export_params=True,
                opset_version=13,
                do_constant_folding=True,
                input_names=['input'],
                output_names=['output'],
                dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
            )
            
            logger.info(f"[ONNX] Model converted: {onnx_path}")
            return self._load_session(onnx_path, device)
            
        except Exception as e:
            logger.error(f"[ONNX] Conversion failed: {e}")
            return None
    
    def _load_session(self, onnx_path: Path, device: str) -> Optional[ort.InferenceSession]:
        """
        Load ONNX model as inference session.
        
        Args:
            onnx_path: Path to ONNX model
            device: Device to use
            
        Returns:
            Inference session
        """
        if not ONNX_AVAILABLE:
            return None
        
        providers = []
        if device == "cuda":
            if "CUDAExecutionProvider" in ort.get_available_providers():
                providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
            else:
                providers = ["CPUExecutionProvider"]
        else:
            providers = ["CPUExecutionProvider"]
        
        try:
            session = ort.InferenceSession(
                str(onnx_path),
                providers=providers
            )
            logger.info(f"[ONNX] Session created with providers: {providers}")
            return session
        except Exception as e:
            logger.error(f"[ONNX] Failed to create session: {e}")
            return None


