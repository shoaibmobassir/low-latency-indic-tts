# Troubleshooting Guide

## Frontend 404 Errors

### Issue: `GET http://localhost:3050/_next/static/... 404 (Not Found)`

**Solution:**
1. **Hard refresh your browser:**
   - Mac: `Cmd + Shift + R`
   - Windows/Linux: `Ctrl + Shift + R`
   - Or clear browser cache

2. **Restart Next.js server:**
   ```bash
   cd frontend/web_ui
   pkill -f "next dev"
   npm run dev
   ```

3. **Wait for server to fully start** (about 10-15 seconds)

## Audio Not Playing

### Issue: Data received but no sound

**Solutions:**

1. **Check browser console (F12)** for errors
2. **Verify audio permissions** in browser settings
3. **Try REST API fallback:**
   - Uncheck "Use WebSocket Streaming" checkbox
   - Click "Speak" again
4. **Manual play:**
   - After streaming completes, click the "Play" button
5. **Check console logs:**
   - Should see: `Received audio chunk: X bytes`
   - Should see: `Added chunk: X samples`
   - Should see: `Playing audio: X samples`

### Common Causes:

- **Browser autoplay policy**: Some browsers block autoplay
- **Audio context suspended**: Requires user interaction
- **Empty audio buffer**: No chunks received
- **Sample rate mismatch**: Should be 16000 Hz

## WebSocket Connection Issues

### Issue: WebSocket fails to connect

**Solutions:**

1. **Verify backend is running:**
   ```bash
   curl http://localhost:8050/api/health
   ```

2. **Check WebSocket URL:**
   - Should be: `ws://localhost:8050/api/ws/stream_tts`

3. **Check browser console** for connection errors

4. **Use REST API fallback** (uncheck WebSocket checkbox)

## Backend Not Responding

### Issue: Backend health check fails

**Solutions:**

1. **Check if backend is running:**
   ```bash
   ps aux | grep "backend.web_tts.main"
   ```

2. **Restart backend:**
   ```bash
   cd /Users/adityabisen/Desktop/tts_service
   source venv/bin/activate
   python -m backend.web_tts.main
   ```

3. **Check port 8050:**
   ```bash
   lsof -i :8050
   ```

## Quick Fixes

### Restart Both Servers

```bash
# Stop servers
./stop_servers.sh

# Start servers
./start_servers.sh
```

### Clear Browser Cache

1. Open DevTools (F12)
2. Right-click refresh button
3. Select "Empty Cache and Hard Reload"

### Check Logs

**Backend logs:** Check terminal where backend is running
**Frontend logs:** Check browser console (F12)

## Still Having Issues?

1. **Check browser console** (F12) for detailed errors
2. **Verify both servers are running:**
   - Backend: http://localhost:8050/api/health
   - Frontend: http://localhost:3050
3. **Try REST API** instead of WebSocket
4. **Check network tab** in DevTools to see requests/responses

