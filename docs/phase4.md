# Phase 4: Web UI Frontend

## Overview

Phase 4 implements a production-ready Next.js frontend that connects to the Phase 3 FastAPI backend, providing a real-time streaming TTS interface for Gujarati and Marathi languages.

## Architecture

### Frontend Structure

```
Next.js 14+ (App Router)
├── app/
│   ├── layout.tsx        # Root layout with fonts
│   ├── page.tsx          # Main UI page
│   └── globals.css       # Global styles + Tailwind
├── components/
│   ├── TextInput.tsx     # Unicode text input
│   ├── LanguageSelector.tsx
│   ├── ModelSelector.tsx
│   ├── StreamingPlayer.tsx
│   └── RequestForm.tsx
└── lib/
    ├── websocket.ts      # WebSocket client
    ├── audio.ts          # Audio playback
    └── api.ts            # REST API client
```

### Technology Stack

- **Next.js 14+** (App Router)
- **React 18+**
- **TypeScript**
- **TailwindCSS** (styled UI)
- **Web APIs** (WebSocket, AudioContext)

## Features

### UI Components

1. **TextInput**
   - Unicode support for Gujarati and Marathi
   - IME input handling
   - Live character count
   - Language-specific font rendering

2. **LanguageSelector**
   - Toggle between Gujarati and Marathi
   - Visual language indicators

3. **ModelSelector**
   - MMS-TTS (High Quality)
   - Piper (Low Latency)
   - IndicTTS (Fallback)

4. **StreamingPlayer**
   - Real-time progress indicator
   - Play/Stop controls
   - Status visualization
   - Error display

5. **RequestForm**
   - Combines all selectors
   - Chunk size slider (20-80ms)
   - Submit button

### WebSocket Streaming

**Connection:** `ws://localhost:8050/api/ws/stream_tts`

**Protocol:**
1. Client sends JSON request
2. Server streams PCM16 binary chunks
3. Client decodes and buffers chunks
4. Server sends end message with metadata
5. Client plays buffered audio

**Features:**
- Automatic reconnection
- Real-time chunk buffering
- Low-latency playback
- Error handling

### REST API Fallback

**Endpoint:** `POST http://localhost:8050/api/tts`

**Usage:**
- Fallback when WebSocket unavailable
- Complete audio generation
- Base64 WAV decoding
- Direct audio playback

### Audio Playback

**PCM16 Decoding:**
- Converts binary chunks to Float32
- Buffers chunks for seamless playback
- Uses Web Audio API (AudioContext)

**Features:**
- Progress tracking
- Volume control
- Stop/clear functionality
- No stuttering or glitching

## Configuration

### Port

Frontend runs on **port 3050** (as specified in package.json scripts).

### Backend Connection

- **REST API:** `http://localhost:8050/api/tts`
- **WebSocket:** `ws://localhost:8050/api/ws/stream_tts`

### Theme

System theme support (respects user's OS preference):
- Light mode
- Dark mode
- Automatic switching

## Unicode Support

### Fonts

- **Gujarati:** Noto Sans Gujarati
- **Marathi:** Noto Sans Devanagari

Loaded via Google Fonts in `globals.css`.

### Text Rendering

- Proper font family assignment per language
- IME input support
- Full Unicode character support

## Usage

### Development

```bash
cd frontend/web_ui
npm install
npm run dev
```

Server starts on `http://localhost:3050`

### Production Build

```bash
npm run build
npm start
```

## Component API

### RequestForm

```tsx
<RequestForm
  onSubmit={(request) => {
    // request: { text, lang, model, chunk_ms }
  }}
  disabled={false}
/>
```

### StreamingPlayer

```tsx
<StreamingPlayer
  audioPlayer={audioPlayerInstance}
  status="idle" | "connecting" | "streaming" | "playing" | "finished" | "error"
  error={errorMessage | null}
/>
```

### WebSocket Client

```typescript
const client = new TTSWebSocketClient(
  onChunk: (chunk: ArrayBuffer) => void,
  onEnd: (message: TTSEndMessage) => void,
  onError: (error: string) => void,
  onStatusChange: (status: WebSocketStatus) => void
)

client.connect()
client.send({ text, lang, model, chunk_ms })
```

### Audio Player

```typescript
const player = new AudioPlayer(16000) // sample rate

player.addPCM16Chunk(chunk)
player.setOnProgress((progress) => {})
player.setOnEnd(() => {})
await player.play()
player.stop()
```

## Error Handling

### WebSocket Errors

- Connection failures
- Server errors
- Automatic reconnection (up to 3 attempts)

### REST API Errors

- Network errors
- Server errors
- Validation errors

### Audio Playback Errors

- Decoding failures
- Playback failures
- User-friendly error messages

## Performance

### Streaming Latency

- **First Chunk:** <100ms
- **Chunk Buffering:** Real-time
- **Playback Start:** Immediate after buffering

### UI Responsiveness

- Non-blocking operations
- Progress indicators
- Status updates
- Smooth animations

## Next Steps

Phase 4 provides the frontend interface for:
- **Phase 5:** Telecom TTS WebSocket Server (separate endpoint)

---

**Status:** ✅ Complete  
**Port:** 3050  
**Last Updated:** November 22, 2025

