#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
from pathlib import Path
import requests

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from telegram_video_hub import load_config

def main():
    cfg = load_config()
    token = cfg.get("bot_token")
    chat_id = cfg.get("chat_id")
    if not token or not chat_id:
        print("Missing bot credentials")
        return

    qr_path = Path("C:/Users/User/Desktop/qr_cyberbird_lingo.png")
    cloud_url = "https://rolled-pmc-ver-greatest.trycloudflare.com"

    caption = (
        "🚀 <b>CYBERBIRD LINGO PRO v2.5.0 ĐÃ TRỰC TUYẾN 100%!</b>\n\n"
        "✨ <b>Chế độ mới:</b> Hội Thoại Thực Chiến Công Xưởng (12 Tình Huống Logic)\n"
        "⚡ <b>Đường truyền:</b> Cloudflare Tunnel Toàn Cầu (Hong Kong Edge tốc độ cao)\n\n"
        f"🔗 <b>Link chơi trực tiếp trên mọi thiết bị:</b>\n{cloud_url}\n\n"
        "💡 <i>Hoặc quét mã QR đính kèm để mở ngay trên điện thoại!</i>"
    )

    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    data = {
        "chat_id": chat_id,
        "caption": caption,
        "parse_mode": "HTML"
    }

    if qr_path.exists():
        with open(qr_path, "rb") as f:
            files = {"photo": ("qr_cyberbird_lingo.png", f, "image/png")}
            r = requests.post(url, data=data, files=files, timeout=30)
            res = r.json()
            print("sendPhoto response:", res)
            if res.get("ok"):
                print(f"✅ Đã gửi link & QR code trực tiếp về Telegram (Msg ID: {res['result']['message_id']})")
                return

    # Fallback to sendMessage
    msg_url = f"https://api.telegram.org/bot{token}/sendMessage"
    r = requests.post(msg_url, json={"chat_id": chat_id, "text": caption, "parse_mode": "HTML"}, timeout=30)
    print("Sent message:", r.status_code)

if __name__ == "__main__":
    main()
