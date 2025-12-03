# 📦 Product Requirements

This document defines the complete product requirements for the Gujarati & Marathi TTS System.

## Overview

A **production-ready real-time TTS system** with two main components:
1. GPU-Hosted TTS + Web UI
2. Telecom API Endpoint (Low Latency)

---

## A. GPU-Hosted TTS + Web UI

### Features

- ✅ Supports **Gujarati & Marathi** text input
- ✅ Generates and streams TTS audio in **real-time (<100ms)**
- ✅ Web-based UI for testing TTS
- ✅ Language selector (Gujarati/Marathi)
- ✅ Audio controls (play, pause, stop, download)
- ✅ Streaming MP3/WAV output
- ✅ Frontend runs on **port 3050**
- ✅ Backend runs on **port 8050**

### User Experience

- User enters text in selected language (Gujarati/Marathi)
- System generates audio in real-time
- Audio streams to browser for immediate playback
- User can download generated audio files

### Technical Requirements

- Real-time audio generation (<100ms latency)
- Support for MP3 and WAV formats
- Responsive web interface
- Cross-browser compatibility

---

## B. Telecom API Endpoint (Low Latency)

### Features

- ✅ Receives generated text from telecom multimodal pipeline
- ✅ Converts to **PCM 8k/16k** or **G.711 µ-law**
- ✅ Streams audio over **WebSocket**
- ✅ **Ultra-low latency (<100ms)**
- ✅ Real-time chunk generation (20–40 ms frames)

### Integration Requirements

- WebSocket-based streaming protocol
- Support for telecom audio formats (PCM, G.711)
- Low-latency optimization for real-time communication
- Integration with telecom multimodal pipeline

### Performance Requirements

- **Latency:** <100ms end-to-end
- **Chunk size:** 20–40 ms frames
- **Format support:** PCM 8kHz, PCM 16kHz, G.711 µ-law
- **Streaming:** Real-time WebSocket delivery

---

## C. TTS Models

### Web UI (Quality-First)

**Primary Model:**
- **Coqui XTTS-v2** (preferred if voice cloning required)
- **OR IndicTTS** (alternative)

**Requirements:**
- High-quality audio output
- Natural-sounding speech
- Support for Gujarati and Marathi
- Voice cloning capability (if using XTTS-v2)

### Telecom API (Speed-First)

**Primary Model:**
- **Piper TTS** (Gujarati, Marathi models)

**Requirements:**
- Fast inference (<100ms)
- Low resource usage
- Support for Gujarati and Marathi
- Optimized for streaming

---

## D. Language Support

### Supported Languages

1. **Gujarati**
   - Full text-to-speech support
   - Natural pronunciation
   - Proper intonation

2. **Marathi**
   - Full text-to-speech support
   - Natural pronunciation
   - Proper intonation

### Language Selection

- Users can select language via UI
- API accepts language parameter
- Models load dynamically based on language

---

## E. Audio Formats

### Web UI Formats

- **MP3** (compressed, for download)
- **WAV** (uncompressed, for high quality)

### Telecom API Formats

- **PCM 8kHz** (telecom standard)
- **PCM 16kHz** (high quality)
- **G.711 µ-law** (telecom compression)

---

## F. Performance Requirements

### Latency Targets

- **Web UI:** <100ms generation time
- **Telecom API:** <100ms end-to-end latency
- **Chunk generation:** 20–40 ms frames

### Throughput

- Support concurrent requests
- Efficient GPU utilization
- Resource-efficient model loading

---

## G. Scalability Requirements

- Support multiple concurrent users
- Efficient GPU memory management
- Model caching and reuse
- Horizontal scaling capability (future)

---

## H. Security Requirements

- Input validation and sanitization
- Rate limiting for API endpoints
- Secure WebSocket connections
- Error handling without information leakage

---

## I. Monitoring & Observability

- Logging for debugging
- Performance metrics collection
- Error tracking
- Resource usage monitoring

---

## J. Deployment Requirements

- Docker containerization
- Kubernetes support (optional)
- Environment-based configuration
- Health check endpoints

---

## Product Requirements Summary

| Component | Language Support | Latency | Format | Port |
|-----------|-----------------|---------|--------|------|
| Web UI | Gujarati, Marathi | <100ms | MP3, WAV | 3050 |
| Telecom API | Gujarati, Marathi | <100ms | PCM, G.711 | 8050 |

**All requirements are mandatory and must be implemented in full.**

