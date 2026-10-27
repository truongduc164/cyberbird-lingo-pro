#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Douyin Full-Screen Intercut Pipeline (Chuyển Cảnh Toàn Màn Hình Đan Xen)
- Zero Split-Screen (Khắc phục hoàn toàn lỗi chia đôi gây mỏi mắt/xấu trải nghiệm)
- 100% Full-Screen 9:16 (1080x1920) tràn viền sống động
- Đan xen nhịp nhàng giữa:
    + Cận cảnh Tranh Minh Họa Gốc (phóng to từ vựng, có radar phát sáng)
    + Video Đời Thực Chuyển Động Chân Thực (toàn màn hình 1080x1920)
- Giọng đọc bản xứ tiếng Trung (Xiaoxiao)
- Phụ đề song ngữ Tiếng Trung + Pinyin + Tiếng Việt
- Gửi trực tiếp về Telegram Bot
"""

import os
import sys
import math
import asyncio
from pathlib import Path
import subprocess
import numpy as np
import cv2
from PIL import Image, ImageFilter
import edge_tts

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
        "title": "Mở đầu • Toàn cảnh tranh",
        "cn": "学习中文，快乐每一天！看图学单词，生动又有趣。",
        "vi": "Học tiếng Trung, vui mỗi ngày! Nhìn tranh học từ vựng, vừa sinh động vừa dễ nhớ.",
        "crop": "full",
        "real_video": str(ASSETS_DIR / "girl_phone.mp4"),
        "vocab_badge": "今日单词 • TỪ VỰNG HÔM NAY",
        "split_ratio": 0.45  # 45% infographic zoom, 55% real video
    },
    {
        "id": 2,
        "title": "Đầu, Mặt & Điện thoại",
        "cn": "躺在地上看手机 (shǒujī)，头 (tóu)，圆脸 (liǎn) 和眼睛 (yǎnjing)。",
        "vi": "Lướt điện thoại (shǒujī), đầu (tóu), khuôn mặt (liǎn) và đôi mắt (yǎnjing).",
        "crop": (30, 200, 520, 500),
        "real_video": str(ASSETS_DIR / "girl_phone.mp4"),
        "vocab_badge": "头 tóu (đầu) | 手机 shǒujī (điện thoại)",
        "split_ratio": 0.50
    },
    {
        "id": 3,
        "title": "Bàn tay, Cánh tay & Thẻ căn cước",
        "cn": "双手 (shǒu) 拿着手机，张开手臂 (shǒubì)，胸前挂着证件 (zhèngjiàn)。",
        "vi": "Hai bàn tay (shǒu) cầm điện thoại, cánh tay (shǒubì) và thẻ căn cước (zhèngjiàn).",
        "crop": (150, 360, 580, 440),
        "real_video": str(ASSETS_DIR / "girl_phone.mp4"),
        "vocab_badge": "手 shǒu (tay) | 证件 zhèngjiàn (thẻ)",
        "split_ratio": 0.50
    },
    {
        "id": 4,
        "title": "Thắt lưng, Quần, Đôi chân & Bàn chân",
        "cn": "系好腰带 (yāodài)，穿着裤子 (kùzi)，伸展双腿 (tuǐ) 和双脚 (jiǎo)。",
        "vi": "Thắt lưng (yāodài), mặc quần (kùzi), đôi chân (tuǐ) và bàn chân (jiǎo).",
        "crop": (300, 430, 468, 590),
        "real_video": str(ASSETS_DIR / "stretching.mp4"),
        "vocab_badge": "裤子 kùzi (quần) | 腿 tuǐ (chân) | 脚 jiǎo (bàn chân)",
        "split_ratio": 0.48
    },
    {
        "id": 5,
        "title": "Mẹo nhỏ • Nghỉ ngơi & Thư giãn",
        "cn": "手机虽然好玩，但不要忘记休息哦，保持健康最重要！",
        "vi": "Điện thoại tuy vui, nhưng đừng quên nghỉ ngơi nhé, giữ gìn sức khỏe là trên hết!",
        "crop": (360, 710, 400, 310),
        "real_video": str(ASSETS_DIR / "relaxing_coffee.mp4"),
        "vocab_badge": "小提示 • LỜI KHUYÊN NGHỈ NGƠI",
        "split_ratio": 0.45
    }
]

def get_audio_duration(file_path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return float(res.stdout.strip())

async def generate_voiceovers(work_dir: Path):
    voice = "zh-CN-XiaoxiaoNeural"
    durations = []
    for s in SCENES:
        out_f = work_dir / f"voice_{s['id']}.mp3"
        if not out_f.exists() or out_f.stat().st_size < 1000:
            communicate = edge_tts.Communicate(s["cn"], voice, rate="-4%")
            await communicate.save(str(out_f))
        dur = get_audio_duration(out_f)
        durations.append(dur)
        print(f"  • Scene {s['id']}: {dur:.2f}s | {s['title']}")
    return durations

def create_fullscreen_graphic_frame(orig_pil: Image.Image, crop_box, progress: float, badge_text: str) -> np.ndarray:
    """
    Renders 1080x1920 full-screen frame with cropped graphic element,
    smooth subtle Ken Burns zoom, soft ambient background, and glowing badge.
    """
    canvas_w, canvas_h = 1080, 1920
    
    # 1. Background: blurred ambient fill from original image
    bg = orig_pil.resize((canvas_w, canvas_h), Image.Resampling.BICUBIC)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=35))
    
    # Darken background slightly for contrast
    bg_cv = cv2.cvtColor(np.array(bg), cv2.COLOR_RGB2BGR)
    bg_cv = (bg_cv.astype(np.float32) * 0.40).astype(np.uint8)
    
    # 2. Main Cropped Graphic Subject
    if crop_box == "full":
        sub_pil = orig_pil
    else:
        x, y, w, h = crop_box
        sub_pil = orig_pil.crop((x, y, x + w, y + h))
    
    # Subtle zoom scale (1.0 to 1.05)
    zoom = 1.0 + 0.05 * progress
    
    # Fit into safe middle area (max 1000x1200)
    max_w, max_h = 1000, 1250
    aspect = sub_pil.width / sub_pil.height
    if aspect > (max_w / max_h):
        target_w = int(max_w * zoom)
        target_h = int(target_w / aspect)
    else:
        target_h = int(max_h * zoom)
        target_w = int(target_h * aspect)
        
    sub_resized = sub_pil.resize((target_w, target_h), Image.Resampling.LANCZOS)
    sub_cv = cv2.cvtColor(np.array(sub_resized), cv2.COLOR_RGB2BGR)
    
    # Rounded Card Frame with subtle glowing neon border
    card_h, card_w = sub_cv.shape[:2]
    pos_x = (canvas_w - card_w) // 2
    pos_y = 220 + (1250 - card_h) // 2
    
    # Ensure bounds
    pos_x = max(0, min(pos_x, canvas_w - card_w))
    pos_y = max(180, min(pos_y, canvas_h - card_h - 260))
    
    # Draw soft outer glow behind card
    glow_color = (255, 215, 0) # Gold glow
    cv2.rectangle(bg_cv, (pos_x - 6, pos_y - 6), (pos_x + card_w + 6, pos_y + card_h + 6), (40, 40, 40), -1)
    
    # Paste card onto background
    bg_cv[pos_y:pos_y+card_h, pos_x:pos_x+card_w] = sub_cv
    
    # Border
    cv2.rectangle(bg_cv, (pos_x, pos_y), (pos_x + card_w, pos_y + card_h), (0, 235, 255), 3, lineType=cv2.LINE_AA)
    
    # Active Vocab Badge Banner above subtitles (y=1500)
    cv2.rectangle(bg_cv, (100, 1490), (980, 1565), (10, 20, 30), -1)
    cv2.rectangle(bg_cv, (100, 1490), (980, 1565), (0, 235, 255), 2, lineType=cv2.LINE_AA)
    cv2.putText(bg_cv, badge_text, (130, 1540),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2, lineType=cv2.LINE_AA)
                
    return bg_cv

def render_scene_intercut_video(scene: dict, total_dur: float, orig_pil: Image.Image, work_dir: Path) -> Path:
    """
    Renders one full-screen scene clip:
    - First half: 100% full-screen graphic zoom
    - Second half: 100% full-screen realistic stock clip
    Both share the SAME 1080x1920 canvas, smoothly alternating!
    """
    scene_id = scene["id"]
    out_clip = work_dir / f"intercut_scene_{scene_id}.mp4"
    if out_clip.exists() and out_clip.stat().st_size > 100000:
        return out_clip
        
    fps = 30
    total_frames = int(round(total_dur * fps))
    graphic_ratio = scene.get("split_ratio", 0.5)
    graphic_frames = int(round(total_frames * graphic_ratio))
    real_frames = total_frames - graphic_frames
    
    # Temp intermediate clips
    part_graphic = work_dir / f"temp_graphic_{scene_id}.mp4"
    part_real = work_dir / f"temp_real_{scene_id}.mp4"
    
    # 1. Render Graphic Frames
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    vw = cv2.VideoWriter(str(part_graphic), fourcc, fps, (1080, 1920))
    for f in range(graphic_frames):
        p = f / max(1, graphic_frames - 1)
        frame_bgr = create_fullscreen_graphic_frame(orig_pil, scene["crop"], p, scene["vocab_badge"])
        vw.write(frame_bgr)
    vw.release()
    
    # 2. Render Realistic Clip (Scale & Center Crop to 1080x1920)
    real_dur = real_frames / fps
    real_src = Path(scene["real_video"])
    
    # Filter: Scale to fill 1080x1920 + Crop center (Clean & Fast)
    real_filter = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1"
    
    cmd_real = [
        FFMPEG, "-y",
        "-ss", "1.0",
        "-i", str(real_src),
        "-t", f"{real_dur:.3f}",
        "-vf", real_filter,
        "-r", str(fps),
        "-c:v", "libx264", "-crf", "18", "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        "-an",
        str(part_real)
    ]
    subprocess.run(cmd_real, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    # 3. Concatenate Part Graphic & Part Real
    cmd_concat = [
        FFMPEG, "-y",
        "-i", str(part_graphic),
        "-i", str(part_real),
        "-filter_complex", "[0:v]fps=30,setpts=PTS-STARTPTS[v0];[1:v]fps=30,setpts=PTS-STARTPTS[v1];[v0][v1]concat=n=2:v=1:a=0[vout]",
        "-map", "[vout]",
        "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        str(out_clip)
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    # Clean temp files
    try:
        part_graphic.unlink(missing_ok=True)
        part_real.unlink(missing_ok=True)
    except Exception:
        pass
        
    return out_clip

def build_ass_subtitles(scenes, durations, out_file: Path):
    """
    Subtitles positioned in the bottom safe zone (MarginV=180).
    Clean, bold typography:
    - Line 1: Chinese Hanzi + Pinyin hint (Bright White)
    - Line 2: Vietnamese Translation (Cyan Gold)
    - Top: Badge indicator
    """
    header = """[Script Info]
Title: Douyin FullScreen Intercut Vocab Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Segoe UI,52,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,4,2,2,60,60,180,1
Style: PinyinLine,Segoe UI,40,&H003CEBFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,3,1,2,60,60,260,1
Style: TopBadge,Segoe UI,34,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,3,1,8,60,60,100,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    current_time = 0.0

    def fmt_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds - int(seconds)) * 100)
        return f"{h:01d}:{m:02d}:{s:02d}.{cs:02d}"

    for s, dur in zip(scenes, durations):
        split_ratio = s.get("split_ratio", 0.5)
        graphic_dur = dur * split_ratio
        
        t0 = fmt_time(current_time)
        t_mid = fmt_time(current_time + graphic_dur)
        t1 = fmt_time(current_time + dur)
        
        cn_text = s["cn"]
        vi_text = s["vi"]

        # Subtitles persistent during whole scene
        events.append(f"Dialogue: 0,{t0},{t1},PinyinLine,,0,0,260,,{cn_text}")
        events.append(f"Dialogue: 0,{t0},{t1},Default,,0,0,180,,{vi_text}")
        
        # Dynamic Top Badge: Graphic vs Real Action
        events.append(f"Dialogue: 1,{t0},{t_mid},TopBadge,,0,0,100,,🎨 TRANH MINH HỌA • INFOGRAPHIC")
        events.append(f"Dialogue: 1,{t_mid},{t1},TopBadge,,0,0,100,,▶ CHUYỂN ĐỘNG THỰC TẾ • REAL-LIFE MOTION")

        current_time += dur

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events))

def main():
    print("=" * 70)
    print("🎬 KHOI TAO VIDEO TOAN MAN HINH (FULL-SCREEN INTERCUT)")
    print("   -> Loai bo 100% man hinh chia doi")
    print("   -> Dan xen toan man hinh: Tranh can canh <--> Video nguoi that")
    print("=" * 70)
    
    work_dir = WORKSPACE_ROOT / "temp_fullscreen_intercut"
    work_dir.mkdir(exist_ok=True)
    
    # Load original image with PIL
    orig_pil = Image.open(IMAGE_PATH).convert("RGB")
    print(f"✔ Da tai anh goc: {IMAGE_PATH.name} ({orig_pil.width}x{orig_pil.height})")
    
    # 1. Voiceovers
    print("\n[1/4] Tao giong doc tieng Trung...")
    durations = asyncio.run(generate_voiceovers(work_dir))
    
    # Concatenate voiceovers
    voice_files = [work_dir / f"voice_{s['id']}.mp3" for s in SCENES]
    audio_list_file = work_dir / "audio_list.txt"
    with open(audio_list_file, "w", encoding="utf-8") as f:
        for vf in voice_files:
            f.write(f"file '{vf.resolve().as_posix()}'\n")
            
    final_audio = work_dir / "final_audio.mp3"
    subprocess.run([
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", str(audio_list_file),
        "-c", "copy",
        str(final_audio)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"✔ Da ghep xong audio ({get_audio_duration(final_audio):.2f}s)")
    
    # 2. Render each scene clip with Full-Screen Intercut
    print("\n[2/4] Render cac doan video toan man hinh dan xen...")
    scene_clips = []
    for s, dur in zip(SCENES, durations):
        print(f"  • Xu ly Scene {s['id']}: {s['title']} ({dur:.2f}s)...")
        clip = render_scene_intercut_video(s, dur, orig_pil, work_dir)
        scene_clips.append(clip)
        
    # 3. Concatenate Scenes & Apply ASS Subtitles
    print("\n[3/4] Ghep noi va ep phu de song ngu toan man hinh...")
    ass_path = work_dir / "subtitles.ass"
    build_ass_subtitles(SCENES, durations, ass_path)
    escaped_ass = str(ass_path.resolve()).replace("\\", "/").replace(":", "\\:")
    
    inputs = []
    filter_inputs = ""
    for idx, c in enumerate(scene_clips):
        inputs.extend(["-i", str(c)])
        filter_inputs += f"[{idx}:v]fps=30,setpts=PTS-STARTPTS[v{idx}];"
        
    concat_filter = f"{filter_inputs}" + "".join([f"[v{i}]" for i in range(len(scene_clips))]) + f"concat=n={len(scene_clips)}:v=1:a=0[vconcat]"
    full_filter = f"{concat_filter};[vconcat]subtitles='{escaped_ass}'[vfinal]"
    
    out_dir = WORKSPACE_ROOT / "storage"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "video_fullscreen_intercut_song_ngu.mp4"
    
    cmd_final = [
        FFMPEG, "-y",
        *inputs,
        "-i", str(final_audio),
        "-filter_complex", full_filter,
        "-map", "[vfinal]",
        "-map", f"{len(scene_clips)}:a",
        "-c:v", "libx264", "-crf", "19", "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(out_path)
    ]
    subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"\n🎉 Xuat video toan man hinh thanh cong: {out_path.name} ({size_mb:.1f} MB)")
    
    # Save copy to Desktop
    desktop_copy = Path("C:/Users/User/Desktop/video_fullscreen_intercut_song_ngu.mp4")
    try:
        import shutil
        shutil.copy2(str(out_path), str(desktop_copy))
        print(f"💾 Da luu ban sao tren Desktop: {desktop_copy.name}")
    except Exception as e:
        pass
        
    # 4. Dispatch to Telegram Video Hub
    print("\n[4/4] Gui video ve Telegram Video Hub...")
    ok, res = dispatch_video(
        video_path=str(out_path),
        title="Định Dạng Toàn Màn Hình Đan Xen (Zero Split-Screen)",
        description="Khắc phục hoàn toàn lỗi chia đôi: 100% toàn màn hình 9:16 tràn viền, chuyển cảnh nhịp nhàng giữa Cận cảnh tranh nguyên tác và Video người thật chuyển động chân thực.",
        app_name="Douyin-FullScreenIntercut",
        tags=["FullScreen", "ZeroSplitScreen", "TranhNguyenTac", "VideoThatChuyenDong", "SongNgu9x16"],
        blocking=True
    )
    if ok:
        print(f"✅ {res}")
    else:
        print(f"⚠️ Dispatch notice: {res}")

if __name__ == "__main__":
    main()
