#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veo-gravity Showcase: AI Generated Anime Character Video from Antigravity Quota
- Uses native Antigravity generated Makoto Shinkai aesthetic image
- Multi-shot cinematic camera motion (Wide room -> Face & Eyes -> Phone & Hands -> Sunset & Ending)
- Screen light glow, breathing motion, floating ambient dust particles
- Native Chinese Xiaoxiao voiceover + Ghibli/Lo-fi background music
- Dual-line bilingual subtitles (9:16 vertical 1080x1920)
- Auto-dispatch to Telegram Video Hub
"""

import os
import sys
import math
import asyncio
from pathlib import Path
import subprocess
import numpy as np
import cv2
from PIL import Image
import edge_tts

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

WORKSPACE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from telegram_video_hub import dispatch_video

FFMPEG = "ffmpeg"
IMAGE_PATH = Path(r"C:\Users\User\.gemini\antigravity\brain\3974c1a6-9381-4861-bd15-40057c89e7eb\anime_girl_chill_phone_1792728608015.jpg")

SCENES = [
    {
        "id": 1,
        "title": "Toàn cảnh hoàng hôn & Căn phòng ấm áp",
        "cn": "学习中文，快乐每一天！在温暖的夕阳下，享受属于自己的宁静时光。",
        "vi": "Học tiếng Trung, vui mỗi ngày! Dưới ánh hoàng hôn ấm áp, tận hưởng phút giây bình yên.",
        "crop_start": (0, 0, 768, 1365),
        "crop_end": (30, 60, 708, 1258)
    },
    {
        "id": 2,
        "title": "Cận cảnh nụ cười & Đôi mắt sáng",
        "cn": "躺在温暖的垫子上，明亮的眼睛 (yǎnjing)，开心地看着手机屏幕 (píngmù)。",
        "vi": "Nằm trên chiếc gối êm, đôi mắt sáng (yǎnjing), vui vẻ nhìn màn hình điện thoại.",
        "crop_start": (220, 500, 480, 853),
        "crop_end": (250, 540, 420, 746)
    },
    {
        "id": 3,
        "title": "Hai bàn tay cầm điện thoại & Ánh sáng ấm",
        "cn": "双手 (shǒu) 拿着手机 (shǒujī)，屏幕的微光照亮了整个慵懒的午后。",
        "vi": "Hai bàn tay (shǒu) cầm điện thoại (shǒujī), ánh sáng màn hình thắp sáng buổi chiều thư thái.",
        "crop_start": (150, 240, 540, 960),
        "crop_end": (180, 260, 480, 853)
    },
    {
        "id": 4,
        "title": "Mẹo nhỏ • Ngắm nhìn hoàng hôn",
        "cn": "小提示：手机虽然好玩，但也要记得常常抬头，看看窗外美丽的晚霞哦！",
        "vi": "Mẹo nhỏ: Điện thoại tuy vui, nhưng hãy nhớ thỉnh thoảng ngước nhìn hoàng hôn tuyệt đẹp nhé!",
        "crop_start": (100, 80, 620, 1102),
        "crop_end": (50, 40, 680, 1208)
    }
]

async def generate_speech(text: str, output_path: Path, voice: str = "zh-CN-XiaoxiaoNeural") -> float:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    comm = edge_tts.Communicate(text, voice, rate="+1%")
    await comm.save(str(output_path))
    
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(output_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def format_ass_timestamp(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hrs:d}:{mins:02d}:{secs:05.2f}"

def build_ass_subtitles(scenes, output_ass: Path):
    ass_content = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Bilingual,Microsoft YaHei,54,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,4.0,2.0,2,40,40,320,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    for sc in scenes:
        start_ts = format_ass_timestamp(sc["start"])
        end_ts = format_ass_timestamp(sc["start"] + sc["dur"])
        cn = sc["cn"]
        vi = sc["vi"]
        text_line = f"{{\\b1\\c&H00FFFFFF\\fs54}}{cn}\\N{{\\b1\\c&H003CEBFF\\fs42}}{vi}"
        ass_content += f"Dialogue: 0,{start_ts},{end_ts},Bilingual,,0,0,0,,{text_line}\n"

    output_ass.write_text(ass_content, encoding="utf-8")

def render_cinematic_scene(orig_img: np.ndarray, sc: dict, out_video: Path, fps=30):
    """
    Renders continuous cinematic camera motion (Ken Burns zoom & pan)
    with breathing motion, pulsing screen glow, and floating dust particles.
    """
    canvas_w, canvas_h = 1080, 1920
    total_frames = int(round(sc["dur"] * fps))
    orig_h, orig_w = orig_img.shape[:2]

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_video), fourcc, fps, (canvas_w, canvas_h))

    x0, y0, w0, h0 = sc["crop_start"]
    x1, y1, w1, h1 = sc["crop_end"]

    # Generate random particle offsets for atmospheric room dust
    np.random.seed(sc["id"] * 42)
    n_particles = 25
    particles_x = np.random.uniform(0, canvas_w, n_particles)
    particles_y = np.random.uniform(0, canvas_h, n_particles)
    particles_speed = np.random.uniform(0.5, 1.8, n_particles)

    for f in range(total_frames):
        alpha = f / max(1, total_frames - 1)
        # Smooth ease-in-out cosine curve
        smooth_t = (1 - math.cos(alpha * math.pi)) / 2

        # Interpolate crop region
        cur_x = int(x0 + (x1 - x0) * smooth_t)
        cur_y = int(y0 + (y1 - y0) * smooth_t)
        cur_w = int(w0 + (w1 - w0) * smooth_t)
        cur_h = int(h0 + (h1 - h0) * smooth_t)

        # Subtle breathing vertical shift (2.5 seconds cycle)
        breath = int(math.sin(2 * math.pi * f / (fps * 2.5)) * 3)
        cur_y = max(0, min(orig_h - cur_h, cur_y + breath))
        cur_x = max(0, min(orig_w - cur_w, cur_x))

        crop = orig_img[cur_y : cur_y + cur_h, cur_x : cur_x + cur_w]
        frame = cv2.resize(crop, (canvas_w, canvas_h), interpolation=cv2.INTER_LANCZOS4)

        # Subtle warm screen glow pulsation (3.0 Hz)
        glow_pulse = 0.04 * math.sin(2 * math.pi * f / (fps * 0.7))
        if glow_pulse > 0:
            frame = np.clip(frame.astype(np.float32) * (1.0 + glow_pulse), 0, 255).astype(np.uint8)

        # Render floating golden dust particles in the warm sunset room
        for p_i in range(n_particles):
            py = int((particles_y[p_i] - f * particles_speed[p_i] * 1.5) % canvas_h)
            px = int((particles_x[p_i] + math.sin(f * 0.05 + p_i) * 15) % canvas_w)
            p_radius = 2 if p_i % 2 == 0 else 3
            p_alpha = 0.4 + 0.3 * math.sin(f * 0.1 + p_i)
            # Soft golden overlay
            overlay = frame.copy()
            cv2.circle(overlay, (px, py), p_radius, (120, 220, 255), -1, cv2.LINE_AA)
            cv2.addWeighted(overlay, p_alpha, frame, 1 - p_alpha, 0, frame)

        writer.write(frame)

    writer.release()

def main():
    print("=" * 60)
    print("🎬 VEO-GRAVITY SHOWCASE: ANIME CHARACTER VIDEO ENGINE")
    print("=" * 60)

    work_dir = Path("temp_veo_gravity")
    work_dir.mkdir(parents=True, exist_ok=True)
    out_path = Path("storage/veo_gravity_anime_showcase.mp4").resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Read image via PIL to handle any UTF-8 path safety
    pil_img = Image.open(IMAGE_PATH).convert("RGB")
    orig_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    print(f"Loaded generated anime art: {IMAGE_PATH.name} ({orig_img.shape[1]}x{orig_img.shape[0]})")

    print("\n[1/4] Tạo giọng đọc Tiếng Trung Xiaoxiao...")
    current_time = 0.0
    audio_files = []

    for sc in SCENES:
        idx = sc["id"]
        audio_p = work_dir / f"voice_{idx}.mp3"
        dur = asyncio.run(generate_speech(sc["cn"], audio_p, voice="zh-CN-XiaoxiaoNeural"))
        scene_dur = round(dur + 0.6, 2)
        sc["start"] = round(current_time, 2)
        sc["dur"] = scene_dur
        sc["audio"] = str(audio_p)
        audio_files.append(audio_p)
        print(f"  • Cảnh {idx} [{sc['title']}]: {scene_dur:.1f}s | {sc['cn'][:16]}...")
        current_time += scene_dur

    total_duration = round(current_time, 2)
    print(f"  -> Tổng thời lượng video: {total_duration:.2f}s")

    print("\n[2/4] Ghép âm thanh & Nhạc nền Lo-fi Ghibli...")
    concat_audio_txt = work_dir / "audio_list.txt"
    with open(concat_audio_txt, "w", encoding="utf-8") as f:
        for ap in audio_files:
            f.write(f"file '{ap.resolve().as_posix()}'\n")

    merged_voice = work_dir / "voice_merged.mp3"
    subprocess.run([
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_audio_txt),
        "-c", "copy", str(merged_voice)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    final_audio = work_dir / "final_audio.mp3"
    bgm_path = WORKSPACE_ROOT / "MoneyPrinterTurbo/resource/songs/output002.mp3"
    if bgm_path.exists():
        cmd_mix = [
            FFMPEG, "-y",
            "-i", str(merged_voice),
            "-stream_loop", "-1", "-i", str(bgm_path),
            "-filter_complex",
            f"[0:a]volume=1.0[voice];[1:a]volume=0.14[bgm];[voice][bgm]amix=inputs=2:duration=first[aout]",
            "-map", "[aout]",
            "-t", f"{total_duration:.2f}",
            str(final_audio)
        ]
        subprocess.run(cmd_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    else:
        final_audio = merged_voice

    print("\n[3/4] Render 4 phân cảnh Cinematic Camera Motion 30 FPS...")
    clip_files = []
    for sc in SCENES:
        idx = sc["id"]
        raw_clip = work_dir / f"raw_clip_{idx}.mp4"
        clean_clip = work_dir / f"clip_{idx}.mp4"

        render_cinematic_scene(orig_img, sc, raw_clip, fps=30)
        
        # Standardize codec with ffmpeg
        cmd_reencode = [
            FFMPEG, "-y",
            "-i", str(raw_clip),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-an",
            str(clean_clip)
        ]
        subprocess.run(cmd_reencode, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        clip_files.append(clean_clip)
        print(f"  ✓ Cinematic clip {idx} rendered: {sc['dur']:.1f}s (1080x1920 @ 30.00fps)")

    print("\n[4/4] Nối cảnh mượt mà & Đốt phụ đề Song Ngữ Trung - Việt...")
    inputs = []
    filter_inputs = ""
    for idx, cp in enumerate(clip_files):
        inputs.extend(["-i", str(cp)])
        filter_inputs += f"[{idx}:v]"

    concat_filter = f"{filter_inputs}concat=n={len(clip_files)}:v=1:a=0[vconcat]"
    
    ass_path = work_dir / "subtitles.ass"
    build_ass_subtitles(SCENES, ass_path)
    escaped_ass = str(ass_path.resolve()).replace("\\", "/").replace(":", "\\:")
    
    full_filter = f"{concat_filter};[vconcat]subtitles='{escaped_ass}'[vfinal]"

    cmd_final = [
        FFMPEG, "-y",
        *inputs,
        "-i", str(final_audio),
        "-filter_complex", full_filter,
        "-map", "[vfinal]",
        "-map", f"{len(clip_files)}:a",
        "-c:v", "libx264", "-crf", "19", "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(out_path)
    ]
    subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    print(f"\n🎉 Video hoàn thành: {out_path.name} ({out_path.stat().st_size / (1024*1024):.1f} MB)")

    # Save copy to Desktop
    desktop_copy = Path("C:/Users/User/Desktop/veo_gravity_anime_showcase.mp4")
    try:
        import shutil
        shutil.copy2(str(out_path), str(desktop_copy))
        print(f"💾 Đã lưu bản sao trên Desktop: {desktop_copy.name}")
    except Exception as e:
        print(f"Desktop notice: {e}")

    # Dispatch to Telegram Hub
    print("\n📤 Đang gửi video về Telegram Video Hub...")
    ok, res = dispatch_video(
        video_path=str(out_path),
        title="Veo-gravity Showcase: Hoạt Cảnh Anime Makoto Shinkai (0 VNĐ API)",
        description="Video anime chuyển động điện ảnh được sinh bởi năng lực đồ họa của Antigravity, kết hợp giọng đọc Xiaoxiao và phụ đề song ngữ.",
        app_name="Veo-gravity",
        tags=["VeoGravity", "AnimeShorts", "MakotoShinkai", "HocTiengTrung", "SongNgu9x16"],
        blocking=True
    )
    if ok:
        print(f"✅ {res}")
    else:
        print(f"⚠️ Dispatch notice: {res}")

if __name__ == "__main__":
    main()
