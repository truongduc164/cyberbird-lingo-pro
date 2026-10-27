#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

# Connect to centralized Telegram Video Hub
HUB_DIR = Path(__file__).resolve().parent.parent / "telegram_video_hub"
if str(HUB_DIR.parent) not in sys.path:
    sys.path.insert(0, str(HUB_DIR.parent))

from telegram_video_hub import dispatch_video, send_video_sync, load_config

def main():
    cfg = load_config()
    if not cfg.get("bot_token") or not cfg.get("chat_id"):
        print("❌ Telegram Bot Token hoặc Chat ID chưa được cấu hình!")
        print("👉 Hãy chạy setup nhanh: python -m telegram_video_hub.cli setup")
        return

    # Check target video
    video_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not video_path:
        default_video = Path(__file__).parent / "bo_ngua_bat_ve.mp4"
        if default_video.exists():
            video_path = str(default_video)
        else:
            print("Usage: python send_to_telegram.py <path_to_video.mp4>")
            return

    title = sys.argv[2] if len(sys.argv) > 2 else "Bọ Ngựa Bắt Ve, Chim Sẻ Phía Sau"
    print(f"🚀 Đang gửi video qua Telegram Hub: {video_path}")
    
    ok, res = send_video_sync(
        video_path=video_path,
        title=title,
        description="Video hoạt hình ngụ ngôn Hán-Việt Douyin Full HD",
        app_name="BilingualStoryStudio",
        tags=["DouyinSongNgu", "HocTiengTrung", "ShortsAI"]
    )
    if ok:
        print(f"✅ {res}")
    else:
        print(f"❌ {res}")

if __name__ == "__main__":
    main()
