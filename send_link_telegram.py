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

# Link Cố Định Vĩnh Viễn 24/7 trên GitHub Pages CDN — Không bao giờ đổi địa chỉ!
PERMANENT_URL = "https://truongduc164.github.io/cyberbird-lingo/"


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

    cloud_url = sys.argv[1].strip() if len(sys.argv) > 1 and sys.argv[1].strip() else PERMANENT_URL
    qr_path = generate_qr(cloud_url)
    print(f"Generated permanent QR for: {cloud_url} -> {qr_path}")

    caption = (
        "🦅 <b>CYBERBIRD LINGO PRO v3.2 — LINK CỐ ĐỊNH VĨNH VIỄN & AI BIÊN TẬP BÀI HỌC!</b>\n\n"
        "✨ <b>2 nâng cấp lớn đã hoàn tất:</b>\n"
        "1️⃣ <b>Link Cố Định 24/7 (Bỏ hẳn trycloudflare):</b> Lưu 1 lần ra Màn hình chính iPhone/Android là dùng trọn đời, tự động cập nhật bài mới mỗi ngày cho mọi máy khách kể cả khi tắt PC!\n"
        "2️⃣ <b>AI Biên Tập Viên Sư Phạm:</b> Tự khử lỗi OCR/tên riêng, đúc kết chủ đề + mẹo nhớ + từ vựng & hội thoại trau chuốt dễ học!\n\n"
        f"👉 <a href=\"{cloud_url}\"><b>MỞ GAME CỐ ĐỊNH VĨNH VIỄN TẠI ĐÂY</b></a>\n"
        f"🔗 {cloud_url}"
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
            files = {"photo": ("qr_cyberbird_permanent_v32.png", f, "image/png")}
            r = requests.post(url, data=data, files=files, timeout=30)
            res = r.json()
            print("sendPhoto response:", res.get("ok"))
            if res.get("ok"):
                print(f"✅ Đã gửi Link Cố Định Vĩnh Viễn & QR v3.2 về Telegram (Msg ID: {res['result']['message_id']})")
                return
            else:
                print("sendPhoto error:", res)

    msg_url = f"https://api.telegram.org/bot{token}/sendMessage"
    r = requests.post(msg_url, json={"chat_id": chat_id, "text": caption, "parse_mode": "HTML"}, timeout=30)
    print("Sent fallback message:", r.status_code)


if __name__ == "__main__":
    main()
