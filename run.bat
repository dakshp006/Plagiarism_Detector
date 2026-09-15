@echo off
echo ======================================================================
echo    PLAGIARISM & DUPLICATE TEXT DETECTION SYSTEM - LAUNCHER
echo ======================================================================

IF NOT EXIST "venv" (
    echo [INFO] Creating Python virtual environment 'venv'...
    python -m venv venv
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Installing required dependencies...
python -m pip install -r requirements.txt

echo [INFO] Launching Web Server on http://127.0.0.1:5000 ...
python run_web.py
pause
