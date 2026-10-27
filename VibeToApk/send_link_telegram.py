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
        "🎛️ <b>CYBERBIRD LINGO PRO v2.5.3 - TÙY CHỈNH TỐC ĐỘ NÓI & CỠ CHỮ!</b>\n\n"
        "✨ <i>Em đã tinh chỉnh hoàn thiện theo đúng ý kiến đóng góp của Sếp:</i>\n\n"
        "1️⃣ <b>Tự Động Đồng Bộ Tốc Độ Giọng Đọc:</b>\n"
        "   • 🟢 <b>Dễ:</b> Giọng Xiaoxiao đọc chậm rãi <b>0.85x</b>, phát âm từng âm tiết cực rõ ràng cho người mới học.\n"
        "   • 🟡 <b>Vừa:</b> Tốc độ chuẩn tự nhiên <b>1.0x</b>.\n"
        "   • 🔴 <b>Pro:</b> Tốc độ bứt phá <b>1.2x</b>, rèn phản xạ giao tiếp dồn dập.\n\n"
        "2️⃣ <b>Bảng Tự Do Tùy Chỉnh (Tốc Độ Nói & Cỡ Chữ):</b>\n"
        "   • 🗣️ <b>Giọng nói:</b> Tùy chọn độc lập <code>🐢 0.85x</code> • <code>⚡ 1.0x</code> • <code>🚀 1.2x</code>.\n"
        "   • 🔤 <b>Cỡ chữ ô cổng:</b> Tùy chọn <code>14px</code> • <code>16.5px (Lớn)</code> • <code>19px (Siêu To)</code>!\n\n"
        "3️⃣ <b>Chữ Ô Cổng Bay To Rõ Nét Hơn 30%:</b> Chữ trong ô làn trên/dưới và thanh đề bài được nâng cấp kích thước lớn, tương phản cao, liếc mắt là đọc được ngay khi đang bay!\n\n"
        f"🔗 <b>Bấm vào đây để trải nghiệm ngay:</b>\n{cloud_url}\n\n"
        "💡 <i>Quét mã QR đính kèm hoặc bấm link để thử giọng đọc chậm 0.85x và chữ to nhé Sếp!</i>"
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
