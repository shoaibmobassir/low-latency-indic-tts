"""
FastAPI Router for Web TTS API
Defines REST and WebSocket endpoints for TTS generation.
"""

import base64
import io
import json
import logging
import time
from typing import Literal

import numpy as np
import soundfile as sf
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import Response

from backend.common.config import USE_CASE_WEB_UI, DEFAULT_SAMPLE_RATE, ENABLE_CHUNK_METADATA
from backend.common.tts_engine import TTSEngine
from backend.web_tts.dependencies import (
    get_tts_engine,
    map_model_to_engine_type,
    validate_language,
    validate_model_choice,
)
from backend.web_tts.schemas import (
    ErrorResponse,
    TTSRequest,
    TTSResponse,
    WebSocketEndMessage,
    WebSocketMessage,
)
from backend.web_tts.metrics import LatencyMetrics, latency_tracker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["TTS"])


@router.post("/tts", response_model=TTSResponse)
async def generate_tts(
    request: TTSRequest,
    engine: TTSEngine = Depends(get_tts_engine)
) -> TTSResponse:
    """
    Generate complete TTS audio and return as base64-encoded WAV.
    
    Args:
        request: TTS request with text, language, and model
        engine: TTS engine instance
        
    Returns:
        TTSResponse with base64 audio and metadata
        
    Raises:
        HTTPException: If generation fails
    """
    total_start_time = time.time()
    
    try:
        # Validate inputs
        validation_start = time.time()
        lang = validate_language(request.lang)
        model = validate_model_choice(request.model)
        
        
        model_type = map_model_to_engine_type(model)
        validation_time = (time.time() - validation_start) * 1000
        
        logger.info(
            f"[TTS-REST] text_length={len(request.text)} "
            f"model={model} lang={lang}"
        )
        
        # Generate audio
        inference_start = time.time()
        try:
            waveform, sample_rate = engine.infer_wav(
                text=request.text,
                language=lang,
                use_case=USE_CASE_WEB_UI,
                model_type=model_type
            )
        except Exception as e:
            logger.error(f"[TTS-REST] Inference failed: {e}")
            raise
        
        # Validate inference results
        if waveform is None or len(waveform) == 0:
            raise ValueError("Inference returned empty waveform")
        if sample_rate is None or sample_rate <= 0:
            raise ValueError(f"Invalid sample rate from inference: {sample_rate}")
        
        inference_time = (time.time() - inference_start) * 1000
        
        # Convert to WAV bytes
        encoding_start = time.time()
        wav_buffer = io.BytesIO()
        sf.write(wav_buffer, waveform, sample_rate, format='WAV')
        wav_bytes = wav_buffer.getvalue()
        
        # Encode to base64
        audio_base64 = base64.b64encode(wav_bytes).decode('utf-8')
        encoding_time = (time.time() - encoding_start) * 1000
        
        # Calculate duration
        duration_ms = (len(waveform) / sample_rate) * 1000
        total_time = (time.time() - total_start_time) * 1000
        
        # Record metrics
        metrics = LatencyMetrics(
            total_time_ms=total_time,
            inference_time_ms=inference_time,
            chunking_time_ms=0.0,  # REST doesn't chunk
            network_time_ms=0.0,  # Not measured here
            text_length=len(request.text),
            audio_duration_ms=duration_ms,
            model=model,
            device=engine.device_type,
            language=lang,
            use_case="web_ui"
        )
        latency_tracker.record(metrics)
        
        logger.info(
            f"[TTS-REST] text_length={len(request.text)} "
            f"model={model} total={total_time:.1f}ms "
            f"inference={inference_time:.1f}ms encoding={encoding_time:.1f}ms "
            f"audio_duration={duration_ms:.1f}ms RTF={metrics.real_time_factor:.3f}"
        )
        
        return TTSResponse(
            audio_base64=audio_base64,
            sample_rate=sample_rate,
            model=model,
            device=engine.device_type,
            duration_ms=duration_ms,
            text_length=len(request.text),
            inference_time_ms=inference_time,
            total_time_ms=total_time,
            real_time_factor=metrics.real_time_factor
        )
        
    except ValueError as e:
        logger.error(f"[TTS-REST] Validation error: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[TTS-REST] Generation failed: {e}")
        from fastapi import HTTPException
        error_msg = str(e)
        # Provide more helpful error messages
        if "empty input" in error_msg.lower() or "negative output size" in error_msg.lower():
            error_msg = (
                f"Text processing failed. This usually means:\n"
                f"1. The text language doesn't match the selected language\n"
                f"2. The text contains unsupported characters\n"
                f"3. The text is empty or invalid\n"
                f"Original error: {error_msg}"
            )
        raise HTTPException(status_code=500, detail=error_msg)


@router.websocket("/ws/stream_tts")
async def stream_tts(websocket: WebSocket):
    """
    WebSocket endpoint for streaming TTS audio chunks.
    
    Protocol:
    1. Client sends JSON message with text, lang, model, chunk_ms
    2. Server streams binary audio chunks (WAV format)
    3. Server sends final JSON message with metadata
    """
    await websocket.accept()
    
    try:
        # Receive initial message
        data = await websocket.receive_json()
        message = WebSocketMessage(**data)
        
        # Validate inputs
        lang = validate_language(message.lang)
        model = validate_model_choice(message.model)
        
        
        model_type = map_model_to_engine_type(model)
        chunk_ms = message.chunk_ms
        
        logger.info(
            f"[TTS-WS] text=\"{message.text[:50]}...\" "
            f"lang={lang} model={model} chunk_ms={chunk_ms}"
        )
        
        # Get engine
        engine = get_tts_engine()
        
        # Use packet-based streaming for constant latency (independent of text size)
        total_start_time = time.time()
        server_received_ts = total_start_time  # When server received the request
        chunk_count = 0
        first_chunk_sent = False
        first_chunk_time: float | None = None
        total_audio_samples = 0
        sample_rate = DEFAULT_SAMPLE_RATE
        inference_start = time.time()
        
        try:
            # Stream audio packets with constant latency
            # Text is split into small packets (5 words), each processed independently
            # First packet latency is constant regardless of total text size
            # IMPORTANT: Send each chunk immediately as it's generated (no buffering)
            logger.info(
                f"[TTS-WS] Starting packet streaming: text_length={len(message.text)}, "
                f"model={model}, language={lang}"
            )
            
            packet_start = time.time()
            for chunk_bytes in engine.infer_chunked(
                text=message.text,
                language=lang,
                use_case=USE_CASE_WEB_UI,
                chunk_ms=chunk_ms,
                model_type=model_type,
                low_latency=True,
                streaming=True  # Enable packet-based streaming
            ):
                # Instrumentation: Record chunk generation and send timestamps
                server_chunk_gen_ts = time.time()
                server_chunk_sent_ts = None
                
                # CRITICAL: Send immediately - don't buffer!
                # Track first chunk latency (constant regardless of text size)
                if not first_chunk_sent:
                    first_chunk_start = time.time()
                    
                    # Send chunk metadata if enabled (for latency measurement)
                    if ENABLE_CHUNK_METADATA:
                        chunk_meta = {
                            "type": "chunk_meta",
                            "server_received_ts": server_received_ts,
                            "chunk_index": chunk_count,
                            "server_chunk_gen_ts": server_chunk_gen_ts,
                            "is_first_chunk": True
                        }
                        await websocket.send_text(json.dumps(chunk_meta))
                    
                    await websocket.send_bytes(chunk_bytes)
                    server_chunk_sent_ts = time.time()
                    first_chunk_time = (server_chunk_sent_ts - first_chunk_start) * 1000
                    chunk_count += 1
                    first_chunk_sent = True
                    packet_time = (server_chunk_gen_ts - packet_start) * 1000
                    logger.info(
                        f"[TTS-WS] ✅ First packet sent in {first_chunk_time:.1f}ms "
                        f"(packet_gen={packet_time:.1f}ms, text_length={len(message.text)}, "
                        f"constant latency achieved)"
                    )
                else:
                    # Send chunk metadata if enabled
                    if ENABLE_CHUNK_METADATA:
                        chunk_meta = {
                            "type": "chunk_meta",
                            "server_received_ts": server_received_ts,
                            "chunk_index": chunk_count,
                            "server_chunk_gen_ts": server_chunk_gen_ts,
                            "is_first_chunk": False
                        }
                        await websocket.send_text(json.dumps(chunk_meta))
                    
                    # Send subsequent chunks immediately (no buffering)
                    await websocket.send_bytes(chunk_bytes)
                    server_chunk_sent_ts = time.time()
                    chunk_count += 1
                    
                # Estimate audio duration from chunk size
                # Each chunk is a WAV file, estimate samples from bytes
                # WAV header is ~44 bytes, rest is audio data (2 bytes per sample for int16)
                if len(chunk_bytes) > 44:
                    estimated_samples = (len(chunk_bytes) - 44) // 2
                    total_audio_samples += estimated_samples
                    
            inference_time = (time.time() - inference_start) * 1000
            logger.info(
                f"[TTS-WS] Packet streaming complete: {chunk_count} chunks, "
                f"inference={inference_time:.1f}ms, samples={total_audio_samples}"
            )
                    
        except Exception as e:
            logger.error(f"[TTS-WS] Packet streaming failed: {e}", exc_info=True)
            raise
        
        # Calculate metrics
        total_time = (time.time() - total_start_time) * 1000
        inference_time = (time.time() - inference_start) * 1000 if 'inference_start' in locals() else total_time * 0.8
        
        if total_audio_samples > 0 and sample_rate > 0:
            duration_ms = (total_audio_samples / sample_rate) * 1000
        else:
            # Fallback estimation
            duration_ms = chunk_count * chunk_ms  # Rough estimate
        
        # Record metrics
        # For packet streaming, inference time is distributed across packets
        metrics = LatencyMetrics(
            total_time_ms=total_time,
            inference_time_ms=inference_time,
            chunking_time_ms=0.0,  # Chunking happens during packet generation
            network_time_ms=0.0,  # Not measured here
            text_length=len(message.text),
            audio_duration_ms=duration_ms if duration_ms > 0 else None,
            model=model,
            device=engine.device_type,
            language=lang,
            use_case="web_ui"
        )
        latency_tracker.record(metrics)
        
        # Send end message with latency info
        end_message = WebSocketEndMessage(
            event="end",
            duration_ms=duration_ms,
            chunks_sent=chunk_count,
            model=model,
            device=engine.device_type,
            inference_time_ms=metrics.inference_time_ms,
            total_time_ms=total_time,
            real_time_factor=metrics.real_time_factor,
            first_chunk_time_ms=first_chunk_time if first_chunk_sent else None,
            chunking_time_ms=0.0  # Packet-based: no separate chunking phase
        )
        await websocket.send_json(end_message.dict())
        
        log_msg = (
            f"[TTS-WS] text=\"{message.text[:50]}...\" "
            f"lang={lang} model={model} total={total_time:.1f}ms "
            f"chunks={chunk_count} RTF={metrics.real_time_factor:.3f} "
            f"text_length={len(message.text)}"
        )
        if first_chunk_sent and first_chunk_time:
            log_msg += f" first_packet={first_chunk_time:.1f}ms (constant latency)"
        logger.info(log_msg)
        
    except WebSocketDisconnect:
        logger.info("[TTS-WS] Client disconnected")
    except ValueError as e:
        logger.error(f"[TTS-WS] Validation error: {e}")
        error_msg = str(e)
        await websocket.send_json({
            "error": error_msg,
            "code": "validation_error"
        })
    except Exception as e:
        logger.error(f"[TTS-WS] Generation failed: {e}")
        error_msg = str(e)
        # Provide more helpful error messages
        if "empty input" in error_msg.lower() or "negative output size" in error_msg.lower():
            error_msg = (
                f"Text processing failed. This usually means:\n"
                f"1. The text language doesn't match the selected language\n"
                f"2. The text contains unsupported characters\n"
                f"3. The text is empty or invalid\n"
                f"Original error: {error_msg}"
            )
        await websocket.send_json({
            "error": error_msg,
            "code": "generation_error"
        })


@router.get("/health")
async def health_check(engine: TTSEngine = Depends(get_tts_engine)):
    """
    Health check endpoint.
    
    Returns:
        Health status and loaded models
    """
    models_loaded = {
        "mms_tts": list(engine.mms_tts_models.keys()),
        "indictts": engine.indictts_loaded
    }
    
    return {
        "status": "healthy",
        "device": engine.device_type,
        "models_loaded": models_loaded
    }


@router.get("/metrics")
async def get_metrics():
    """
    Get latency metrics and statistics.
    
    Returns:
        Aggregated latency statistics and per-model breakdown
    """
    stats = latency_tracker.get_stats()
    
    # Get per-model stats
    model_stats = {}
    for model in ["mms", "indic"]:
        model_stat = latency_tracker.get_model_stats(model)
        if model_stat:
            model_stats[model] = model_stat
    
    return {
        "overall": stats,
        "by_model": model_stats,
        "recent_requests": len(latency_tracker.metrics_history)
    }

