# Phase 3: Web TTS FastAPI Server

## Overview

Phase 3 implements a production-grade FastAPI server that exposes the Phase 2 TTS engine through REST and WebSocket endpoints for the Web UI.

## Architecture

### Server Structure

```
FastAPI App (port 8050)
├── CORS Middleware (allows frontend on port 3050)
├── Router (/api)
│   ├── POST /api/tts (REST endpoint)
│   ├── WebSocket /api/ws/stream_tts (streaming)
│   └── GET /api/health (health check)
└── Dependencies
    ├── get_tts_engine() (global engine instance)
    ├── validate_language()
    └── validate_model_choice()
```

### File Structure

```
backend/web_tts/
├── __init__.py          # Package initialization
├── main.py                 # FastAPI app and server startup
├── router.py              # API endpoints (REST + WebSocket)
├── schemas.py             # Pydantic models
└── dependencies.py        # Dependency injection
```

## API Endpoints

### REST Endpoint: POST /api/tts

**Purpose:** Generate complete TTS audio and return as base64-encoded WAV.

**Request:**
```json
{
  "text": "નમસ્તે",
  "lang": "gu",
  "model": "mms",
  "chunk_ms": 40
}
```

**Response:**
```json
{
  "audio_base64": "UklGRiQAAABXQVZFZm10...",
  "sample_rate": 16000,
  "model": "mms",
  "device": "mps",
  "duration_ms": 1234.5,
  "text_length": 6
}
```

**Example curl:**
```bash
curl -X POST "http://localhost:8050/api/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "નમસ્તે",
    "lang": "gu",
    "model": "mms"
  }'
```

### WebSocket Endpoint: /api/ws/stream_tts

**Purpose:** Stream TTS audio in real-time chunks.

**Protocol:**

1. **Client → Server (JSON):**
```json
{
  "text": "નમસ્તે",
  "lang": "gu",
  "model": "mms",
  "chunk_ms": 40
}
```

2. **Server → Client (Binary chunks):**
- Streams WAV-encoded audio chunks
- Each chunk is ~40ms of audio
- Binary format for efficient transmission

3. **Server → Client (Final JSON):**
```json
{
  "event": "end",
  "duration_ms": 1234.5,
  "chunks_sent": 31,
  "model": "mms",
  "device": "mps"
}
```

**Example WebSocket Client (Python):**
```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8050/api/ws/stream_tts"
    async with websockets.connect(uri) as websocket:
        # Send request
        await websocket.send(json.dumps({
            "text": "નમસ્તે",
            "lang": "gu",
            "model": "mms",
            "chunk_ms": 40
        }))
        
        # Receive chunks
        chunks = []
        while True:
            message = await websocket.recv()
            if isinstance(message, bytes):
                chunks.append(message)
            else:
                # Final message
                end_data = json.loads(message)
                print(f"Received {end_data['chunks_sent']} chunks")
                break

asyncio.run(test_websocket())
```

### Health Check: GET /api/health

**Purpose:** Check server status and loaded models.

**Response:**
```json
{
  "status": "healthy",
  "device": "mps",
  "models_loaded": {
    "mms_tts": ["gu", "mr"],
    "piper": ["gu", "mr"],
    "indictts": true
  }
}
```

## Model Selection

### Available Models

- **"mms"** - MMS-TTS (high quality, recommended for Web UI)
- **"piper"** - Piper TTS (low latency)
- **"indic"** - IndicTTS (gTTS fallback)

### Default Model

Default model for Web UI is **MMS-TTS** ("mms") for high-quality output.

## Audio Formats

### REST Endpoint

- **Format:** WAV (16-bit PCM)
- **Sample Rate:** Model-dependent (typically 16kHz)
- **Encoding:** Base64-encoded binary

### WebSocket Streaming

- **Format:** WAV chunks (raw PCM)
- **Chunk Size:** 40ms (configurable)
- **Sample Rate:** Model-dependent

## Logging

### Log Format

All requests are logged with standardized format:

**REST:**
```
[TTS-REST] text_length=<n> model=<mms/piper/indic> duration=<ms> audio_duration=<ms>
```

**WebSocket:**
```
[TTS-WS] text="<text>..." lang=<gu/mr> model=<mms/piper/indic> duration=<ms> chunks=<n>
```

### Example Logs

```
2025-11-22 10:00:00 [TTS-REST] text_length=6 model=mms duration=234.5ms audio_duration=1234.5ms
2025-11-22 10:00:01 [TTS-WS] text="નમસ્તે..." lang=gu model=mms duration=234.5ms chunks=31
```

## Error Handling

### Error Response Format

```json
{
  "error": "Error message",
  "code": "error_code",
  "details": {
    "field": "additional_info"
  }
}
```

### Common Error Codes

- `validation_error` - Invalid input parameters
- `generation_error` - TTS generation failed
- `model_not_loaded` - Model not available

## Startup Sequence

1. **Initialize FastAPI app**
2. **Setup CORS middleware** (allow frontend on port 3050)
3. **Pre-load models:**
   - MMS-TTS (Gujarati + Marathi)
   - Piper TTS (Gujarati + Marathi)
   - IndicTTS (gTTS fallback)
4. **Warm up GPU** (if available)
5. **Log loaded models and device info**

## Performance Targets

### Latency Targets

- **REST Endpoint:** <100ms (text → audio generation)
- **WebSocket First Chunk:** <100ms
- **Chunk Generation:** <5ms per chunk
- **Total Streaming:** Real-time (no buffering delays)

### Throughput

- **Concurrent Requests:** Support 10+ simultaneous users
- **WebSocket Connections:** Support multiple concurrent streams

## Code Architecture

### Dependency Injection

```python
# Dependencies are injected via FastAPI Depends()
@router.post("/tts")
async def generate_tts(
    request: TTSRequest,
    engine: TTSEngine = Depends(get_tts_engine)
):
    # engine is the global singleton instance
    pass
```

### Global Engine Instance

The TTS engine is initialized once at startup and reused for all requests:

```python
# backend/web_tts/dependencies.py
_tts_engine: TTSEngine | None = None

def get_tts_engine() -> TTSEngine:
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = TTSEngine()
        # Pre-load models...
    return _tts_engine
```

## Testing

### Manual Testing

1. **Start server:**
```bash
cd /Users/adityabisen/Desktop/tts_service
source venv/bin/activate
python -m backend.web_tts.main
```

2. **Test REST endpoint:**
```bash
curl -X POST "http://localhost:8050/api/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "નમસ્તે", "lang": "gu", "model": "mms"}'
```

3. **Test WebSocket:**
Use a WebSocket client or the Python example above.

### Health Check

```bash
curl http://localhost:8050/api/health
```

## Next Steps

Phase 3 provides the backend API for:
- **Phase 4:** Web UI Frontend (consumes REST and WebSocket endpoints)

---

**Status:** ✅ Complete  
**Port:** 8050  
**Last Updated:** November 22, 2025

