#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
import qrcode
import requests

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WORKSPACE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from telegram_video_hub import load_config

DEFAULT_CLOUD_URL = "https://arrive-variety-download-hunting.trycloudflare.com"


def generate_qr(target_url: str) -> Path:
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=3,
    )
    qr.add_data(target_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0284c7", back_color="white")

    qr_path = WORKSPACE_ROOT / "qr_cyberbird_lingo.png"
    img.save(qr_path)

    desktop_qr = Path("C:/Users/User/Desktop/qr_cyberbird_lingo.png")
    if desktop_qr.parent.exists():
        try:
            img.save(desktop_qr)
        except Exception:
            pass
    return qr_path


def main():
    cfg = load_config()
    token = cfg.get("bot_token")
    chat_id = cfg.get("chat_id")
    if not token or not chat_id:
        print("Missing bot credentials")
        return

    cloud_url = sys.argv[1].strip() if len(sys.argv) > 1 and sys.argv[1].strip() else DEFAULT_CLOUD_URL
    qr_path = generate_qr(cloud_url)
    print(f"Generated fresh QR for: {cloud_url} -> {qr_path}")

    caption = (
        "🦅 <b>CYBERBIRD LINGO PRO v3.1.1 — LINK MỚI VÀO CHƠI NGAY!</b>\n\n"
        "✅ Đã làm mới đường truyền + đưa nút <b>🚀 BẮT ĐẦU BAY NGAY</b> lên ngay chính giữa màn hình iPhone (chạm 1 phát bay luôn + tự lưu Offline 100% MP3)!\n\n"
        f"👉 <a href=\"{cloud_url}\"><b>BẤM VÀO ĐÂY ĐỂ MỞ GAME NGAY</b></a>\n"
        f"🔗 {cloud_url}\n\n"
        "📡 <i>Dự phòng cố định:</i>\n"
        "• Cùng Wi-Fi: http://192.168.2.19:8099\n"
        "• Tailscale: http://100.84.141.94:8099"
    )
    print(f"Caption length: {len(caption)} chars")

    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    data = {
        "chat_id": chat_id,
        "caption": caption,
        "parse_mode": "HTML",
    }

    if qr_path.exists():
        with open(qr_path, "rb") as f:
            files = {"photo": ("qr_cyberbird_lingo_v311.png", f, "image/png")}
            r = requests.post(url, data=data, files=files, timeout=30)
            res = r.json()
            print("sendPhoto response:", res.get("ok"))
            if res.get("ok"):
                print(f"✅ Đã gửi link & QR code v3.1.1 trực tiếp về Telegram (Msg ID: {res['result']['message_id']})")
                return
            else:
                print("sendPhoto error:", res)

    msg_url = f"https://api.telegram.org/bot{token}/sendMessage"
    r = requests.post(msg_url, json={"chat_id": chat_id, "text": caption, "parse_mode": "HTML"}, timeout=30)
    print("Sent fallback message:", r.status_code)


if __name__ == "__main__":
    main()
