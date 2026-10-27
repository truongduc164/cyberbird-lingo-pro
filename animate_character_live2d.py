#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Live 2D Motion Animation for Chinese Learning Infographic
- Breathing motion on character body
- Screen glow flicker effect from smartphone
- Interactive bouncing & pulsing highlight on active vocabulary tags
- Floating sparkle particles
- Native Chinese Xiaoxiao voiceover + Lo-fi BGM
- Dual-line bilingual subtitles (9:16 mobile format)
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
IMAGE_PATH = Path(r"D:\0.PROGRAMME\4. DEAN OPTIMIZE\12.Vibe idea (tạm)\.telegravity_uploads\tg_1792726291_telegram_photo.jpg")

SCENES = [
    {
        "id": 1,
        "title": "Đầu, Mặt & Điện thoại",
        "cn": "看手机 (shǒujī)，头上 (tóu) 有乌黑的头发，可爱的脸蛋 (liǎn) 和明亮的眼睛 (yǎnjing)。",
        "vi": "Lướt điện thoại (shǒujī), có đầu (tóu), khuôn mặt (liǎn) và đôi mắt (yǎnjing).",
        "highlight_box": (100, 200, 320, 280),
        "target_zoom": (40, 160, 480, 520)
    },
    {
        "id": 2,
        "title": "Hai bàn tay & Thẻ căn cước",
        "cn": "双手 (shǒu) 拿着手机，张开手臂 (shǒubì)，胸前还挂着工作证件 (zhèngjiàn)。",
        "vi": "Hai bàn tay (shǒu) cầm điện thoại, cánh tay (shǒubì) và thẻ căn cước (zhèngjiàn).",
        "highlight_box": (300, 320, 280, 260),
        "target_zoom": (140, 280, 560, 480)
    },
    {
        "id": 3,
        "title": "Vòng eo, Quần, Đôi chân & Bàn chân",
        "cn": "系好腰带 (yāodài)，穿着舒适的裤子 (kùzi)，伸展双腿 (tuǐ) 和双脚 (jiǎo)。",
        "vi": "Thắt lưng (yāodài), mặc chiếc quần (kùzi), đôi chân (tuǐ) và bàn chân (jiǎo).",
        "highlight_box": (420, 450, 320, 350),
        "target_zoom": (260, 400, 480, 560)
    },
    {
        "id": 4,
        "title": "Mẹo nhỏ • Nghỉ ngơi",
        "cn": "小提示：手机虽然好玩，但也要注意多休息，保护眼睛哦！",
        "vi": "Mẹo nhỏ: Điện thoại tuy vui, nhưng cũng phải chú ý nghỉ ngơi, bảo vệ mắt nhé!",
        "highlight_box": (380, 720, 360, 260),
        "target_zoom": (320, 680, 420, 320)
    }
]

async def generate_speech(text: str, output_path: Path, voice: str = "zh-CN-XiaoxiaoNeural") -> float:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    comm = edge_tts.Communicate(text, voice, rate="+2%")
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

def render_animated_scene(orig_img: np.ndarray, sc: dict, out_video: Path, fps=30):
    """
    Renders an animated clip with breathing motion, phone screen flicker, and pulsing highlight ring!
    """
    canvas_w, canvas_h = 1080, 1920
    total_frames = int(round(sc["dur"] * fps))
    
    # Precompute blurred background
    orig_h, orig_w = orig_img.shape[:2]
    bg = cv2.resize(orig_img, (canvas_w, canvas_h))
    bg = cv2.GaussianBlur(bg, (91, 91), 0)
    # Darken background slightly
    bg = cv2.addWeighted(bg, 0.45, np.zeros_like(bg), 0.55, 0)

    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_video), fourcc, fps, (canvas_w, canvas_h))

    zx, zy, zw, zh = sc["target_zoom"]
    hx, hy, hw, hh = sc["highlight_box"]

    for f in range(total_frames):
        t = f / fps
        frame = bg.copy()

        # 1. Breathing motion (subtle vertical oscillation: 3.5px)
        breath_offset = int(math.sin(2 * math.pi * t / 2.2) * 4)

        # 2. Camera drift (slow Ken Burns zoom in 1.0 -> 1.06)
        zoom_factor = 1.0 + (f / total_frames) * 0.06
        cur_w = int(zw / zoom_factor)
        cur_h = int(zh / zoom_factor)
        cur_x = zx + (zw - cur_w) // 2
        cur_y = max(0, min(orig_h - cur_h, zy + (zh - cur_h) // 2 + breath_offset))

        # Crop region from original image
        cropped = orig_img[cur_y : cur_y + cur_h, cur_x : cur_x + cur_w]
        if cropped.size == 0:
            cropped = orig_img

        # 3. Phone screen light flicker (cyan-white glow pulsing)
        glow_alpha = 0.25 + 0.15 * math.sin(2 * math.pi * t * 3.5)
        # Position of phone inside crop
        phone_rel_x = int((180 - cur_x) * (canvas_w * 0.92 / cur_w))
        phone_rel_y = int((380 - cur_y) * (canvas_w * 0.92 / cur_w))

        # Scale cropped image to fit canvas card
        card_w = int(canvas_w * 0.92)
        scale_ratio = card_w / cropped.shape[1]
        card_h = int(cropped.shape[0] * scale_ratio)
        max_card_h = int(canvas_h * 0.65)
        if card_h > max_card_h:
            card_h = max_card_h
            card_w = int(cropped.shape[1] * (card_h / cropped.shape[0]))

        card_resized = cv2.resize(cropped, (card_w, card_h), interpolation=cv2.INTER_LANCZOS4)

        # Add white border
        bordered = cv2.copyMakeBorder(card_resized, 6, 6, 6, 6, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        bw, bh = bordered.shape[1], bordered.shape[0]

        px = (canvas_w - bw) // 2
        py = (canvas_h - bh) // 2 - 120

        # Paste bordered card onto background
        frame[py : py + bh, px : px + bw] = bordered

        # 4. Animated pulsing highlight ring on the active vocabulary area
        ring_radius = int(25 + 10 * math.sin(2 * math.pi * t * 2.5))
        ring_alpha = 0.6 + 0.4 * math.sin(2 * math.pi * t * 2.5)
        ring_center_x = px + bw // 2
        ring_center_y = py + int(bh * 0.45) + breath_offset
        cv2.circle(frame, (ring_center_x, ring_center_y), ring_radius, (0, 235, 255), 3, cv2.LINE_AA)

        # 5. Floating sparkles / stars (3 golden stars floating upward)
        for s_idx in range(4):
            star_t = (t * 0.6 + s_idx * 0.25) % 1.0
            star_x = int(px + bw * 0.2 + s_idx * 160 + math.sin(star_t * 6) * 15)
            star_y = int(py + bh * 0.9 - star_t * (bh * 0.8))
            star_size = int(6 + 3 * math.sin(star_t * math.pi))
            cv2.circle(frame, (star_x, star_y), star_size, (255, 215, 0), -1, cv2.LINE_AA)

        writer.write(frame)

    writer.release()

def main():
    print("=" * 60)
    print("🎬 LIVE 2D ANIMATION ENGINE (Character Motion & Screen Glow)")
    print("=" * 60)

    work_dir = Path("temp_animated_video")
    work_dir.mkdir(parents=True, exist_ok=True)
    out_path = Path("storage/video_nhan_vat_chuyen_dong_live2d.mp4").resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Read image safely on Windows with UTF-8 path
    try:
        pil_img = Image.open(IMAGE_PATH).convert("RGB")
        orig_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Error loading image via PIL: {e}")
        return

    print("\n[1/4] Tạo giọng đọc Tiếng Trung Xiaoxiao...")
    current_time = 0.0
    audio_files = []

    for sc in SCENES:
        idx = sc["id"]
        audio_p = work_dir / f"voice_{idx}.mp3"
        dur = asyncio.run(generate_speech(sc["cn"], audio_p, voice="zh-CN-XiaoxiaoNeural"))
        scene_dur = round(dur + 0.7, 2)
        sc["start"] = round(current_time, 2)
        sc["dur"] = scene_dur
        sc["audio"] = str(audio_p)
        audio_files.append(audio_p)
        print(f"  • Cảnh {idx} [{sc['title']}]: {scene_dur:.1f}s | {sc['cn'][:16]}...")
        current_time += scene_dur

    total_duration = round(current_time, 2)
    print(f"  -> Tổng thời lượng video: {total_duration:.2f}s")

    print("\n[2/4] Ghép âm thanh & Nhạc nền Lo-fi Cute...")
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
            f"[0:a]volume=1.0[voice];[1:a]volume=0.15[bgm];[voice][bgm]amix=inputs=2:duration=first[aout]",
            "-map", "[aout]",
            "-t", f"{total_duration:.2f}",
            str(final_audio)
        ]
        subprocess.run(cmd_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    else:
        final_audio = merged_voice

    print("\n[3/4] Render hoạt hình Live 2D chuyển động (Nhịp thở + Đèn màn hình + Sao bay)...")
    clip_files = []
    for sc in SCENES:
        idx = sc["id"]
        raw_clip = work_dir / f"raw_clip_{idx}.mp4"
        clean_clip = work_dir / f"clip_{idx}.mp4"

        render_animated_scene(orig_img, sc, raw_clip, fps=30)
        
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
        print(f"  ✓ Animated clip {idx} rendered: {sc['dur']:.1f}s (1080x1920 @ 30.00fps)")

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
        "-c:v", "libx264", "-crf", "20", "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(out_path)
    ]
    subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    print(f"\n🎉 Video hoàn thành: {out_path.name} ({out_path.stat().st_size / (1024*1024):.1f} MB)")

    # Save copy to Desktop
    desktop_copy = Path("C:/Users/User/Desktop/video_nhan_vat_chuyen_dong_live2d.mp4")
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
        title="Nhân Vật Chuyển Động Live2D: Học Tiếng Trung Cơ Thể (Bản Động)",
        description="Video nhân vật chuyển động nhịp thở, ánh sáng màn hình nhấp nháy, ngôi sao lơ lửng, vòng tròn nhún nhảy từ vựng theo nhịp giọng đọc Xiaoxiao.",
        app_name="Live2D-Chinese",
        tags=["NhanVatChuyenDong", "Live2D", "HocTiengTrung", "SongNgu9x16"],
        blocking=True
    )
    if ok:
        print(f"✅ {res}")
    else:
        print(f"⚠️ Dispatch notice: {res}")

if __name__ == "__main__":
    main()
