#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Douyin Viral 1M+ Views Format: Dual-Screen Visual Vocabulary Learning
- Upper Screen: 100% Original Infographic with animated spotlight pulse on active vocabulary
- Lower Screen: 100% Realistic Live Motion Footage (Real person phone, stretching, coffee)
- Native Chinese Voiceover (Xiaoxiao)
- Dual-line Subtitles (Chinese + Pinyin + Vietnamese)
- Safe Zone for 9:16 mobile display (1080x1920 @ 30.00fps)
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
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WORKSPACE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from telegram_video_hub import dispatch_video

FFMPEG = "ffmpeg"
IMAGE_PATH = Path(r"D:\0.PROGRAMME\4. DEAN OPTIMIZE\12.Vibe idea (tạm)\.telegravity_uploads\tg_1792726291_telegram_photo.jpg")
ASSETS_DIR = Path("realistic_assets")

SCENES = [
    {
        "id": 1,
        "title": "Mở đầu • Nhìn tranh học từ vựng",
        "cn": "学习中文，快乐每一天！看图学单词，生动又有趣。",
        "vi": "Học tiếng Trung, vui mỗi ngày! Nhìn tranh học từ vựng, vừa sinh động vừa dễ nhớ.",
        "video": str(ASSETS_DIR / "girl_phone.mp4"),
        "spotlight": None,
        "vocab_badge": "今日单词 • TỪ VỰNG HÔM NAY"
    },
    {
        "id": 2,
        "title": "Đầu, Mặt & Điện thoại",
        "cn": "躺在地上看手机 (shǒujī)，头 (tóu)，圆脸 (liǎn) 和眼睛 (yǎnjing)。",
        "vi": "Lướt điện thoại (shǒujī), đầu (tóu), khuôn mặt (liǎn) và đôi mắt (yǎnjing).",
        "video": str(ASSETS_DIR / "girl_phone.mp4"),
        "spotlight": (200, 380, 75),  # (x, y, radius) on original image
        "vocab_badge": "头 tóu (đầu) | 手机 shǒujī (điện thoại)"
    },
    {
        "id": 3,
        "title": "Bàn tay, Cánh tay & Thẻ căn cước",
        "cn": "双手 (shǒu) 拿着手机，张开手臂 (shǒubì)，胸前挂着证件 (zhèngjiàn)。",
        "vi": "Hai bàn tay (shǒu) cầm điện thoại, cánh tay (shǒubì) và thẻ căn cước (zhèngjiàn).",
        "video": str(ASSETS_DIR / "girl_phone.mp4"),
        "spotlight": (440, 520, 80),
        "vocab_badge": "手 shǒu (tay) | 证件 zhèngjiàn (thẻ)"
    },
    {
        "id": 4,
        "title": "Thắt lưng, Quần, Đôi chân & Bàn chân",
        "cn": "系好腰带 (yāodài)，穿着裤子 (kùzi)，伸展双腿 (tuǐ) 和双脚 (jiǎo)。",
        "vi": "Thắt lưng (yāodài), mặc quần (kùzi), đôi chân (tuǐ) và bàn chân (jiǎo).",
        "video": str(ASSETS_DIR / "stretching.mp4"),
        "spotlight": (580, 720, 95),
        "vocab_badge": "裤子 kùzi (quần) | 腿 tuǐ (chân) | 脚 jiǎo (bàn chân)"
    },
    {
        "id": 5,
        "title": "Mẹo nhỏ • Nghỉ ngơi & Thư giãn",
        "cn": "小提示：手机虽然好玩，也要注意多休息，喝杯水放松一下哦！",
        "vi": "Mẹo nhỏ: Điện thoại tuy vui, nhưng nhớ chú ý nghỉ ngơi, uống nước thư giãn nhé!",
        "video": str(ASSETS_DIR / "relaxing_coffee.mp4"),
        "spotlight": (680, 890, 85),
        "vocab_badge": "小提示 xiǎotíshì: Chú ý nghỉ ngơi!"
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
Style: Bilingual,Microsoft YaHei,52,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,4.0,2.0,2,40,40,160,1
Style: Badge,Microsoft YaHei,38,&H0000F5FF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,3.0,1.5,2,40,40,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    for sc in scenes:
        start_ts = format_ass_timestamp(sc["start"])
        end_ts = format_ass_timestamp(sc["start"] + sc["dur"])
        cn = sc["cn"]
        vi = sc["vi"]
        badge = sc["vocab_badge"]
        
        # Vocab badge line
        ass_content += f"Dialogue: 1,{start_ts},{end_ts},Badge,,0,0,0,,{{\\b1\\c&H0024E8FF}}🏷️ {badge}\n"
        # Subtitle lines
        text_line = f"{{\\b1\\c&H00FFFFFF\\fs52}}{cn}\\N{{\\b1\\c&H003CEBFF\\fs40}}{vi}"
        ass_content += f"Dialogue: 0,{start_ts},{end_ts},Bilingual,,0,0,0,,{text_line}\n"

    output_ass.write_text(ass_content, encoding="utf-8")

def prepare_upper_frame(orig_img: np.ndarray, spotlight=None, anim_t: float = 0.0) -> np.ndarray:
    """
    Renders the upper half (1080 x 860) containing the 100% original infographic
    with optional pulsing spotlight circle on the target vocabulary.
    """
    card_w, card_h = 1080, 860
    canvas = np.full((card_h, card_w, 3), (25, 25, 30), dtype=np.uint8)

    # Scale original image (768x1024) to fit within 1040 x 820
    orig_h, orig_w = orig_img.shape[:2]
    scale = min(1040 / orig_w, 820 / orig_h)
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)
    resized_orig = cv2.resize(orig_img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

    # Add stylish rounded white card border
    bordered = cv2.copyMakeBorder(resized_orig, 4, 4, 4, 4, cv2.BORDER_CONSTANT, value=[255, 255, 255])
    bw, bh = bordered.shape[1], bordered.shape[0]

    px = (card_w - bw) // 2
    py = (card_h - bh) // 2

    canvas[py : py + bh, px : px + bw] = bordered

    # Draw pulsing spotlight circle on active vocabulary location
    if spotlight:
        sx, sy, sr = spotlight
        # Transform coords to canvas
        target_cx = px + int(sx * scale)
        target_cy = py + int(sy * scale)
        pulse_r = int(sr * scale + 10 * math.sin(anim_t * 6.0))
        alpha = 0.7 + 0.3 * math.sin(anim_t * 6.0)

        overlay = canvas.copy()
        # Glowing radar ring
        cv2.circle(overlay, (target_cx, target_cy), pulse_r, (0, 235, 255), 4, cv2.LINE_AA)
        cv2.circle(overlay, (target_cx, target_cy), int(pulse_r * 0.7), (0, 165, 255), 2, cv2.LINE_AA)
        cv2.addWeighted(overlay, alpha, canvas, 1 - alpha, 0, canvas)

    return canvas

def render_dual_screen_scene(orig_img: np.ndarray, sc: dict, out_video: Path, fps=30):
    """
    Renders 1080x1920 composite frame:
    - Top (y=0 to 860): 100% Original Infographic with active spotlight
    - Divider & Label (y=860 to 930): Banner "THỰC HÀNH CỬ ĐỘNG THỰC TẾ"
    - Bottom (y=930 to 1650): 100% Realistic Live Motion Video
    - Bottom Area (y=1650 to 1920): Subtitles safe zone
    """
    canvas_w, canvas_h = 1080, 1920
    total_frames = int(round(sc["dur"] * fps))

    # Open lower realistic video
    cap = cv2.VideoCapture(sc["video"])
    if not cap.isOpened():
        print(f"Warning: Cannot open video {sc['video']}")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_video), fourcc, fps, (canvas_w, canvas_h))

    lower_w, lower_h = 1040, 720
    lower_px = (canvas_w - lower_w) // 2
    lower_py = 930

    for f in range(total_frames):
        t = f / fps
        frame = np.full((canvas_h, canvas_w, 3), (18, 18, 22), dtype=np.uint8)

        # 1. Render Upper Screen (Original Infographic)
        upper_canvas = prepare_upper_frame(orig_img, sc["spotlight"], anim_t=t)
        frame[0 : 860, 0 : canvas_w] = upper_canvas

        # 2. Render Divider Banner
        banner_y = 875
        cv2.rectangle(frame, (40, banner_y), (canvas_w - 40, banner_y + 40), (35, 35, 45), -1)
        cv2.rectangle(frame, (40, banner_y), (canvas_w - 40, banner_y + 40), (0, 215, 255), 2)
        cv2.putText(
            frame,
            "▶ CHUYEN DONG CHAN THUC • REAL-LIFE MOTION",
            (canvas_w // 2 - 270, banner_y + 27),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 240, 255),
            2,
            cv2.LINE_AA
        )

        # 3. Render Lower Screen (Realistic Motion Footage)
        ret, vframe = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, vframe = cap.read()

        if ret and vframe is not None:
            # Crop to 1040:720 ratio and resize
            vh, vw = vframe.shape[:2]
            target_ratio = lower_w / lower_h
            cur_ratio = vw / vh

            if cur_ratio > target_ratio:
                # Video is wider than target -> crop sides
                crop_w = int(vh * target_ratio)
                start_x = (vw - crop_w) // 2
                cropped_vf = vframe[:, start_x : start_x + crop_w]
            else:
                crop_h = int(vw / target_ratio)
                start_y = (vh - crop_h) // 2
                cropped_vf = vframe[start_y : start_y + crop_h, :]

            resized_vf = cv2.resize(cropped_vf, (lower_w - 8, lower_h - 8), interpolation=cv2.INTER_LANCZOS4)
            bordered_vf = cv2.copyMakeBorder(resized_vf, 4, 4, 4, 4, cv2.BORDER_CONSTANT, value=[255, 255, 255])
            
            frame[lower_py : lower_py + lower_h, lower_px : lower_px + lower_w] = bordered_vf

        writer.write(frame)

    cap.release()
    writer.release()

def main():
    print("=" * 60)
    print("🎬 DOUYIN 1M+ VIEWS FORMAT: DUAL-SCREEN VISUAL VOCABULARY")
    print("=" * 60)

    work_dir = Path("temp_douyin_masterpiece")
    work_dir.mkdir(parents=True, exist_ok=True)
    out_path = Path("storage/video_douyin_trieu_view_song_ngu.mp4").resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Read original image safely via PIL
    pil_img = Image.open(IMAGE_PATH).convert("RGB")
    orig_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    print(f"Loaded original image: {IMAGE_PATH.name} ({orig_img.shape[1]}x{orig_img.shape[0]})")

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

    print("\n[2/4] Ghép âm thanh & Nhạc nền Lo-fi Douyin...")
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

    print("\n[3/4] Render 5 phân cảnh Dual-Screen (Ảnh nguyên tác + Video thật 30 FPS)...")
    clip_files = []
    for sc in SCENES:
        idx = sc["id"]
        raw_clip = work_dir / f"raw_clip_{idx}.mp4"
        clean_clip = work_dir / f"clip_{idx}.mp4"

        render_dual_screen_scene(orig_img, sc, raw_clip, fps=30)
        
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
        print(f"  ✓ Dual-screen clip {idx} rendered: {sc['dur']:.1f}s (1080x1920 @ 30.00fps)")

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
    desktop_copy = Path("C:/Users/User/Desktop/video_douyin_trieu_view_song_ngu.mp4")
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
        title="Định Dạng Douyin Triệu View: Tranh Nguyên Tác + Video Thật Chuyển Động (Song Ngữ)",
        description="Màn hình chia đôi: Nửa trên giữ 100% tranh nguyên tác có radar phát sáng định vị từ vựng; Nửa dưới là video người thật chuyển động chân thực 100%.",
        app_name="Douyin-VisualPro",
        tags=["DouyinTrieuView", "TranhNguyenTac", "VideoThatChuyenDong", "HocTiengTrung", "SongNgu9x16"],
        blocking=True
    )
    if ok:
        print(f"✅ {res}")
    else:
        print(f"⚠️ Dispatch notice: {res}")

if __name__ == "__main__":
    main()
