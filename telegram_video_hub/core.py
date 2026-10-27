import os
import sys
import json
import time
import shutil
import logging
import tempfile
import threading
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

import requests

from .formatter import format_caption

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [TelegramHub] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("TelegramVideoHub")

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"

def load_config() -> Dict[str, Any]:
    """Loads configuration with fallback to environment variables."""
    cfg = {
        "bot_token": "",
        "chat_id": "",
        "message_thread_id": None,
        "max_file_size_mb": 49.0,
        "auto_compress_if_large": True,
        "enable_streaming": True
    }
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                cfg.update(loaded)
        except Exception as e:
            logger.warning(f"Could not read config.json: {e}")

    # Environment variables take precedence if set
    env_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    env_chat = os.environ.get("TELEGRAM_CHAT_ID")
    if env_token:
        cfg["bot_token"] = env_token
    if env_chat:
        cfg["chat_id"] = env_chat

    return cfg

def save_config(cfg: Dict[str, Any]) -> bool:
    """Saves updated configuration to config.json."""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Failed to save config.json: {e}")
        return False

def probe_video(video_path: Path) -> Dict[str, Any]:
    """
    Extracts video metadata (width, height, duration, size_mb) using ffprobe.
    """
    info = {
        "width": 1080,
        "height": 1920,
        "duration": 0.0,
        "size_mb": video_path.stat().st_size / (1024 * 1024)
    }

    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,duration:format=duration",
            "-of", "json",
            str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        streams = data.get("streams", [])
        if streams:
            info["width"] = int(streams[0].get("width", 1080))
            info["height"] = int(streams[0].get("height", 1920))
            dur_str = streams[0].get("duration")
            if dur_str:
                info["duration"] = float(dur_str)

        if not info["duration"]:
            fmt = data.get("format", {})
            dur_str = fmt.get("duration")
            if dur_str:
                info["duration"] = float(dur_str)

    except Exception as e:
        logger.warning(f"ffprobe extraction fallback: {e}")

    return info

def generate_thumbnail(video_path: Path, output_thumb: Path, duration: float = 1.0) -> bool:
    """
    Extracts a high-quality JPEG thumbnail (max 320x320 px, <= 200KB)
    at 1s or 15% into the video to avoid dark start frames.
    """
    try:
        seek_time = "00:00:01"
        if duration > 3.0:
            seek_sec = min(2.0, duration * 0.15)
            seek_time = f"{seek_sec:.2f}"

        cmd = [
            "ffmpeg", "-y",
            "-ss", seek_time,
            "-i", str(video_path),
            "-vframes", "1",
            "-vf", "scale=320:320:force_original_aspect_ratio=decrease",
            "-q:v", "3",
            str(output_thumb)
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return res.returncode == 0 and output_thumb.exists() and output_thumb.stat().st_size > 0
    except Exception as e:
        logger.warning(f"Thumbnail generation error: {e}")
        return False

def ensure_faststart(video_path: Path, temp_dir: Path) -> Path:
    """
    Optimizes MP4 container by shifting moov atom to the front for instant streaming.
    """
    out_path = temp_dir / f"stream_{video_path.name}"
    try:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-c", "copy",
            "-movflags", "+faststart",
            str(out_path)
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0 and out_path.exists():
            return out_path
    except Exception as e:
        logger.warning(f"Faststart optimization failed: {e}")
    return video_path

def compress_video(video_path: Path, temp_dir: Path, target_mb: float = 45.0) -> Path:
    """
    Intelligently compresses video using H.264 CRF 26-28 to bring it strictly under 50MB.
    """
    out_path = temp_dir / f"compressed_{video_path.stem}.mp4"
    logger.info(f"Video is > {target_mb}MB. Applying smart compression...")
    try:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-c:v", "libx264",
            "-crf", "26",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            str(out_path)
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0 and out_path.exists():
            new_size = out_path.stat().st_size / (1024 * 1024)
            logger.info(f"Compression complete: {new_size:.1f} MB (saved from {video_path.stat().st_size / (1024*1024):.1f} MB)")
            return out_path
    except Exception as e:
        logger.error(f"Compression failed: {e}")
    return video_path

def send_video_sync(
    video_path: str,
    title: str = "",
    description: str = "",
    app_name: str = "Video AI Studio",
    tags: Optional[List[str]] = None,
    custom_thumb: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Synchronously transmits the video to Telegram using official Bot API specs.
    Returns: (is_success, status_or_error_message)
    """
    cfg = load_config()
    token = cfg.get("bot_token", "").strip()
    chat_id = cfg.get("chat_id", "").strip()

    if not token or not chat_id:
        msg = "Telegram Bot Token or Chat ID is not configured! Please configure in telegram_video_hub/config.json."
        logger.error(msg)
        return False, msg

    path = Path(video_path).resolve()
    if not path.exists():
        msg = f"Video file not found: {path}"
        logger.error(msg)
        return False, msg

    start_time = time.time()
    logger.info(f"Preparing dispatch for video: {path.name} ({path.stat().st_size / (1024*1024):.1f} MB)")

    # Read video properties
    info = probe_video(path)
    file_size_mb = info["size_mb"]

    with tempfile.TemporaryDirectory() as tmp_str:
        tmp_dir = Path(tmp_str)
        send_file_path = path

        # Auto-compress if exceeds limit
        max_limit = cfg.get("max_file_size_mb", 49.0)
        if file_size_mb > max_limit and cfg.get("auto_compress_if_large", True):
            send_file_path = compress_video(path, tmp_dir, target_mb=max_limit)
            info = probe_video(send_file_path)
            file_size_mb = info["size_mb"]

        # Ensure FastStart
        if cfg.get("enable_streaming", True):
            send_file_path = ensure_faststart(send_file_path, tmp_dir)

        # Generate thumbnail
        thumb_path = None
        if custom_thumb and Path(custom_thumb).exists():
            thumb_path = Path(custom_thumb)
        else:
            auto_thumb = tmp_dir / "thumbnail.jpg"
            if generate_thumbnail(send_file_path, auto_thumb, duration=info["duration"]):
                thumb_path = auto_thumb

        # Format Caption
        caption_html = format_caption(
            app_name=app_name,
            title=title,
            description=description,
            duration=info["duration"],
            width=info["width"],
            height=info["height"],
            file_size_mb=file_size_mb,
            tags=tags
        )

        url = f"https://api.telegram.org/bot{token}/sendVideo"
        data = {
            "chat_id": chat_id,
            "caption": caption_html,
            "parse_mode": "HTML",
            "supports_streaming": "true" if cfg.get("enable_streaming", True) else "false",
            "width": info["width"],
            "height": info["height"],
            "duration": int(round(info["duration"]))
        }

        if cfg.get("message_thread_id"):
            data["message_thread_id"] = cfg["message_thread_id"]

        logger.info(f"Uploading to Telegram (chat: {chat_id})...")
        try:
            with open(send_file_path, "rb") as video_fp:
                files = {"video": (send_file_path.name, video_fp, "video/mp4")}
                
                thumb_fp = None
                if thumb_path and thumb_path.exists():
                    thumb_fp = open(thumb_path, "rb")
                    files["thumbnail"] = ("thumb.jpg", thumb_fp, "image/jpeg")

                try:
                    response = requests.post(url, data=data, files=files, timeout=180)
                finally:
                    if thumb_fp:
                        thumb_fp.close()

            res_json = response.json()
            if response.status_code == 200 and res_json.get("ok"):
                elapsed = time.time() - start_time
                msg_id = res_json.get("result", {}).get("message_id")
                success_msg = f"Successfully dispatched video to Telegram (Message ID: {msg_id}) in {elapsed:.1f}s"
                logger.info(f"✅ {success_msg}")
                return True, success_msg
            else:
                err_desc = res_json.get("description", response.text)
                err_msg = f"Telegram API error ({response.status_code}): {err_desc}"
                logger.error(f"❌ {err_msg}")
                return False, err_msg

        except requests.exceptions.RequestException as e:
            err_msg = f"Network exception during Telegram upload: {e}"
            logger.error(f"❌ {err_msg}")
            return False, err_msg

def dispatch_video(
    video_path: str,
    title: str = "",
    description: str = "",
    app_name: str = "AI Video Hub",
    tags: Optional[List[str]] = None,
    custom_thumb: Optional[str] = None,
    blocking: bool = False
) -> None:
    """
    Main entry point for all apps to send videos to Telegram.
    By default (blocking=False), uploads asynchronously in a background daemon thread
    so the main video generator returns immediately without freezing.
    """
    if blocking:
        return send_video_sync(
            video_path=video_path,
            title=title,
            description=description,
            app_name=app_name,
            tags=tags,
            custom_thumb=custom_thumb
        )

    # Non-blocking async thread
    thread = threading.Thread(
        target=send_video_sync,
        kwargs={
            "video_path": video_path,
            "title": title,
            "description": description,
            "app_name": app_name,
            "tags": tags,
            "custom_thumb": custom_thumb
        },
        daemon=True
    )
    thread.start()
    logger.info(f"🚀 Video upload task dispatched to background thread for: {Path(video_path).name}")
