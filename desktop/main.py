import subprocess
import sys
import time
from pathlib import Path

import webview

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
FRONTEND_URL = "http://localhost:5173"


def start_backend():
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=BACKEND,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )


if __name__ == "__main__":
    backend = start_backend()
    time.sleep(1.5)
    try:
        webview.create_window("Shoro POS", FRONTEND_URL, width=1280, height=820, min_size=(1024, 700))
        webview.start()
    finally:
        backend.terminate()
