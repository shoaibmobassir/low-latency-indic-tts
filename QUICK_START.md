# 🚀 Quick Start Guide

## ✅ Current Status

**Both servers are running!**

- ✅ **Backend:** http://localhost:8050 (FastAPI)
- ✅ **Frontend:** http://localhost:3050 (Next.js)

## 🌐 Access the Application

**Open your browser and go to:**
```
http://localhost:3050
```

## 🧪 Quick Test

1. **Open the UI:** http://localhost:3050
2. **Enter Gujarati text:** `નમસ્તે, તમે કેમ છો?`
3. **Select language:** Gujarati
4. **Select model:** MMS-TTS
5. **Click "Speak"**
6. **Audio should play automatically!**

## 📊 Server Status

### Backend Health Check
```bash
curl http://localhost:8050/api/health
```

**Current Status:**
- ✅ Status: healthy
- ✅ Device: mps (Apple Silicon GPU)
- ✅ MMS-TTS models loaded: Gujarati, Marathi
- ⚠️ Piper models: Not loaded (will load on first use)
- ⚠️ IndicTTS: Not loaded (will load on first use)

### Test REST API
```bash
curl -X POST http://localhost:8050/api/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"નમસ્તે","lang":"gu","model":"mms"}' \
  | python3 -m json.tool | head -5
```

## 🛠️ Server Management

### Start Servers (if stopped)
```bash
./start_servers.sh
```

### Stop Servers
```bash
./stop_servers.sh
```

### Manual Start

**Terminal 1 - Backend:**
```bash
cd /Users/adityabisen/Desktop/tts_service
source venv/bin/activate
python -m backend.web_tts.main
```

**Terminal 2 - Frontend:**
```bash
cd /Users/adityabisen/Desktop/tts_service/frontend/web_ui
npm run dev
```

## 🎯 Test Cases

### Gujarati Text Examples

**Short:**
```
નમસ્તે
```

**Medium:**
```
એક સમયની વાત છે, ગુજરાતના એક નાના ગામમાં આરવ નામનો છોકરો રહેતો હતો.
```

### Marathi Text Examples

**Short:**
```
नमस्कार
```

**Medium:**
```
एक गावात आरव नावाचा हुशार आणि जिज्ञासू मुलगा राहत होता.
```

## 🔍 Troubleshooting

### Frontend Not Loading

1. Check if port 3050 is available:
```bash
lsof -i :3050
```

2. Check frontend logs in terminal

3. Try refreshing the browser

### Backend Not Responding

1. Check if port 8050 is available:
```bash
lsof -i :8050
```

2. Check backend logs in terminal

3. Verify health endpoint:
```bash
curl http://localhost:8050/api/health
```

### Audio Not Playing

1. Check browser console (F12) for errors
2. Try REST API fallback (uncheck WebSocket checkbox)
3. Verify browser audio permissions

## 📝 Next Steps

- Test different models (MMS-TTS, Piper, IndicTTS)
- Test both languages (Gujarati, Marathi)
- Try WebSocket streaming vs REST API
- Adjust chunk size (20-80ms)

---

**For detailed testing instructions, see [TESTING_GUIDE.md](./TESTING_GUIDE.md)**

