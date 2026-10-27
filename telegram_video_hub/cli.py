import sys
import time
import argparse
import requests
from pathlib import Path

# Fix Windows console UTF-8 output
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from .core import load_config, save_config, send_video_sync

def test_token(token: str):
    """Checks if bot token is valid and returns bot info."""
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if r.status_code == 200 and data.get("ok"):
            return True, data.get("result", {})
        return False, data.get("description", "Unknown error")
    except Exception as e:
        return False, str(e)

def auto_detect_chat_id(token: str, max_wait: int = 30):
    """Polls getUpdates to detect the chat ID when user sends a message to the bot."""
    print(f"\n📡 Đang lắng nghe tin nhắn từ Telegram... (Tối đa {max_wait} giây)")
    print("👉 Hãy mở app Telegram, tìm Bot của bạn và bấm /start hoặc gửi 'Hello':")
    
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    start = time.time()
    last_update_id = 0

    while time.time() - start < max_wait:
        try:
            r = requests.get(f"{url}?offset={last_update_id + 1}", timeout=5)
            data = r.json()
            if data.get("ok") and data.get("result"):
                for upd in data["result"]:
                    last_update_id = upd["update_id"]
                    msg = upd.get("message") or upd.get("channel_post")
                    if msg and "chat" in msg:
                        chat = msg["chat"]
                        sender_name = chat.get("title") or chat.get("first_name") or "User"
                        return chat["id"], sender_name
        except Exception:
            pass
        time.sleep(2)
        print(".", end="", flush=True)

    return None, None

def send_test_message(token: str, chat_id: str):
    """Sends a quick test message to verify communication."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    text = (
        "🎉 <b>[Telegram Video Hub Connected!]</b>\n\n"
        "✅ Trạm trung chuyển thông báo video đã kết nối thành công!\n"
        "🚀 Sẵn sàng nhận video tự động từ <b>BilingualStoryStudio</b> & <b>MoneyPrinterTurbo</b>."
    )
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200 and r.json().get("ok")
    except Exception:
        return False

def interactive_setup():
    print("=" * 60)
    print("🤖 TELEGRAM VIDEO HUB - THIẾT LẬP KẾT NỐI NHANH")
    print("=" * 60)
    
    cfg = load_config()
    current_token = cfg.get("bot_token", "")
    current_chat = cfg.get("chat_id", "")

    if current_token:
        print(f"• Token hiện tại: {current_token[:10]}...{current_token[-5:]}")
    if current_chat:
        print(f"• Chat ID hiện tại: {current_chat}")

    # Prompt Token
    token_input = input("\n🔑 Nhập Bot Token (Enter để giữ nguyên): ").strip()
    token = token_input if token_input else current_token

    if not token:
        print("❌ Chưa có Bot Token. Bạn hãy chat với @BotFather trên Telegram để tạo Bot và lấy token.")
        return

    # Verify Token
    print("\n🔍 Đang xác thực Bot Token...")
    ok, bot_info = test_token(token)
    if not ok:
        print(f"❌ Token không hợp lệ: {bot_info}")
        return

    bot_name = bot_info.get("first_name", "Bot")
    username = bot_info.get("username", "")
    print(f"✅ Kết nối thành công tới Bot: {bot_name} (@{username})")

    # Prompt or auto-detect Chat ID
    print("\n💬 THIẾT LẬP CHAT ID (Nơi nhận video):")
    print("1. Tự động phát hiện (Gửi 1 tin nhắn bất kỳ tới Bot để script tự bắt)")
    print("2. Nhập thủ công Chat ID (Group ID hoặc User ID)")
    choice = input("👉 Chọn (1 hoặc 2, Enter mặc định là 1): ").strip()

    chat_id = current_chat
    if choice == "2":
        manual_id = input("Nhập Chat ID: ").strip()
        if manual_id:
            chat_id = manual_id
    else:
        detected_id, sender = auto_detect_chat_id(token)
        if detected_id:
            print(f"\n🎉 Đã bắt được Chat ID: {detected_id} (Từ: {sender})")
            chat_id = str(detected_id)
        else:
            if current_chat:
                print(f"\n⚠️ Không nhận được tin nhắn mới, sử dụng Chat ID cũ: {current_chat}")
            else:
                manual_id = input("\nHết thời gian chờ. Nhập Chat ID thủ công: ").strip()
                if manual_id:
                    chat_id = manual_id

    if not chat_id:
        print("❌ Chưa có Chat ID. Cấu hình chưa hoàn tất.")
        return

    # Save to config.json
    cfg["bot_token"] = token
    cfg["chat_id"] = str(chat_id)
    save_config(cfg)
    print("\n💾 Đã lưu cấu hình vào telegram_video_hub/config.json!")

    # Test send
    print("📤 Đang gửi tin nhắn xác nhận tới Telegram...")
    if send_test_message(token, chat_id):
        print("🎉 THÀNH CÔNG! Hãy kiểm tra Telegram của bạn để xem tin nhắn xác nhận.")
    else:
        print("⚠️ Không gửi được tin nhắn test. Vui lòng kiểm tra lại quyền của Bot.")

def main():
    parser = argparse.ArgumentParser(description="Telegram Video Hub CLI")
    parser.add_argument("command", nargs="?", default="setup", choices=["setup", "test", "send"], help="Command to run")
    parser.add_argument("--video", "-v", help="Path to video file (for send command)")
    parser.add_argument("--app", "-a", default="CLI Test", help="App name")
    parser.add_argument("--title", "-t", default="Video Test", help="Video title")
    args = parser.parse_args()

    if args.command == "setup":
        interactive_setup()
    elif args.command == "test":
        cfg = load_config()
        if not cfg.get("bot_token") or not cfg.get("chat_id"):
            print("❌ Chưa cấu hình Token & Chat ID. Chạy `python -m telegram_video_hub.cli setup` trước.")
            return
        print("📤 Đang gửi tin nhắn test...")
        if send_test_message(cfg["bot_token"], cfg["chat_id"]):
            print("✅ Gửi tin nhắn test thành công!")
        else:
            print("❌ Gửi tin nhắn test thất bại.")
    elif args.command == "send":
        if not args.video:
            print("❌ Vui lòng truyền đường dẫn file video qua --video <path>")
            return
        print(f"📤 Đang gửi video: {args.video}...")
        ok, res = send_video_sync(
            video_path=args.video,
            title=args.title,
            app_name=args.app,
            tags=["TestCli"]
        )
        if ok:
            print(f"✅ {res}")
        else:
            print(f"❌ {res}")

if __name__ == "__main__":
    main()
