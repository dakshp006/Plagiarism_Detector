#!/usr/bin/env bash
set -e

echo "======================================================================"
echo "   PLAGIARISM & DUPLICATE TEXT DETECTION SYSTEM - LAUNCHER (macOS/Linux)"
echo "======================================================================"

if [ ! -d "venv" ]; then
    echo "[INFO] Creating Python virtual environment 'venv'..."
    python3 -m venv venv
fi

echo "[INFO] Activating virtual environment..."
source venv/bin/activate

echo "[INFO] Installing required dependencies..."
pip install -r requirements.txt

echo "[INFO] Launching Web Server on http://127.0.0.1:5000 ..."
python run_web.py
