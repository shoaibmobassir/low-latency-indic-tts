"""
FastAPI Dependencies for Web TTS API
Provides dependency injection for TTS engine and validation functions.
"""

import logging
from typing import Literal

from backend.common.tts_engine import TTSEngine, USE_CASE_WEB_UI

logger = logging.getLogger(__name__)

# Global TTS engine instance
_tts_engine: TTSEngine | None = None


def get_tts_engine() -> TTSEngine:
    """
    Get or create the global TTS engine instance.
    
    Returns:
        TTSEngine instance
    """
    global _tts_engine
    
    if _tts_engine is None:
        logger.info("[TTS] Initializing global TTS engine...")
        _tts_engine = TTSEngine()
        
        # Pre-load models for both languages
        try:
            logger.info("[TTS] Pre-loading MMS-TTS models...")
            _tts_engine.load_mms_tts("gu")
            _tts_engine.load_mms_tts("mr")
        except Exception as e:
            logger.warning(f"[TTS] Failed to pre-load MMS-TTS: {e}")
        
        # Warm up GPU if available
        try:
            _tts_engine.warmup_gpu()
        except Exception as e:
            logger.warning(f"[TTS] GPU warmup failed: {e}")
        
        logger.info("[TTS] TTS engine initialized and ready")
    
    return _tts_engine


def validate_language(lang: str) -> Literal["gu", "mr"]:
    """
    Validate language code.
    
    Args:
        lang: Language code to validate
        
    Returns:
        Validated language code
        
    Raises:
        ValueError: If language is invalid
    """
    if lang not in ["gu", "mr"]:
        raise ValueError(f"Invalid language: {lang}. Must be 'gu' or 'mr'")
    return lang


def validate_model_choice(model: str) -> Literal["mms", "indic"]:
    """
    Validate model choice.
    
    Args:
        model: Model name to validate
        
    Returns:
        Validated model name
        
    Raises:
        ValueError: If model is invalid
    """
    if model not in ["mms", "indic"]:
        raise ValueError(f"Invalid model: {model}. Must be 'mms' or 'indic'")
    return model


def map_model_to_engine_type(model: str) -> Literal["mms_tts", "indictts"]:
    """
    Map API model name to engine model type.
    
    Args:
        model: API model name ('mms', 'indic')
        
    Returns:
        Engine model type
    """
    mapping = {
        "mms": "mms_tts",
        "indic": "indictts"
    }
    return mapping.get(model, "mms_tts")

