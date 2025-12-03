# 🎙️ Indic TTS Streaming

> Real-time, low-latency Text-to-Speech system for Gujarati and Marathi languages with streaming audio playback.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

-  **Ultra-Low Latency**: <100ms perceived latency (click to first audio playback)
-  **Real-Time Streaming**: WebSocket-based packet streaming with immediate audio playback
-  **Multi-Model Support**: MMS-TTS (high quality) and IndicTTS (fallback)
-  **Indic Language Focus**: Native support for Gujarati (ગુજરાતી) and Marathi (मराठी)
-  **Smart Language Detection**: Automatic language detection with auto-correction
-  **Interactive UI**: Modern web interface with play/pause controls
-  **GPU Accelerated**: CUDA (NVIDIA), MPS (Apple Silicon), and CPU support
-  **Production Ready**: Docker support, health checks, and comprehensive monitoring

## 🏗️ Architecture

```
┌─────────────────┐         WebSocket/REST        ┌──────────────────┐
│   Next.js UI    │ ◄──────────────────────────► │   FastAPI Server │
│   (Port 3050)   │         Real-time Audio       │   (Port 8050)    │
└─────────────────┘                               └──────────────────┘
                                                            │
                                                            ▼
                                                   ┌────────────────┐
                                                   │  TTS Engine    │
                                                   ├────────────────┤
                                                   │ • MMS-TTS      │
                                                   │ • IndicTTS     │
                                                   │ • Piper TTS    │
                                                   └────────────────┘
```

### Key Components

- **Frontend**: Next.js with TypeScript, TailwindCSS, and Web Audio API
- **Backend**: FastAPI with WebSocket streaming and REST endpoints
- **TTS Engine**: Multi-model support with smart chunking and streaming
- **Audio Pipeline**: Packet-based streaming with PCM16 encoding

##  Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- GPU (NVIDIA CUDA or Apple Silicon MPS) or CPU

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/indic-tts-streaming.git
cd indic-tts-streaming
```

2. **Set up Python environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r backend/models/requirements.txt
```

3. **Set up Frontend**
```bash
cd frontend/web_ui
npm install
cd ../..
```

4. **Set Hugging Face token** (required for model downloads)
```bash
export HUGGING_FACE_HUB_TOKEN=your_token_here
```

5. **Start the servers**
```bash
./start_servers.sh
```

The application will be available at:
- **Frontend**: http://localhost:3050
- **Backend API**: http://localhost:8050
- **API Docs**: http://localhost:8050/docs

## 📖 Usage

### Web Interface

1. Open http://localhost:3050 in your browser
2. Enter text in Gujarati or Marathi
3. Select language and model
4. Click **"Speak"** to generate and play audio
5. Use **Play/Pause** to control playback

### REST API

**Generate TTS audio:**
```bash
curl -X POST http://localhost:8050/api/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "નમસ્તે, તમે કેમ છો?",
    "lang": "gu",
    "model": "mms"
  }' \
  --output audio.wav
```

**Health Check:**
```bash
curl http://localhost:8050/api/health
```

### WebSocket Streaming

```javascript
const ws = new WebSocket('ws://localhost:8050/api/ws/stream_tts');

ws.onopen = () => {
  ws.send(JSON.stringify({
    text: "નમસ્તે, તમે કેમ છો?",
    lang: "gu",
    model: "mms",
    chunk_size_ms: 60
  }));
};

ws.onmessage = (event) => {
  if (event.data instanceof Blob) {
    // Audio chunk (PCM16 format)
    playAudioChunk(event.data);
  } else {
    // JSON metadata or end message
    const message = JSON.parse(event.data);
    console.log(message);
  }
};
```

## ⚙️ Configuration

### Model Selection

Edit `backend/common/config.py`:

```python
# Audio Configuration
DEFAULT_CHUNK_SIZE_MS = 60  # Optimized for <100ms latency

# Performance Optimization
USE_FP16_ON_CUDA = True      # 1.5-2x speedup on NVIDIA GPUs
USE_TORCH_COMPILE = True     # Faster inference (PyTorch 2.0+)
LOW_LATENCY_MODE = True      # Enable all optimizations
```

### Available Models

| Model | Languages | Quality | Latency | Use Case |
|-------|-----------|---------|---------|----------|
| **MMS-TTS** | Gujarati, Marathi | High | Low | Web UI, General |
| **IndicTTS** | Gujarati, Marathi | Medium | Very Low | Fallback |
| **Piper TTS** | Gujarati, Marathi | Medium | Ultra Low | Telecom API |

### Chunk Size Tuning

The system uses **60ms chunks** by default (optimized experimentally). To adjust:

```python
# In backend/common/config.py
DEFAULT_CHUNK_SIZE_MS = 60  # Range: 20-100ms
```

**Trade-offs:**
- **Smaller chunks (20-40ms)**: Lower latency, more CPU overhead
- **Larger chunks (80-100ms)**: Higher latency, smoother playback

## 🐳 Docker Deployment

### Build and Run

```bash
docker-compose up -d
```

The services will be available on the same ports (3050, 8050).

### Environment Variables

Create a `.env` file:

```bash
HUGGING_FACE_HUB_TOKEN=your_token_here
CUDA_VISIBLE_DEVICES=0
TTS_DEVICE=cuda  # or mps, or cpu
```

## 📊 Performance Metrics

### Latency Benchmarks (Apple M1 Max, MPS)

| Text Length | First Chunk | Total Time | Perceived Latency |
|-------------|-------------|------------|-------------------|
| 50 chars | ~80ms | ~1.2s | ~90ms |
| 200 chars | ~85ms | ~4.5s | ~95ms |
| 500 chars | ~90ms | ~11s | ~98ms |

### GPU Acceleration

| Device | Speedup | Typical RTF* |
|--------|---------|--------------|
| NVIDIA H100 | 5-10x | 0.05-0.1x |
| Apple M1/M2 | 3-5x | 0.15-0.25x |
| CPU | 1x | 0.5-1.0x |

*RTF = Real-Time Factor (lower is faster)

## 🛣️ Roadmap

- [x] Real-time WebSocket streaming
- [x] Multi-model support (MMS-TTS, IndicTTS)
- [x] Smart language detection
- [x] GPU acceleration (CUDA, MPS)
- [x] Web UI with audio controls
- [ ] Additional Indic languages (Hindi, Bengali, Tamil)
- [ ] Voice cloning support
- [ ] Prosody and emotion control
- [ ] Batch processing API
- [ ] Kubernetes deployment configs

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write tests for new features
- Update documentation as needed

## 📚 Documentation

- [Quick Start Guide](QUICK_START.md)
- [Testing Guide](TESTING_GUIDE.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [API Documentation](http://localhost:8050/docs) (when server is running)

## 🏷️ Repository Name Suggestions

When publishing to GitHub, consider these names:
- `indic-tts-streaming` ⭐ (Recommended)
- `realtime-indic-tts`
- `gujarati-marathi-tts`
- `streaming-indic-voice`
- `low-latency-indic-tts`

## 🙏 Acknowledgments

- [Facebook MMS-TTS](https://github.com/facebookresearch/fairseq/tree/main/examples/mms) - Massively Multilingual Speech models
- [IndicTTS](https://github.com/AI4Bharat/Indic-TTS) - Indic language TTS models
- [Piper TTS](https://github.com/rhasspy/piper) - Fast, local neural text to speech

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For issues and questions:
- Open an [issue](https://github.com/yourusername/indic-tts-streaming/issues)
- Check [Troubleshooting Guide](TROUBLESHOOTING.md)
- Review [API Documentation](http://localhost:8050/docs)

---

**Made with ❤️ for Indic language speakers**

