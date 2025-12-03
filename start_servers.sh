#!/bin/bash
# Start both backend and frontend servers for TTS System

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Starting TTS System Servers"
echo "=========================================="

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please create it first."
    exit 1
fi

source venv/bin/activate

# Start backend server
echo ""
echo "Starting Backend Server (port 8050)..."
cd "$SCRIPT_DIR"
python -m backend.web_tts.main &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 5

# Check if backend is running
if curl -s http://localhost:8050/api/health > /dev/null; then
    echo "✅ Backend server is running on http://localhost:8050"
else
    echo "❌ Backend server failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Start frontend server
echo ""
echo "Starting Frontend Server (port 3050)..."
cd "$SCRIPT_DIR/frontend/web_ui"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait for frontend to start
sleep 8

# Check if frontend is running
if curl -s http://localhost:3050 > /dev/null; then
    echo "✅ Frontend server is running on http://localhost:3050"
else
    echo "❌ Frontend server failed to start"
    kill $FRONTEND_PID 2>/dev/null || true
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Both servers are running!"
echo "=========================================="
echo ""
echo "Backend:  http://localhost:8050"
echo "Frontend: http://localhost:3050"
echo ""
echo "API Health: http://localhost:8050/api/health"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Save PIDs to file for cleanup
echo "$BACKEND_PID" > /tmp/tts_backend.pid
echo "$FRONTEND_PID" > /tmp/tts_frontend.pid

# Wait for interrupt
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; rm -f /tmp/tts_backend.pid /tmp/tts_frontend.pid; exit" INT TERM

wait

