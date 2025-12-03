"""
Latency Metrics and Performance Monitoring
Tracks and logs TTS inference latency for optimization.
"""

import logging
import time
from dataclasses import dataclass
from typing import Optional
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class LatencyMetrics:
    """Latency metrics for a single TTS request."""
    total_time_ms: float
    inference_time_ms: float
    chunking_time_ms: float
    network_time_ms: float
    text_length: int
    audio_duration_ms: float | None
    model: str
    device: str
    language: str
    use_case: str
    
    @property
    def real_time_factor(self) -> float:
        """RTF = inference_time / audio_duration"""
        if self.audio_duration_ms is None or self.audio_duration_ms == 0:
            return 0.0
        if self.inference_time_ms is None or self.inference_time_ms == 0:
            return 0.0
        return self.inference_time_ms / self.audio_duration_ms
    
    @property
    def throughput_chars_per_sec(self) -> float:
        """Characters processed per second."""
        if self.inference_time_ms is None or self.inference_time_ms == 0:
            return 0.0
        return (self.text_length * 1000) / self.inference_time_ms
    
    def to_dict(self) -> dict:
        """Convert to dictionary for logging/API."""
        return {
            "total_time_ms": round(self.total_time_ms, 2) if self.total_time_ms is not None else 0.0,
            "inference_time_ms": round(self.inference_time_ms, 2) if self.inference_time_ms is not None else 0.0,
            "chunking_time_ms": round(self.chunking_time_ms, 2) if self.chunking_time_ms is not None else 0.0,
            "network_time_ms": round(self.network_time_ms, 2) if self.network_time_ms is not None else 0.0,
            "text_length": self.text_length,
            "audio_duration_ms": round(self.audio_duration_ms, 2) if self.audio_duration_ms is not None else 0.0,
            "real_time_factor": round(self.real_time_factor, 3),
            "throughput_chars_per_sec": round(self.throughput_chars_per_sec, 2),
            "model": self.model,
            "device": self.device,
            "language": self.language,
            "use_case": self.use_case,
        }


class LatencyTracker:
    """Tracks latency metrics over time."""
    
    def __init__(self, max_history: int = 100):
        self.metrics_history: deque = deque(maxlen=max_history)
        self.total_requests = 0
    
    def record(self, metrics: LatencyMetrics):
        """Record a new latency measurement."""
        self.metrics_history.append(metrics)
        self.total_requests += 1
        
        # Log detailed metrics
        logger.info(
            f"[LATENCY] Model={metrics.model} Device={metrics.device} "
            f"Text={metrics.text_length}chars "
            f"Total={metrics.total_time_ms:.1f}ms "
            f"Inference={metrics.inference_time_ms:.1f}ms "
            f"RTF={metrics.real_time_factor:.3f} "
            f"Throughput={metrics.throughput_chars_per_sec:.1f}chars/s"
        )
    
    def get_stats(self) -> dict:
        """Get aggregated statistics."""
        if not self.metrics_history:
            return {
                "total_requests": 0,
                "avg_total_time_ms": 0,
                "avg_inference_time_ms": 0,
                "avg_rtf": 0,
                "avg_throughput_chars_per_sec": 0,
            }
        
        metrics_list = list(self.metrics_history)
        
        return {
            "total_requests": self.total_requests,
            "avg_total_time_ms": sum(m.total_time_ms for m in metrics_list) / len(metrics_list),
            "avg_inference_time_ms": sum(m.inference_time_ms for m in metrics_list) / len(metrics_list),
            "avg_chunking_time_ms": sum(m.chunking_time_ms for m in metrics_list) / len(metrics_list),
            "avg_rtf": sum(m.real_time_factor for m in metrics_list) / len(metrics_list),
            "avg_throughput_chars_per_sec": sum(m.throughput_chars_per_sec for m in metrics_list) / len(metrics_list),
            "min_inference_time_ms": min(m.inference_time_ms for m in metrics_list),
            "max_inference_time_ms": max(m.inference_time_ms for m in metrics_list),
        }
    
    def get_model_stats(self, model: str) -> dict:
        """Get statistics for a specific model."""
        model_metrics = [m for m in self.metrics_history if m.model == model]
        if not model_metrics:
            return {}
        
        return {
            "model": model,
            "count": len(model_metrics),
            "avg_inference_time_ms": sum(m.inference_time_ms for m in model_metrics) / len(model_metrics),
            "avg_rtf": sum(m.real_time_factor for m in model_metrics) / len(model_metrics),
        }


# Global latency tracker instance
latency_tracker = LatencyTracker()

