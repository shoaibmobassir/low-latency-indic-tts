# Testing Guide - TTS System Integration

## Quick Start

### Option 1: Automated Script (Recommended)

```bash
# Start both servers
./start_servers.sh

# Stop both servers
./stop_servers.sh
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd /Users/adityabisen/Desktop/tts_service
source venv/bin/activate
python -m backend.web_tts.main
```

**Terminal 2 - Frontend:**
```bash
cd /Users/adityabisen/Desktop/tts_service/frontend/web_ui
npm install  # First time only
npm run dev
```

## Server URLs

- **Backend API:** http://localhost:8050
- **Frontend UI:** http://localhost:3050
- **API Health Check:** http://localhost:8050/api/health

## Testing Steps

### 1. Verify Backend Health

```bash
curl http://localhost:8050/api/health
```

Expected response:
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

### 2. Test REST API

```bash
curl -X POST http://localhost:8050/api/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "નમસ્તે",
    "lang": "gu",
    "model": "mms"
  }'
```

This returns base64-encoded WAV audio.

### 3. Test Frontend UI

1. Open browser: http://localhost:3050
2. Enter Gujarati text: `નમસ્તે, તમે કેમ છો?`
3. Select language: Gujarati
4. Select model: MMS-TTS
5. Click "Speak"
6. Audio should play automatically

### 4. Test WebSocket Streaming

The frontend automatically uses WebSocket when the checkbox is enabled. To test manually:

```javascript
// In browser console (http://localhost:3050)
const ws = new WebSocket('ws://localhost:8050/api/ws/stream_tts');

ws.onopen = () => {
  ws.send(JSON.stringify({
    text: "નમસ્તે",
    lang: "gu",
    model: "mms",
    chunk_ms: 40
  }));
};

ws.onmessage = (event) => {
  if (event.data instanceof ArrayBuffer) {
    console.log('Received audio chunk:', event.data.byteLength, 'bytes');
  } else {
    console.log('End message:', JSON.parse(event.data));
  }
};
```

## Test Cases

### Gujarati Text

**Short:**
```
નમસ્તે
```

**Medium:**
```
એક સમયની વાત છે, ગુજરાતના એક નાના ગામમાં આરવ નામનો છોકરો રહેતો હતો.
```

**Long:**
```
એક સમયની વાત છે, ગુજરાતના એક નાના ગામમાં આરવ નામનો છોકરો રહેતો હતો. તેને નવી નવી વસ્તુઓ શીખવાનું ખૂબ ગમતું હતું. રોજ સાંજે, તે તેની દાદી પાસેથી પ્રાચીન કથાઓ સાંભળતો અને તેઓમાંથી જીવનનો સાર શીખતો.
```

### Marathi Text

**Short:**
```
नमस्कार
```

**Medium:**
```
एक गावात आरव नावाचा हुशार आणि जिज्ञासू मुलगा राहत होता.
```

**Long:**
```
एक गावात आरव नावाचा हुशार आणि जिज्ञासू मुलगा राहत होता. त्याला नवीन गोष्टी शिकण्याची मोठी आवड होती. दर संध्याकाळी तो आपल्या आजीकडून जुनी लोककथा ऐकत असे आणि त्या कथांमधून जीवनातील शिकवण समजून घेत असे.
```

## Model Testing

### MMS-TTS (High Quality)
- Best for: Web UI, high-quality output
- Test with: Medium to long texts
- Expected: High-quality audio, ~200-500ms latency (Mac)

### Piper TTS (Low Latency)
- Best for: Real-time streaming
- Test with: Short to medium texts
- Expected: Fast generation, ~50-100ms latency (Mac)

### IndicTTS (Fallback)
- Best for: When other models fail
- Test with: Any text
- Expected: gTTS quality, ~500-1000ms latency

## Troubleshooting

### Backend Not Starting

1. Check if port 8050 is available:
```bash
lsof -i :8050
```

2. Check Python environment:
```bash
source venv/bin/activate
python -c "import fastapi, uvicorn; print('OK')"
```

3. Check model files exist:
```bash
ls -la backend/models/piper_models/gu_IN-medium/
```

### Frontend Not Starting

1. Check if port 3050 is available:
```bash
lsof -i :3050
```

2. Install dependencies:
```bash
cd frontend/web_ui
npm install
```

3. Check Node.js version:
```bash
node --version  # Should be 18+
```

### WebSocket Connection Failed

1. Verify backend is running
2. Check browser console for errors
3. Verify WebSocket URL: `ws://localhost:8050/api/ws/stream_tts`

### Audio Not Playing

1. Check browser console for errors
2. Verify audio chunks are being received
3. Check browser audio permissions
4. Try REST API fallback (uncheck WebSocket checkbox)

## Performance Benchmarks

### Expected Latencies (Mac M1)

- **MMS-TTS (Gujarati):** 200-500ms
- **MMS-TTS (Marathi):** 200-500ms
- **Piper (Gujarati):** 50-100ms
- **Piper (Marathi):** 50-100ms
- **IndicTTS:** 500-1000ms

### Expected Latencies (H100 GPU)

- **MMS-TTS:** 50-100ms
- **Piper:** 20-50ms
- **IndicTTS:** 500-1000ms

## Next Steps

After successful testing:
- Phase 5: Telecom TTS WebSocket Server
- Phase 6: Integration with Telecom Platform
- Phase 7: Dockerization & Deployment

---

**Last Updated:** November 22, 2025

