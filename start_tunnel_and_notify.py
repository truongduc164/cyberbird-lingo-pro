#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Starts Cloudflare Quick Tunnel for http://127.0.0.1:8099, extracts the live
https://*.trycloudflare.com URL as soon as it comes up, automatically regenerates
the QR code, and sends the clickable link + QR straight to Telegram!
"""
import re
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
CLOUDFLARED = Path(r"C:\Program Files (x86)\cloudflared\cloudflared.exe")
URL_RE = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com", re.I)


def main():
    if not CLOUDFLARED.exists():
        print(f"cloudflared not found at {CLOUDFLARED}")
        return

    proc = subprocess.Popen(
        [str(CLOUDFLARED), "tunnel", "--url", "http://127.0.0.1:8099"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    notified = False
    try:
        assert proc.stdout is not None
        for line in proc.stdout:
            print(line, end="", flush=True)
            if not notified:
                m = URL_RE.search(line)
                if m:
                    live_url = m.group(0)
                    notified = True
                    print(f"\n[AUTO-TELEGRAM] Sending fresh tunnel URL + QR to Telegram: {live_url}\n", flush=True)
                    subprocess.Popen([sys.executable, str(ROOT / "send_link_telegram.py"), live_url])
    except KeyboardInterrupt:
        proc.terminate()


if __name__ == "__main__":
    main()
