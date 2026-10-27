#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
import requests

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

WORKSPACE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from telegram_video_hub import load_config


def main():
    cfg = load_config()
    token = cfg.get("bot_token")
    chat_id = cfg.get("chat_id")
    if not token or not chat_id:
        print("Missing bot credentials")
        return

    qr_path = WORKSPACE_ROOT / "qr_cyberbird_lingo.png"
    if not qr_path.exists():
        qr_path = Path("C:/Users/User/Desktop/qr_cyberbird_lingo.png")

    cloud_url = "https://level-lang-satisfactory-stevens.trycloudflare.com"

    caption = (
        "🦅 <b>CYBERBIRD LINGO PRO v3.0 — NHẬT KÝ NGÀY & SILENT WATCHDOG!</b>\n\n"
        "✨ <i>Dự án độc lập <code>23. CyberBird-Lingo-Game</code> đã hoàn thiện bản v3.0:</i>\n"
        "• 📅 <b>Nhật Ký Ngày (Timeline):</b> Watchdog chạy ngầm tự tổng hợp WeChat/Zalo/Tủ điện (<b>89 từ + 6 hội thoại</b> hôm nay: <code>BTN-8-11</code>, <code>7071</code>, <code>SMI-16</code>, <code>SP-165</code> + 137 file âm thanh Xiaoxiao).\n"
        "• ⚡ <b>165+ Từ Vựng & 31+ Hội Thoại:</b> Tích hợp 45 thuật ngữ Tủ Điện & Tự Động Hóa + lọc chủ đề + gói <b>APK Offline v3.0</b>.\n\n"
        f"🔗 <b>Chơi ngay tại đây:</b>\n{cloud_url}\n\n"
        "💡 <i>Quét mã QR hoặc bấm link trên iPhone / Android để bay thử ngay nhé Sếp!</i>"
    )

    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    data = {
        "chat_id": chat_id,
        "caption": caption,
        "parse_mode": "HTML"
    }

    if qr_path.exists():
        with open(qr_path, "rb") as f:
            files = {"photo": ("qr_cyberbird_lingo_v3.png", f, "image/png")}
            r = requests.post(url, data=data, files=files, timeout=30)
            res = r.json()
            print("sendPhoto response:", res.get("ok"))
            if res.get("ok"):
                print(f"✅ Đã gửi link & QR code v3.0 trực tiếp về Telegram (Msg ID: {res['result']['message_id']})")
                return

    msg_url = f"https://api.telegram.org/bot{token}/sendMessage"
    r = requests.post(msg_url, json={"chat_id": chat_id, "text": caption, "parse_mode": "HTML"}, timeout=30)
    print("Sent message:", r.status_code)


if __name__ == "__main__":
    main()
