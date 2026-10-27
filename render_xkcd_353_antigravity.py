#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XKCD 353 "Python & import antigravity" Animated Masterpiece
============================================================
- Phóng tác hoạt hình 100% từ truyện tranh kinh điển xkcd.com/353
- Bối cảnh: Bầu trời xanh dịu, mây trắng bồng bềnh, mặt đất cỏ mộc mạc
- Nhân vật người que XKCD:
    + Guy 1: Đứng dưới đất ngước nhìn lên đầy kinh ngạc
    + Guy 2: Bay lơ lửng bồng bềnh trên trời nhờ Python, tà áo bay trong gió
- Lồng tiếng đối thoại 2 nhân vật (Guy 1 & Guy 2) với giọng bản xứ chuẩn
- Phụ đề 2 dòng chuẩn: TRÊN TRUNG - DƯỚI VIỆT (Segoe UI Bold không lỗi font)
- Cú twist đoạn kết: "import antigravity" phóng vút lên vũ trụ!
- Xuất 1080x1920 (9:16) @ 30fps -> Gửi thẳng về Telegram bot.
"""

import os
import sys
import math
import wave
import asyncio
from pathlib import Path
import subprocess
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont
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
WORK_DIR = WORKSPACE_ROOT / "temp_xkcd_353"
WORK_DIR.mkdir(exist_ok=True)
OUT_DIR = WORKSPACE_ROOT / "storage"
OUT_DIR.mkdir(exist_ok=True)

FONT_YAHEI_BOLD = r"C:\Windows\Fonts\msyhbd.ttc" if Path(r"C:\Windows\Fonts\msyhbd.ttc").exists() else r"C:\Windows\Fonts\msyh.ttc"
FONT_VI_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_VI_REGULAR = r"C:\Windows\Fonts\segoeui.ttf"

SCENES = [
    {
        "id": 1,
        "title": "Panel 1 • Sao cậu bay được vậy?",
        "parts": [
            {
                "speaker": "guy1",
                "audio": "s1_v1.mp3",
                "cn": "你居然在飞！你怎么做到的？",
                "vi": "Cậu đang bay kìa! Sao cậu làm được vậy?"
            },
            {
                "speaker": "guy2",
                "audio": "s1_v2.mp3",
                "cn": "因为Python啊！",
                "vi": "Nhờ Python đó!"
            }
        ]
    },
    {
        "id": 2,
        "title": "Panel 2 • Học Python tối qua",
        "parts": [
            {
                "speaker": "guy2",
                "audio": "s2_v1.mp3",
                "cn": "我昨晚刚学！打印Hello World只要一行代码！",
                "vi": "Tớ mới học tối qua! In Hello World chỉ cần đúng 1 dòng!"
            },
            {
                "speaker": "guy1",
                "audio": "s2_v2.mp3",
                "cn": "真的假的？编程有这么容易吗？",
                "vi": "Thật không vậy? Lập trình có dễ vậy sao?"
            }
        ]
    },
    {
        "id": 3,
        "title": "Panel 3 • Sao cậu bay được cơ chứ?",
        "parts": [
            {
                "speaker": "guy2",
                "audio": "s3_v1.mp3",
                "cn": "快上来吧！编程变快乐了，上面是全新的世界！",
                "vi": "Lên đây đi! Lập trình vui trở lại rồi, trên này sướng lắm!"
            },
            {
                "speaker": "guy1",
                "audio": "s3_v2.mp3",
                "cn": "但你到底是怎么飞起来的？！",
                "vi": "Nhưng quan trọng là... sao cậu BAY được cơ chứ?!"
            }
        ]
    },
    {
        "id": 4,
        "title": "Panel 4 • Cú Twist: import antigravity",
        "parts": [
            {
                "speaker": "guy2",
                "audio": "s4_v1.mp3",
                "cn": "我刚才只输入了一行代码：import antigravity！",
                "vi": "Tớ chỉ vừa gõ đúng một dòng: import antigravity!"
            },
            {
                "speaker": "guy1",
                "audio": "s4_v2.mp3",
                "cn": "就这么简单？！",
                "vi": "Chỉ có vậy thôi á?!"
            },
            {
                "speaker": "guy2_rocket",
                "audio": "s4_v3.mp3",
                "cn": "其实我还吃了药箱里的药片…但我相信绝对是Python的功劳！",
                "vi": "Thực ra tớ có uống thử mấy viên thuốc… nhưng tớ tin chắc là do Python!"
            }
        ]
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

# ==========================================
# DRAWING XKCD STICKMAN COMIC CANVAS
# ==========================================

def draw_xkcd_background(draw: ImageDraw.ImageDraw, f: int, w: int = 1080, h: int = 1920):
    ground_y = 1450

    # 1. Sky Gradient (Soft pastel sky blue)
    for y in range(0, ground_y, 4):
        p = y / float(ground_y)
        r = int(225 - 25 * p)
        g = int(240 - 15 * p)
        b = int(252 - 10 * p)
        draw.rectangle([0, y, w, y + 4], fill=(r, g, b))

    # 2. Drifting Soft Cartoon Clouds
    clouds = [
        (150, 280, 160),
        (720, 220, 220),
        (400, 480, 180),
        (880, 620, 140)
    ]
    for idx, (cx, cy, cw) in enumerate(clouds):
        drift_x = int(cx + (f * 0.4 * (idx + 1)) % (w + 200) - 100)
        ch = int(cw * 0.45)
        # White cloud puffs
        draw.ellipse([drift_x - cw // 2, cy - ch // 2, drift_x + cw // 2, cy + ch // 2], fill=(255, 255, 255, 240))
        draw.ellipse([drift_x - cw // 4, cy - ch, drift_x + cw // 4, cy], fill=(255, 255, 255, 240))

    # 3. Ground & Grass
    draw.rectangle([0, ground_y, w, h], fill=(235, 240, 230))
    draw.line([(0, ground_y), (w, ground_y)], fill=(34, 40, 48), width=5)

    # Cute sketchy grass tufts
    for gx in [120, 240, 380, 520, 680, 840, 960]:
        draw.line([(gx, ground_y), (gx - 12, ground_y - 20)], fill=(34, 40, 48), width=3)
        draw.line([(gx, ground_y), (gx, ground_y - 28)], fill=(34, 40, 48), width=3)
        draw.line([(gx, ground_y), (gx + 12, ground_y - 22)], fill=(34, 40, 48), width=3)

def draw_guy1_ground(draw: ImageDraw.ImageDraw, f: int, is_speaking: bool, mood: str = "normal"):
    """Guy 1 stands on the ground looking UP at Guy 2 in the sky"""
    ground_y = 1450
    cx = 280
    cy = 1180
    r = 55

    # Head looking up (angled tilted neck)
    neck_x, neck_y = cx, cy + r + 15
    draw.line([(neck_x, neck_y), (neck_x, ground_y - 120)], fill=(20, 24, 34), width=10) # torso
    # Legs
    draw.line([(neck_x, ground_y - 120), (neck_x - 45, ground_y)], fill=(20, 24, 34), width=10)
    draw.line([(neck_x, ground_y - 120), (neck_x + 45, ground_y)], fill=(20, 24, 34), width=10)

    # Head
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255), outline=(20, 24, 34), width=8)

    # Eyes looking UP towards Guy 2
    draw.ellipse([cx - 20, cy - 35, cx - 6, cy - 15], fill=(20, 24, 34))
    draw.ellipse([cx + 6, cy - 35, cx + 20, cy - 15], fill=(20, 24, 34))

    # Mouth
    if is_speaking:
        mouth_ph = (f % 12)
        if mouth_ph < 6:
            draw.ellipse([cx - 14, cy + 10, cx + 14, cy + 30], fill=(20, 24, 34))
        else:
            draw.line([(cx - 15, cy + 20), (cx + 15, cy + 20)], fill=(20, 24, 34), width=6)
    else:
        draw.arc([cx - 15, cy + 10, cx + 15, cy + 28], 0, 180, fill=(20, 24, 34), width=5) # perplexed

    # Arms gesturing up towards Guy 2
    if is_speaking:
        arm_bounce = int(math.sin(f * 0.4) * 8)
        draw.line([(neck_x, neck_y + 30), (neck_x + 60, neck_y - 40 + arm_bounce)], fill=(20, 24, 34), width=8)
        draw.line([(neck_x, neck_y + 30), (neck_x - 40, neck_y + 60)], fill=(20, 24, 34), width=8)
    else:
        draw.line([(neck_x, neck_y + 30), (neck_x + 50, neck_y - 20)], fill=(20, 24, 34), width=8)
        draw.line([(neck_x, neck_y + 30), (neck_x - 30, neck_y + 70)], fill=(20, 24, 34), width=8)

def draw_guy2_sky(draw: ImageDraw.ImageDraw, f: int, is_speaking: bool, mood: str = "normal", rocket_boost: float = 0.0):
    """Guy 2 floats peacefully in the sky with superman posture & flutter cape"""
    cx = 750
    base_cy = 620
    float_bob = int(math.sin(f * 0.22) * 22)
    # If rocket boost in panel 4, fly straight UP!
    rocket_y_offset = int(rocket_boost * 900)
    cy = base_cy + float_bob - rocket_y_offset
    r = 60

    # Fluttering Superhero Cape
    cape_x = cx - 60
    cape_y = cy + 40
    cape_flutter = int(math.sin(f * 0.4) * 16)
    draw.polygon([(cx - 20, cy + 20), (cape_x - 90 + cape_flutter, cape_y + 110), (cape_x - 40, cape_y + 130), (cx, cy + 60)], fill=(239, 68, 68), outline=(20, 24, 34), width=4)

    # Torso (floating horizontal/angled superman posture)
    draw.line([(cx, cy + r), (cx - 70, cy + r + 130)], fill=(20, 24, 34), width=12)

    # Legs trailing behind
    draw.line([(cx - 70, cy + r + 130), (cx - 150, cy + r + 160)], fill=(20, 24, 34), width=10)
    draw.line([(cx - 70, cy + r + 130), (cx - 130, cy + r + 200)], fill=(20, 24, 34), width=10)

    # Arms spread wide like an eagle!
    draw.line([(cx - 20, cy + r + 30), (cx + 80, cy + r - 30)], fill=(20, 24, 34), width=10) # front arm pointing
    draw.line([(cx - 40, cy + r + 30), (cx - 110, cy + r + 10)], fill=(20, 24, 34), width=10) # back arm

    # Head
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255), outline=(20, 24, 34), width=8)

    # Serene confident eyes looking down at Guy 1
    draw.arc([cx - 30, cy - 18, cx - 10, cy], 180, 360, fill=(20, 24, 34), width=6)
    draw.arc([cx + 5, cy - 18, cx + 25, cy], 180, 360, fill=(20, 24, 34), width=6)

    # Happy smile
    draw.arc([cx - 20, cy + 10, cx + 20, cy + 35], 20, 160, fill=(20, 24, 34), width=6)

    # If speaking, animated speech mouth
    if is_speaking:
        mouth_ph = (f % 12)
        if mouth_ph < 6:
            draw.ellipse([cx - 14, cy + 15, cx + 14, cy + 35], fill=(20, 24, 34))

    # Anti-gravity flight aura & sparkle particles around Guy 2
    for i in range(6):
        spark_ang = (f * 0.15 + i * 1.05)
        dist = 90 + int(math.sin(spark_ang * 2) * 20)
        sx = int(cx + math.cos(spark_ang) * dist)
        sy = int(cy + math.sin(spark_ang) * dist)
        font_star = ImageFont.truetype(FONT_VI_BOLD, 22)
        draw.text((sx, sy), "✨", font=font_star, fill=(245, 158, 11))

    # Rocket blast trails if boosting!
    if rocket_boost > 0.1:
        for b_i in range(8):
            bx = cx - 100 - b_i * 15
            by = cy + r + 150 + b_i * 35
            draw.ellipse([bx - 15, by - 15, bx + 15, by + 15], fill=(255, 200, 50, 180))

def draw_subtitles_xkcd(draw: ImageDraw.ImageDraw, part: dict):
    """Clean 2-line Subtitles: TRÊN TRUNG - DƯỚI VIỆT with speaker indicator"""
    font_cn = ImageFont.truetype(FONT_YAHEI_BOLD, 46)
    font_vi = ImageFont.truetype(FONT_VI_BOLD, 36)
    font_speaker = ImageFont.truetype(FONT_VI_BOLD, 24)

    sub_y = 1530
    draw.rounded_rectangle([60, sub_y, 1020, sub_y + 195], radius=26, fill=(18, 22, 34, 240), outline=(245, 158, 11), width=3)

    # Speaker Tag pill
    speaker = part["speaker"]
    spk_tag = "🧑 CẬU 1 (DƯỚI ĐẤT)" if "guy1" in speaker else "🦸 CẬU 2 (BAY TRÊN TRỜI)"
    spk_col = (56, 189, 248) if "guy1" in speaker else (245, 158, 11)
    draw.rounded_rectangle([90, sub_y - 22, 420, sub_y + 18], radius=12, fill=(24, 30, 46), outline=spk_col, width=2)
    draw.text((115, sub_y - 16), spk_tag, font=font_speaker, fill=spk_col)

    # Dòng 1: Tiếng Trung Hán tự màu vàng sáng
    draw.text((540, sub_y + 36), part["cn"], font=font_cn, fill=(253, 224, 71), anchor="mt")

    # Dòng 2: Tiếng Việt Segoe UI Bold màu trắng chuẩn không lỗi font
    draw.text((540, sub_y + 112), part["vi"], font=font_vi, fill=(255, 255, 255), anchor="mt")

# ==========================================
# RENDER SCENE CLIP
# ==========================================

def render_scene(scene: dict) -> Path:
    fps = 30
    sid = scene["id"]
    out_clip = WORK_DIR / f"xkcd_353_clip_{sid}.mp4"

    # Calculate sub-timings
    durations = [get_audio_duration(WORK_DIR / p["audio"]) for p in scene["parts"]]
    total_dur = sum(durations) + 0.6
    total_frames = int(round(total_dur * fps))

    # Frame split points
    frame_splits = []
    accum = 0.0
    for d in durations:
        accum += d
        frame_splits.append(int(round(accum * fps)))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    vw = cv2.VideoWriter(str(out_clip), fourcc, fps, (1080, 1920))

    print(f"  • Rendering Scene {sid}: {scene['title']} ({total_dur:.2f}s, {total_frames} frames)...")

    for f in range(total_frames):
        # Determine active speaker part
        active_idx = 0
        for idx, split_f in enumerate(frame_splits):
            if f < split_f:
                active_idx = idx
                break
        else:
            active_idx = len(scene["parts"]) - 1

        active_part = scene["parts"][active_idx]
        speaker = active_part["speaker"]

        img = Image.new("RGB", (1080, 1920), (230, 240, 250))
        draw = ImageDraw.Draw(img)

        # 1. Background
        draw_xkcd_background(draw, f)

        # 2. Characters
        is_g1_speaking = ("guy1" in speaker)
        is_g2_speaking = ("guy2" in speaker)

        rocket_boost = 0.0
        if sid == 4 and "rocket" in speaker:
            # Last part of scene 4: accelerate into space!
            sub_f = f - frame_splits[-2] if len(frame_splits) >= 2 else 0
            rocket_boost = min(1.0, sub_f / 120.0)

        draw_guy1_ground(draw, f, is_g1_speaking)
        draw_guy2_sky(draw, f, is_g2_speaking, rocket_boost=rocket_boost)

        # In Scene 2: Draw glowing Python code block floating between them!
        if sid == 2:
            code_x, code_y = 540, 480
            draw.rounded_rectangle([code_x - 220, code_y - 45, code_x + 220, code_y + 45], radius=16, fill=(30, 36, 50), outline=(56, 189, 248), width=3)
            font_code = ImageFont.truetype(FONT_VI_BOLD, 30)
            draw.text((code_x, code_y - 18), 'print("Hello, World!")', font=font_code, fill=(56, 189, 248), anchor="mt")

        # In Scene 4: Floating "import antigravity" code pill!
        if sid == 4:
            code_x, code_y = 540, 460
            draw.rounded_rectangle([code_x - 240, code_y - 45, code_x + 240, code_y + 45], radius=16, fill=(30, 36, 50), outline=(245, 158, 11), width=4)
            font_code = ImageFont.truetype(FONT_VI_BOLD, 32)
            draw.text((code_x, code_y - 20), 'import antigravity', font=font_code, fill=(253, 224, 71), anchor="mt")

        # 3. Clean Subtitles
        draw_subtitles_xkcd(draw, active_part)

        bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        vw.write(bgr)

    vw.release()
    return out_clip

# ==========================================
# MAIN PRODUCTION PIPELINE
# ==========================================

def main():
    print("=" * 80)
    print(" XKCD 353 ANIMATED STUDIO - PYTHON & IMPORT ANTIGRAVITY")
    print("=" * 80)

    # 1. Mix Audio per Scene
    print("\n[1/4] Ghép nối âm thanh đối thoại từng cảnh...")
    scene_audios = []
    for s in SCENES:
        sid = s["id"]
        inputs = []
        filter_str = ""
        accum_ms = 0
        for p_idx, p in enumerate(s["parts"]):
            af = WORK_DIR / p["audio"]
            dur = get_audio_duration(af)
            inputs.extend(["-i", str(af)])
            d_ms = int(accum_ms)
            filter_str += f"[{p_idx}:a]adelay={d_ms}|{d_ms}[a{p_idx}];"
            accum_ms += (dur + 0.15) * 1000

        filter_str += "".join([f"[a{i}]" for i in range(len(s["parts"]))])
        filter_str += f"amix=inputs={len(s['parts'])}:duration=longest[aout]"

        scene_a = WORK_DIR / f"scene_{sid}_audio.mp3"
        subprocess.run([
            FFMPEG, "-y", *inputs,
            "-filter_complex", filter_str,
            "-map", "[aout]",
            "-c:a", "libmp3lame", "-b:a", "192k",
            str(scene_a)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        scene_audios.append(scene_a)

    # Concat all scene audios
    audio_list = WORK_DIR / "all_scenes_audio.txt"
    with open(audio_list, "w", encoding="utf-8") as f:
        for sa in scene_audios:
            f.write(f"file '{sa.resolve().as_posix()}'\n")

    raw_voice = WORK_DIR / "raw_voice.mp3"
    subprocess.run([
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", str(audio_list),
        "-c", "copy",
        str(raw_voice)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    total_audio_dur = get_audio_duration(raw_voice)
    print(f"✔ Đã ghép xong toàn bộ đối thoại! Tổng thời lượng: {total_audio_dur:.2f}s")

    # Master audio mix with Lo-fi BGM
    bgm_source = WORKSPACE_ROOT / "MoneyPrinterTurbo" / "resource" / "songs" / "output002.mp3"
    if not bgm_source.exists():
        bgm_source = WORKSPACE_ROOT / "MoneyPrinterTurbo" / "resource" / "songs" / "output000.mp3"

    master_audio = WORK_DIR / "master_audio.mp3"
    subprocess.run([
        FFMPEG, "-y",
        "-i", str(raw_voice),
        "-i", str(bgm_source),
        "-filter_complex",
        f"[1:a]volume=0.15,atrim=0:{total_audio_dur},afade=t=out:st={total_audio_dur - 2.5}:d=2.5[bgm];"
        f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "[aout]",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(master_audio)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print("✔ Hòa âm Master hoàn tất!")

    # 2. Render 4 Scenes
    print("\n[2/4] Render 4 cảnh hoạt hình người que XKCD...")
    clips = []
    for s in SCENES:
        c = render_scene(s)
        clips.append(c)

    # 3. Concatenate video & audio
    print("\n[3/4] Ghép nối và hoàn thiện video 9:16 chuẩn XKCD...")
    inputs = []
    filter_inputs = ""
    for idx, c in enumerate(clips):
        inputs.extend(["-i", str(c)])
        filter_inputs += f"[{idx}:v]fps=30,setpts=PTS-STARTPTS[v{idx}];"

    concat_filter = f"{filter_inputs}" + "".join([f"[v{i}]" for i in range(len(clips))]) + f"concat=n={len(clips)}:v=1:a=0[vconcat]"

    out_path = OUT_DIR / "video_xkcd_353_python_antigravity.mp4"

    cmd_final = [
        FFMPEG, "-y",
        *inputs,
        "-i", str(master_audio),
        "-filter_complex", concat_filter,
        "-map", "[vconcat]",
        "-map", f"{len(clips)}:a",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(out_path)
    ]
    subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"\n🎉 Xuất video thành công: {out_path.name} ({size_mb:.1f} MB)")

    # Desktop copy
    desktop_copy = Path("C:/Users/User/Desktop/video_xkcd_353_python_antigravity.mp4")
    try:
        import shutil
        shutil.copy2(str(out_path), str(desktop_copy))
        print(f"💾 Đã lưu bản sao trên Desktop: {desktop_copy.name}")
    except Exception as e:
        pass

    # 4. Dispatch to Telegram
    print("\n[4/4] Gửi video về Telegram Video Hub...")
    ok, res = dispatch_video(
        video_path=str(out_path),
        title="🚀 XKCD 353: 'Sao cậu bay được? - Nhờ import antigravity đó!'",
        description=(
            "Hoạt hình phóng tác trực tiếp từ webcomic kinh điển xkcd.com/353! "
            "Đối thoại 2 người que lồng tiếng sống động: Guy 1 ngạc nhiên dưới đất & Guy 2 bay lượn trên trời. "
            "Phụ đề song ngữ cực gọn: TRÊN TRUNG - DƯỚI VIỆT, font Segoe UI Bold chuẩn 100% không lỗi dấu!"
        ),
        app_name="XKCD353Studio",
        tags=["XKCD353", "PythonAntigravity", "StickmanComic", "SongNguTrenTrungDuoiViet"],
        blocking=True
    )
    if ok:
        print(f"✅ {res}")
    else:
        print(f"⚠️ Dispatch notice: {res}")

if __name__ == "__main__":
    main()
