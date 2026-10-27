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
        "🚀 <b>CYBERBIRD LINGO PRO v2.5.2 - NÂNG CẤP TOÀN DIỆN!</b>\n\n"
        "✨ <i>Em đã rà soát và giải quyết trọn vẹn 3 yêu cầu của Sếp:</i>\n\n"
        "1️⃣ <b>Khắc Phục Triệt Để 2 Giọng Đọc Xen Kẽ:</b> Chuẩn hóa luồng sinh cổng & câu hỏi duy nhất. Tích hợp bộ ngắt âm <code>stopCurrentVoice()</code> độc quyền — tuyệt đối không còn hiện tượng 2 giọng đọc đè lên nhau khi mới bắt đầu!\n"
        "2️⃣ <b>Nút Đổi Chế Độ & Chủ Đề 1-Chạm:</b>\n"
        "   • Thêm nút <b>🏠 Menu</b> ngay trên thanh điều khiển lúc đang bay.\n"
        "   • Thêm nút <b>🏠 ĐỔI CHẾ ĐỘ & CHỦ ĐỀ</b> ở màn hình kết thúc. Sếp có thể tự do chuyển đổi qua lại giữa Hội Thoại Xưởng và Luyện Từ Vựng mà <b>không cần tải lại trang</b>!\n"
        "3️⃣ <b>Nâng Cấp UI/UX Cyberpunk Glassmorphism:</b> Bố cục thẻ kính mờ sang trọng, tự động căn chỉnh và cuộn mượt mà trên mọi màn hình điện thoại.\n"
        "4️⃣ <b>Tích Hợp Tình Huống Xưởng Từ Ảnh Sếp Gửi:</b>\n"
        "   🛠️ <i>'是不是4号吸塑模有问题？'</i> ➔ ✅ <i>'我现在做的也是4号模，问题严重！'</i> (Đã nạp audio Xiaoxiao chuẩn).\n\n"
        f"🔗 <b>Bấm vào đây để trải nghiệm ngay:</b>\n{cloud_url}\n\n"
        "💡 <i>Quét mã QR đính kèm hoặc bấm link để test ngay nhé Sếp!</i>"
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
