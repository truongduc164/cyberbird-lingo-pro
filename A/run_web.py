"""
Run Web Dashboard for VibeRadar
"""
import sys
import webbrowser
import threading
import time
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import uvicorn
import config

def open_browser():
    time.sleep(1.2)
    url = f"http://{config.SERVER_HOST}:{config.SERVER_PORT}"
    print(f"\n[VibeRadar] Mo trinh duyet tai: {url}")
    webbrowser.open(url)

if __name__ == "__main__":
    print("=" * 60)
    print(f"🚀 VibeRadar Web Dashboard khoi dong tai: http://{config.SERVER_HOST}:{config.SERVER_PORT}")
    print("=" * 60)
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("web.app:app", host=config.SERVER_HOST, port=config.SERVER_PORT, log_level="info")
