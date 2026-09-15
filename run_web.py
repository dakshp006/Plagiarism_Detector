"""
Web Application Launcher for Plagiarism & Duplicate Text Detection System.
Launches the Flask API backend server on http://127.0.0.1:5000
"""

import sys
import os
import subprocess
import webbrowser
import time

def main():
    print("=" * 70)
    print("      PLAGIARISM & DUPLICATE TEXT DETECTION SYSTEM - WEB SERVER      ")
    print("             Python + Rabin-Karp + KMP + Database Engine             ")
    print("=" * 70)

    # Ensure required python dependencies are present
    try:
        import flask
        import flask_cors
    except ImportError:
        print("[INFO] Installing required web dependencies (Flask, Flask-Cors)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-cors"])

    server_script = os.path.join(os.path.dirname(__file__), "server.py")
    
    print("\n[SUCCESS] Starting Web Server on http://127.0.0.1:5000 ...")
    print("Press Ctrl+C in terminal to stop the web server.\n")

    # Start Flask server
    subprocess.run([sys.executable, server_script])

if __name__ == "__main__":
    main()
