# 🔧 Technical Requirements

This document defines the complete technical specifications for the Gujarati & Marathi TTS System.

## Architecture Overview

```
┌─────────────────┐         ┌──────────────────┐
│   Web UI        │────────▶│  Web TTS Server  │
│   (Port 3050)   │         │   (Port 8050)    │
└─────────────────┘         └──────────────────┘
                                      │
                                      ▼
                            ┌──────────────────┐
                            │  TTS Engine      │
                            │  (GPU Runtime)   │
                            └──────────────────┘
                                      │
                                      ▼
                            ┌──────────────────┐
                            │  Models          │
                            │  XTTS-v2/Piper   │
                            └──────────────────┘

┌─────────────────┐         ┌──────────────────┐
│ Telecom Pipeline│────────▶│ Telecom TTS API  │
│                 │ WebSocket│   (Port 8050)    │
└─────────────────┘         └──────────────────┘
                                      │
                                      ▼
                            ┌──────────────────┐
                            │  TTS Engine      │
                            │  (Piper TTS)     │
                            └──────────────────┘
```

---

## Backend Technical Stack

### Web TTS Server

- **Framework:** FastAPI
- **Port:** 8050
- **Language:** Python 3.9+
- **GPU Support:** CUDA (if available)
- **Audio Processing:** librosa, soundfile, pydub
- **Model Framework:** PyTorch / ONNX Runtime

### Telecom TTS Server

- **Framework:** FastAPI
- **Port:** 8050 (shared with web TTS)
- **Language:** Python 3.9+
- **WebSocket:** FastAPI WebSocket support
- **Audio Encoding:** PCM, G.711 µ-law
- **Model Framework:** Piper TTS (ONNX)

### Common Components

- **TTS Engine:** GPU-accelerated inference
- **Streaming:** Chunk-based audio generation
- **Audio Encoding:** Multiple format support
- **Model Loading:** Dynamic model management

---

## Frontend Technical Stack

### Web UI

- **Framework:** Next.js
- **Port:** 3050
- **Language:** TypeScript
- **UI Library:** React
- **Audio Playback:** HTML5 Audio API / Web Audio API
- **HTTP Client:** Axios / Fetch API
- **Styling:** CSS Modules / Tailwind CSS (optional)

---

## Model Specifications

### XTTS-v2 (Web UI)

- **Framework:** PyTorch
- **Format:** PyTorch checkpoint
- **Languages:** Gujarati, Marathi
- **Voice Cloning:** Supported
- **GPU Memory:** ~2-4 GB
- **Inference Speed:** <100ms (GPU)

### Piper TTS (Telecom API)

- **Framework:** ONNX Runtime
- **Format:** ONNX model
- **Languages:** Gujarati, Marathi
- **GPU Memory:** ~500 MB
- **Inference Speed:** <50ms (CPU/GPU)

---

## Audio Specifications

### Web UI Audio

- **Formats:** MP3, WAV
- **Sample Rate:** 22050 Hz (or model default)
- **Bit Depth:** 16-bit
- **Channels:** Mono

### Telecom API Audio

- **PCM 8kHz:**
  - Sample Rate: 8000 Hz
  - Bit Depth: 16-bit
  - Channels: Mono
  - Encoding: Linear PCM

- **PCM 16kHz:**
  - Sample Rate: 16000 Hz
  - Bit Depth: 16-bit
  - Channels: Mono
  - Encoding: Linear PCM

- **G.711 µ-law:**
  - Sample Rate: 8000 Hz
  - Bit Depth: 8-bit (compressed)
  - Channels: Mono
  - Encoding: G.711 µ-law

---

## API Specifications

### Web TTS REST API

**Base URL:** `http://localhost:8050`

**Endpoints:**

1. **POST /api/tts/generate**
   - Input: `{ "text": string, "language": "gu" | "mr", "format": "mp3" | "wav" }`
   - Output: Audio file (binary)
   - Response: `200 OK` with audio data

2. **POST /api/tts/stream**
   - Input: `{ "text": string, "language": "gu" | "mr" }`
   - Output: Streaming audio chunks
   - Response: `200 OK` with chunked transfer encoding

3. **GET /api/health**
   - Output: `{ "status": "healthy", "models_loaded": [...] }`
   - Response: `200 OK`

### Telecom TTS WebSocket API

**WebSocket URL:** `ws://localhost:8050/ws/telecom/tts`

**Protocol:**

1. **Client → Server:**
   ```json
   {
     "text": "string",
     "language": "gu" | "mr",
     "format": "pcm8k" | "pcm16k" | "g711",
     "sample_rate": 8000 | 16000
   }
   ```

2. **Server → Client:**
   - Binary audio chunks (PCM or G.711)
   - Chunk size: 20-40 ms frames
   - Continuous streaming until text complete

3. **Error Messages:**
   ```json
   {
     "error": "string",
     "code": "error_code"
   }
   ```

---

## Performance Requirements

### Latency Targets

- **Web UI Generation:** <100ms (text → audio)
- **Telecom API End-to-End:** <100ms (text → first chunk)
- **Chunk Generation:** 20-40 ms per chunk
- **Model Loading:** <5 seconds (cold start)

### Throughput

- **Concurrent Requests:** Support 10+ simultaneous users
- **GPU Utilization:** Efficient batching (if applicable)
- **Memory Usage:** <8 GB GPU memory (total)

### Resource Requirements

#### Development Environment
- **GPU:** Apple Silicon (M1/M2/M3) with MPS support
- **CPU:** 4+ cores (for fallback)
- **RAM:** 8+ GB
- **Storage:** 5+ GB (for models)

#### Production Deployment
- **GPU:** NVIDIA H100 GPU with CUDA support (recommended)
- **CPU:** 4+ cores (for Piper TTS fallback)
- **RAM:** 8+ GB
- **Storage:** 5+ GB (for models)

**Note:** The system automatically detects and uses the appropriate device (CUDA for H100, MPS for Mac, CPU as fallback).

---

## Infrastructure Requirements

### Docker

- **Backend Container:**
  - Base: `python:3.9-slim` or `nvidia/cuda:11.8.0-runtime-ubuntu22.04`
  - GPU support: NVIDIA Container Toolkit
  - Exposed ports: 8050

- **Frontend Container:**
  - Base: `node:18-alpine`
  - Exposed ports: 3050
  - Build: Next.js production build

### Docker Compose

- Service orchestration
- Volume mounts for models
- Environment variable configuration
- Network configuration

### Kubernetes (Optional)

- Deployment manifests
- Service definitions
- ConfigMaps for configuration
- Secrets management

---

## Security Requirements

### API Security

- Input validation and sanitization
- Rate limiting (per IP/user)
- CORS configuration
- WebSocket origin validation

### Data Security

- No logging of sensitive text
- Secure model storage
- Environment-based secrets

---

## Monitoring & Logging

### Logging

- Structured logging (JSON)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request/response logging (sanitized)
- Performance metrics logging

### Metrics

- Request latency
- Model inference time
- GPU memory usage
- Error rates
- Throughput

### Health Checks

- `/api/health` endpoint
- Model availability check
- GPU availability check
- Resource usage check

---

## Development Environment

### Required Tools

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose
- CUDA Toolkit (for GPU development)
- Git

### Development Dependencies

- Python: pytest, black, mypy, flake8
- Node.js: ESLint, Prettier, TypeScript

---

## Deployment Environment

### Production Requirements

- GPU-enabled server (for XTTS-v2)
- Load balancer (if scaling)
- Monitoring system (Prometheus/Grafana)
- Log aggregation (ELK stack or similar)

### Configuration

- Environment variables for all configurable values
- Model paths configurable
- Port configuration (enforced: 8050, 3050)
- GPU device selection

---

## Technical Requirements Summary

| Component | Technology | Port | GPU Required |
|-----------|-----------|------|--------------|
| Web TTS Backend | FastAPI | 8050 | Yes (XTTS-v2) |
| Telecom TTS Backend | FastAPI + WebSocket | 8050 | Optional (Piper) |
| Web UI Frontend | Next.js | 3050 | No |
| Models | XTTS-v2, Piper TTS | - | Yes (XTTS-v2) |

**All technical requirements must be implemented exactly as specified.**

