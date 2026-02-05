#!/bin/bash

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   PROFESSIONAL REMINDER APP v1.0     ║"
echo "║   Starting Services...               ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not installed"
    exit 1
fi

echo "[1/3] Installing dependencies..."
cd backend
pip install -q -r requirements.txt

echo "[✓] Dependencies installed"

echo "[2/3] Starting backend server..."
python3 app.py &
BACKEND_PID=$!
sleep 2

echo "[3/3] Starting frontend server..."
cd ../frontend
python3 -m http.server 8000 &
FRONTEND_PID=$!
sleep 1

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   REMINDER PRO - RUNNING             ║"
echo "╠══════════════════════════════════════╣"
echo "║ Backend:  http://localhost:3000      ║"
echo "║ Frontend: http://localhost:3000      ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "[✓] App is ready at http://localhost:3000"
echo "[!] Press Ctrl+C to stop"
echo ""

wait
