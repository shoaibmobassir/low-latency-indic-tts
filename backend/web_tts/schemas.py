"""
Pydantic Schemas for Web TTS API
Defines request and response models for REST and WebSocket endpoints.
"""

import base64
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TTSRequest(BaseModel):
    """REST API request model for TTS generation."""
    
    text: str = Field(..., description="Text to convert to speech", min_length=1)
    lang: Literal["gu", "mr"] = Field(..., description="Language code: 'gu' for Gujarati, 'mr' for Marathi")
    model: Literal["mms", "indic"] = Field(
        default="mms",
        description="TTS model to use: 'mms' for MMS-TTS (high quality), 'indic' for IndicTTS (fallback)"
    )
    chunk_ms: int | None = Field(
        default=None,
        description="Chunk size in milliseconds for streaming (optional, used for WebSocket)"
    )
    
    @field_validator('chunk_ms', mode='before')
    @classmethod
    def coerce_chunk_ms(cls, v):
        """Coerce float to int for chunk_ms, or None if not provided."""
        if v is None:
            return None
        if isinstance(v, float):
            return int(v)
        return v


class TTSResponse(BaseModel):
    """REST API response model for TTS generation."""
    
    audio_base64: str = Field(..., description="Base64-encoded WAV audio data")
    sample_rate: int = Field(..., description="Audio sample rate in Hz")
    model: str = Field(..., description="Model used for generation")
    device: str = Field(..., description="Device used (cuda/mps/cpu)")
    duration_ms: float = Field(..., description="Audio duration in milliseconds")
    text_length: int = Field(..., description="Input text length in characters")
    inference_time_ms: float | None = Field(default=None, description="Inference time in milliseconds")
    total_time_ms: float | None = Field(default=None, description="Total processing time in milliseconds")
    real_time_factor: float | None = Field(default=None, description="Real-time factor (inference_time / audio_duration)")


class WebSocketMessage(BaseModel):
    """WebSocket message model for streaming TTS."""
    
    text: str = Field(..., description="Text to convert to speech", min_length=1)
    lang: Literal["gu", "mr"] = Field(..., description="Language code: 'gu' for Gujarati, 'mr' for Marathi")
    model: Literal["mms", "indic"] = Field(
        default="mms",
        description="TTS model to use: 'mms' for MMS-TTS (high quality), 'indic' for IndicTTS (fallback)"
    )
    chunk_ms: int = Field(
        default=40,
        description="Chunk size in milliseconds",
        ge=20,
        le=100
    )
    
    @field_validator('chunk_ms', mode='before')
    @classmethod
    def coerce_chunk_ms(cls, v):
        """Coerce float to int for chunk_ms."""
        if isinstance(v, float):
            return int(v)
        return v


class WebSocketEndMessage(BaseModel):
    """WebSocket end message model."""
    
    event: Literal["end"] = "end"
    duration_ms: float = Field(..., description="Total audio duration in milliseconds")
    chunks_sent: int = Field(..., description="Number of chunks sent")
    model: str = Field(..., description="Model used")
    device: str = Field(..., description="Device used")
    inference_time_ms: float | None = Field(default=None, description="Inference time in milliseconds")
    total_time_ms: float | None = Field(default=None, description="Total processing time in milliseconds")
    real_time_factor: float | None = Field(default=None, description="Real-time factor (inference_time / audio_duration)")
    first_chunk_time_ms: float | None = Field(default=None, description="Time to first chunk in milliseconds (low-latency metric)")
    chunking_time_ms: float | None = Field(default=None, description="Time spent chunking audio in milliseconds")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: dict | None = Field(default=None, description="Additional error details")

