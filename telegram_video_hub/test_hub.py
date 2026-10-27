import os
import sys
from pathlib import Path

# Fix Windows console UTF-8 output
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add workspace root to sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from telegram_video_hub import dispatch_video, send_video_sync, load_config

def main():
    print("=== TELEGRAM VIDEO HUB DIAGNOSTIC ===")
    cfg = load_config()
    print(f"Token configured: {'YES' if cfg.get('bot_token') else 'NO'}")
    print(f"Chat ID configured: {'YES' if cfg.get('chat_id') else 'NO'}")
    print(f"Max size limit: {cfg.get('max_file_size_mb')} MB")
    print(f"FastStreaming enabled: {cfg.get('enable_streaming')}")

    # Check sample video
    sample_video = Path("C:/Users/User/Desktop/douyin_song_ngu_tinh_gon_trau_chuot.mp4")
    if sample_video.exists():
        print(f"\nFound rendered test video: {sample_video.name} ({sample_video.stat().st_size / (1024*1024):.1f} MB)")
    else:
        print("\nNo test video found on Desktop.")

    if not cfg.get("bot_token") or not cfg.get("chat_id"):
        print("\n👉 To configure your bot, run:")
        print("   python -m telegram_video_hub.cli setup")
    else:
        print("\nBot is configured and ready to dispatch videos!")

if __name__ == "__main__":
    main()
