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
        "🎧 <b>CYBERBIRD LINGO PRO v2.5.1 - TỐI ƯU HÓA ÂM THANH TINH GỌN!</b>\n\n"
        "✨ <i>Em đã tinh chỉnh toàn bộ hệ thống âm thanh theo đúng chỉ đạo tinh tế của Sếp:</i>\n\n"
        "1️⃣ <b>Chống Loạn Âm Khi Bay:</b> Trong lúc bay ở chế độ Hội Thoại, loa chỉ đọc câu hỏi của xưởng. Câu trả lời không đọc khi bay để tránh đè âm — tập trung phản xạ mắt và căn cánh bay!\n"
        "2️⃣ <b>Chuông Arcade 'Ting Ting' Trong Veo:</b> Thay thế các tiếng nói động viên ('đạt', 'lợi hại') bằng chuông đôi pha lê <i>Ting Ting</i> cổ điển, cực kỳ đã tai và không làm mất tập trung.\n"
        "3️⃣ <b>Xóa Bỏ 100% Tạp Âm & Tiếng Nhiễu:</b> Khử sạch tiếng xì xào ngẫu nhiên khi đập cánh và tiếng bíp radio rè rè.\n"
        "4️⃣ <b>Nghe Câu Trả Lời Khi Ôn Tập:</b> Nút <i>'🔊 Nghe lại câu trả lời chuẩn'</i> nằm trọn vẹn ở bảng Flashcard khi dừng game để tĩnh tâm tiếp thu sâu.\n\n"
        f"🔗 <b>Bấm vào đây để trải nghiệm ngay:</b>\n{cloud_url}\n\n"
        "💡 <i>Quét mã QR đính kèm hoặc bấm link để test thử âm thanh mới nhé Sếp!</i>"
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
