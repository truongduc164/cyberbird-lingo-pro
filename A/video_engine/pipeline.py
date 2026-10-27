"""
Antigravity Video Automation Pipeline (REA Core)
End-to-End Orchestrator: Topic/Text -> Storyboard -> TTS -> Motion Frames -> Final MP4.
"""
import sys
import os

# Fix Windows console UTF-8 encoding
if sys.platform == "win32":
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .audio_tts import AudioTTSEngine
from .storyboarder import Storyboarder
from .frame_renderer import FrameRenderer
from .compositor import VideoCompositor

BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"

def run_video_pipeline(
    input_content: str,
    is_raw_text: bool = False,
    lang: str = "vi",
    ratio: str = "9:16",
    output_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute full video generation pipeline.
    ratio: '9:16' (1080x1920) or '16:9' (1920x1080)
    """
    start_time = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    # Resolution setup
    if ratio == "16:9":
        width, height = 1920, 1080
    else: # 9:16 Shorts / Reels
        width, height = 1080, 1920

    fps = 24
    session_id = f"vid_{int(time.time())}"
    work_dir = TEMP_DIR / session_id
    work_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[Pipeline] [START] San xuat video '{session_id}' (Ty le: {ratio}, Ngon ngu: {lang})...")

    # 1. Storyboarding
    storyboarder = Storyboarder()
    if is_raw_text:
        scenes = storyboarder.create_storyboard_from_text(input_content)
    else:
        scenes = storyboarder.create_storyboard_from_topic(input_content, lang=lang)

    print(f"[Pipeline] [STORYBOARD] Da chia thanh {len(scenes)} phan canh (scenes).")

    # 2. Initialize Engines
    tts_engine = AudioTTSEngine(lang=lang)
    frame_renderer = FrameRenderer(width=width, height=height, fps=fps)
    compositor = VideoCompositor(fps=fps)

    compiled_scene_mp4s = []
    total_video_duration = 0.0

    # 3. Process each scene
    for i, scene in enumerate(scenes):
        sc_id = scene["scene_id"]
        sc_dir = work_dir / f"scene_{sc_id}"
        sc_dir.mkdir(parents=True, exist_ok=True)

        print(f"[Pipeline] [SCENE] Xu ly Scene #{sc_id}: '{scene['title']}'...")
        
        # Audio TTS
        audio_path = sc_dir / "audio.mp3"
        duration = tts_engine.generate_speech(scene["text"], str(audio_path))
        # Add slight pause (0.2s) for natural rhythm
        duration += 0.2
        total_video_duration += duration
        print(f"           -> Thoi luong audio: {duration:.2f}s")

        # Frame Generation with Ken Burns
        frames_dir = sc_dir / "frames"
        frame_renderer.generate_scene_frames(
            title=scene["title"],
            text=scene["text"],
            duration=duration,
            theme=scene.get("theme", "cyber_blue"),
            motion=scene.get("motion", "zoom_in"),
            output_dir=frames_dir
        )

        # Compile Scene MP4
        scene_mp4 = sc_dir / "scene.mp4"
        success = compositor.compile_scene_video(frames_dir, audio_path, scene_mp4)
        if success:
            compiled_scene_mp4s.append(scene_mp4)
        else:
            print(f"[Pipeline] [WARNING] Canh #{sc_id} gap loi khi render.")

    # 4. Concatenate Scenes
    if not output_name:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"video_{timestamp_str}.mp4"
    elif not output_name.endswith(".mp4"):
        output_name += ".mp4"

    raw_output_path = work_dir / "master_raw.mp4"
    final_output_path = OUTPUT_DIR / output_name

    print(f"[Pipeline] [COMPOSE] Ghep {len(compiled_scene_mp4s)} phan canh thanh video tong...")
    compositor.concat_scenes(compiled_scene_mp4s, raw_output_path)

    # 5. Check for Background Music (BGM)
    bgm_file = ASSETS_DIR / "bgm.mp3"
    if bgm_file.exists():
        print("[Pipeline] [AUDIO] Long nhac nen (BGM)...")
        compositor.mix_bgm(raw_output_path, bgm_file, final_output_path, bgm_volume=0.12)
    else:
        # If no BGM, move raw output to final
        if raw_output_path.exists():
            shutil.copy2(raw_output_path, final_output_path)

    # Clean up work frames to save disk space
    try:
        shutil.rmtree(work_dir, ignore_errors=True)
    except Exception:
        pass

    elapsed = time.time() - start_time
    file_size_mb = final_output_path.stat().st_size / (1024 * 1024) if final_output_path.exists() else 0

    print(f"[Pipeline] [SUCCESS] Hoan tat trong {elapsed:.1f}s!")
    print(f"[Pipeline] [OUTPUT] Video xuat tai: {final_output_path} ({file_size_mb:.2f} MB)")

    return {
        "status": "success",
        "output_path": str(final_output_path),
        "duration": round(total_video_duration, 2),
        "scenes_count": len(scenes),
        "file_size_mb": round(file_size_mb, 2),
        "elapsed_seconds": round(elapsed, 1)
    }
