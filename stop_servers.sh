#!/bin/bash
# Stop both backend and frontend servers

echo "Stopping TTS System servers..."

if [ -f /tmp/tts_backend.pid ]; then
    BACKEND_PID=$(cat /tmp/tts_backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        echo "✅ Stopped backend server (PID: $BACKEND_PID)"
    else
        echo "Backend server was not running"
    fi
    rm -f /tmp/tts_backend.pid
else
    echo "Backend PID file not found"
fi

if [ -f /tmp/tts_frontend.pid ]; then
    FRONTEND_PID=$(cat /tmp/tts_frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        echo "✅ Stopped frontend server (PID: $FRONTEND_PID)"
    else
        echo "Frontend server was not running"
    fi
    rm -f /tmp/tts_frontend.pid
else
    echo "Frontend PID file not found"
fi

# Also try to kill any remaining processes
pkill -f "backend.web_tts.main" 2>/dev/null && echo "Cleaned up backend processes"
pkill -f "next dev" 2>/dev/null && echo "Cleaned up frontend processes"

echo "Done!"

