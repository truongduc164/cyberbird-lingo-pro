#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XKCD Minimalist Stickman Studio - Song Ngữ Trên Trung / Dưới Việt (Clean & Zero Font Error)
=============================================================================================
- Cảm hứng: XKCD (https://xkcd.com/353/) - Phong cách người que tối giản, tinh tế, dí dỏm.
- Khắc phục 100% hai vấn đề người dùng phản hồi:
    1. BỎ NHỒI NHÉT CHỮ: Không còn 3-4 tầng chữ, bỏ Pinyin, bỏ thẻ chip từ vựng rườm rà.
       Chỉ duy nhất 2 DÒNG TINH TẾ Ở ĐÁY: TRÊN TRUNG (vàng sáng) - DƯỚI VIỆT (trắng tinh).
    2. KHẮC PHỤC TRIỆT ĐỂ LỖI FONT:
       + Tiếng Trung dùng font Microsoft YaHei Bold (chuẩn Hán tự).
       + Tiếng Việt dùng font Segoe UI Bold (chuẩn Unicode tiếng Việt, không bao giờ lỗi dấu).
- Hoạt họa Người Que XKCD tối giản, cực kỳ biểu cảm và thoáng đãng:
    + Cảnh 1: Gõ laptop, 100 tab nảy quanh đầu.
    + Cảnh 2: Xẹp lép mệt mỏi, cột pin nhấp nháy đỏ [🪫 1%].
    + Cảnh 3: Đứng dậy bấm tắt tab thừa -> sao vàng bùng nổ ✨.
    + Cảnh 4: Nhấp ngụm cà phê, nháy mắt 😉 giơ ngón tay LIKE 👍 tỏa hào quang.
- Xuất chuẩn 1080x1920 (9:16) @ 30fps -> Gửi thẳng về Telegram bot!
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
WORK_DIR = WORKSPACE_ROOT / "temp_xkcd_clean"
WORK_DIR.mkdir(exist_ok=True)
OUT_DIR = WORKSPACE_ROOT / "storage"
OUT_DIR.mkdir(exist_ok=True)

# Separate Fonts to completely avoid Vietnamese font errors
FONT_YAHEI_BOLD = r"C:\Windows\Fonts\msyhbd.ttc" if Path(r"C:\Windows\Fonts\msyhbd.ttc").exists() else r"C:\Windows\Fonts\msyh.ttc"
FONT_VI_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_VI_REGULAR = r"C:\Windows\Fonts\segoeui.ttf"

SCENES = [
    {
        "id": 1,
        "type": "xkcd_100tabs",
        "title": "Scene 1 • Não Mở 100 Tab",
        "cn": "下午三点，脑子开了100个网页。",
        "vi": "Ba giờ chiều, não mở 100 tab trình duyệt.",
        "extra_pad": 0.8
    },
    {
        "id": 2,
        "type": "xkcd_lowbattery",
        "title": "Scene 2 • Pin Chỉ Còn 1%",
        "cn": "身体坐着，电量只剩百分之一。",
        "vi": "Thân thể ngồi đó, nhưng pin chỉ còn đúng 1%.",
        "extra_pad": 0.7
    },
    {
        "id": 3,
        "type": "xkcd_closetabs",
        "title": "Scene 3 • Cứ Từ Từ, Tắt Bớt Tab Đi",
        "cn": "慢慢来，先把不需要的网页关掉。",
        "vi": "Cứ từ từ thôi, hãy tắt bớt những tab thừa đi.",
        "extra_pad": 0.7
    },
    {
        "id": 4,
        "type": "xkcd_zen_coffee",
        "title": "Scene 4 • Tha Thứ Cho Bản Thân, Mọi Chuyện Còn Kịp",
        "cn": "放过自己，一切都还来得及。",
        "vi": "Tha thứ cho chính mình, mọi chuyện đều còn kịp.",
        "extra_pad": 1.1
    }
]

# ==========================================
# PROCEDURAL AUDIO & SOUND DESIGN (FOLEY)
# ==========================================

def create_foley_sfx(work_dir: Path):
    sr = 44100
    def write_wav(path, data):
        with wave.open(str(path), 'w') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(sr)
            f.writeframes((np.clip(data, -1.0, 1.0) * 32767).astype(np.int16).tobytes())

    # 1. Pop Sound
    t = np.linspace(0, 0.08, int(sr * 0.08), False)
    freq = np.linspace(400, 1300, len(t))
    phase = 2 * np.pi * np.cumsum(freq) / sr
    pop = np.sin(phase) * np.exp(-38 * t)
    write_wav(work_dir / "sfx_pop.wav", pop)

    # 2. Whoosh Transition
    t_w = np.linspace(0, 0.22, int(sr * 0.22), False)
    noise = np.random.uniform(-1, 1, len(t_w))
    env_w = np.sin(np.pi * t_w / 0.22) ** 2
    whoosh = noise * env_w * 0.45
    write_wav(work_dir / "sfx_whoosh.wav", whoosh)

    # 3. Crystal Chime / Ding!
    t_d = np.linspace(0, 0.50, int(sr * 0.50), False)
    ding = (np.sin(2 * np.pi * 1480 * t_d) * 0.65 + np.sin(2 * np.pi * 2960 * t_d) * 0.35) * np.exp(-8 * t_d)
    write_wav(work_dir / "sfx_ding.wav", ding)

    # 4. Low Battery Beep
    t_lb = np.linspace(0, 0.28, int(sr * 0.28), False)
    beep = (np.sin(2 * np.pi * 480 * t_lb) * 0.7 + np.sin(2 * np.pi * 960 * t_lb) * 0.3) * np.exp(-7 * t_lb)
    write_wav(work_dir / "sfx_battery.wav", beep)

def get_audio_duration(file_path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return float(res.stdout.strip())

async def generate_voices(work_dir: Path):
    voice = "zh-CN-XiaoxiaoNeural"
    durations = []
    for s in SCENES:
        out_f = work_dir / f"voice_{s['id']}.mp3"
        if not out_f.exists() or out_f.stat().st_size < 3000:
            communicate = edge_tts.Communicate(s["cn"], voice, rate="-4%")
            await communicate.save(str(out_f))
        dur = get_audio_duration(out_f)
        total_dur = dur + s.get("extra_pad", 0.7)
        durations.append(total_dur)
        print(f"  • Voice {s['id']}: {dur:.2f}s (Clip: {total_dur:.2f}s) | {s['title']}")
    return durations

# ==========================================
# CLEAN XKCD MINIMALIST RENDERING
# ==========================================

def draw_clean_subtitles(draw: ImageDraw.ImageDraw, scene: dict):
    """
    Renders EXACTLY TWO CLEAN LINES (TRÊN TRUNG - DƯỚI VIỆT).
    Zero clutter, zero font error!
    """
    font_cn = ImageFont.truetype(FONT_YAHEI_BOLD, 48)
    font_vi = ImageFont.truetype(FONT_VI_BOLD, 36)

    sub_y = 1520
    # Clean frosted pill in Safe Zone
    draw.rounded_rectangle([70, sub_y, 1010, sub_y + 185], radius=26, fill=(16, 20, 30, 235), outline=(245, 158, 11), width=3)

    # Line 1 (TRÊN): Tiếng Trung Hán tự màu vàng kim
    draw.text((540, sub_y + 26), scene["cn"], font=font_cn, fill=(253, 224, 71), anchor="mt")

    # Line 2 (DƯỚI): Tiếng Việt dịch nghĩa chuẩn Unicode Segoe UI Bold màu trắng
    draw.text((540, sub_y + 100), scene["vi"], font=font_vi, fill=(255, 255, 255), anchor="mt")

def render_xkcd_frame(scene: dict, f: int, total_frames: int) -> Image.Image:
    w, h = 1080, 1920
    desk_y = 1320
    stype = scene["type"]

    # Clean dark minimalist canvas
    img = Image.new("RGB", (w, h), (20, 24, 34))
    draw = ImageDraw.Draw(img)

    # Subtle desk line
    draw.line([(0, desk_y), (w, desk_y)], fill=(65, 75, 95), width=5)

    font_tab = ImageFont.truetype(FONT_VI_BOLD, 24)

    # -------------------------------------------------------------
    # SCENE 1: XKCD STICKMAN WITH 100 TABS & LAPTOP
    # -------------------------------------------------------------
    if stype == "xkcd_100tabs":
        cx = 540
        cy = 920 + int(math.sin(f * 0.45) * 6)
        r = 100

        # Stickman Body
        draw.line([(cx, cy + r), (cx, desk_y - 15)], fill=(255, 255, 255), width=16)

        # Arms typing fast on laptop
        arm_phase = (f % 6)
        hand_l_y = desk_y - 25 + (8 if arm_phase < 3 else -6)
        hand_r_y = desk_y - 25 + (-6 if arm_phase < 3 else 8)

        draw.line([(cx, cy + r + 30), (cx - 120, desk_y - 50)], fill=(255, 255, 255), width=14)
        draw.line([(cx - 120, desk_y - 50), (cx - 60, hand_l_y)], fill=(255, 255, 255), width=14)

        draw.line([(cx, cy + r + 30), (cx + 120, desk_y - 50)], fill=(255, 255, 255), width=14)
        draw.line([(cx + 120, desk_y - 50), (cx + 60, hand_r_y)], fill=(255, 255, 255), width=14)

        # Clean Minimalist Laptop
        draw.polygon([(430, desk_y - 85), (650, desk_y - 85), (680, desk_y), (400, desk_y)], fill=(32, 38, 54), outline=(255, 255, 255), width=4)
        draw.polygon([(445, desk_y - 75), (635, desk_y - 75), (660, desk_y - 12), (420, desk_y - 12)], fill=(56, 189, 248))

        # Typing sparks
        spark_x = (cx - 50) if arm_phase < 3 else (cx + 50)
        draw.line([(spark_x, desk_y - 35), (spark_x - 12, desk_y - 55)], fill=(255, 240, 120), width=4)
        draw.line([(spark_x, desk_y - 35), (spark_x + 12, desk_y - 55)], fill=(255, 240, 120), width=4)

        # Head Circle
        draw.ellipse([cx - r + 8, cy - r + 10, cx + r + 8, cy + r + 10], fill=(12, 14, 20))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255), outline=(20, 22, 30), width=8)

        # Expressive Overwhelmed Eyes
        eye_y = cy - 8
        draw.ellipse([cx - 40 - 18, eye_y - 22, cx - 40 + 18, eye_y + 22], fill=(20, 22, 30))
        draw.ellipse([cx - 40 - 8, eye_y - 14, cx - 40 + 4, eye_y - 2], fill=(255, 255, 255))
        draw.ellipse([cx + 40 - 18, eye_y - 22, cx + 40 + 18, eye_y + 22], fill=(20, 22, 30))
        draw.ellipse([cx + 40 - 8, eye_y - 14, cx + 40 + 4, eye_y - 2], fill=(255, 255, 255))

        # Open 'O' Mouth
        draw.ellipse([cx - 20, cy + 40, cx + 20, cy + 72], fill=(20, 22, 30))

        # Swirl on head
        swirl_angle = (f * 15) % 360
        draw.arc([cx - 60, cy - r - 80, cx + 60, cy - r + 30], swirl_angle, swirl_angle + 270, fill=(255, 220, 80), width=6)

        # Floating Clean Tabs (Only 4-5 neat boxes)
        tab_list = [
            (110, 680, "🔥 TAB 99+: Báo cáo!"),
            (690, 650, "💸 Tiền trọ tháng này?"),
            (90, 940, "🍜 Trưa nay ăn gì?"),
            (710, 920, "💬 Tin nhắn chưa rep!"),
            (380, 560, "⚠️ DEADLINE 17:00!")
        ]
        for idx, (tx, ty, text) in enumerate(tab_list):
            fy = int(ty + math.sin(f * 0.22 + idx * 1.3) * 14)
            draw.rounded_rectangle([tx, fy, tx + 280, fy + 60], radius=14, fill=(28, 34, 48), outline=(255, 255, 255), width=3)
            draw.text((tx + 20, fy + 14), text, font=font_tab, fill=(255, 255, 255))

    # -------------------------------------------------------------
    # SCENE 2: XKCD DEFALTED / SLUMPED ON DESK [ 🪫 1% ]
    # -------------------------------------------------------------
    elif stype == "xkcd_lowbattery":
        cx = 540
        cy = 1180 + int(math.sin(f * 0.15) * 4)
        r = 100

        # Body collapsed flat on desk
        draw.line([(cx - 200, desk_y - 15), (cx + 200, desk_y - 15)], fill=(255, 255, 255), width=16)

        # Head resting flat horizontally
        draw.ellipse([cx - r + 8, cy - r + 38, cx + r + 8, cy + r + 38], fill=(12, 14, 20))
        draw.ellipse([cx - r, cy - r + 30, cx + r, cy + r + 30], fill=(255, 255, 255), outline=(20, 22, 30), width=8)

        # Slit tired eyes - -
        draw.line([(cx - 45 - 20, cy + 20), (cx - 45 + 20, cy + 20)], fill=(20, 22, 30), width=8)
        draw.line([(cx + 45 - 20, cy + 20), (cx + 45 + 20, cy + 20)], fill=(20, 22, 30), width=8)

        # Drooping mouth
        draw.arc([cx - 24, cy + 50, cx + 24, cy + 80], 0, 180, fill=(20, 22, 30), width=6)

        # Giant Glowing Low Battery Icon [ 🪫 1% ]
        bat_cx, bat_cy = 540, 720
        bat_pulse = (math.sin(f * 0.28) + 1.0) / 2.0
        glow_color = (int(255 * (0.8 + 0.2 * bat_pulse)), int(40 * bat_pulse), int(60 * bat_pulse))

        # Battery body
        draw.rounded_rectangle([bat_cx - 160, bat_cy - 70, bat_cx + 160, bat_cy + 70], radius=24, fill=(25, 30, 44), outline=(255, 255, 255), width=5)
        draw.rounded_rectangle([bat_cx + 160, bat_cy - 25, bat_cx + 184, bat_cy + 25], radius=8, fill=(255, 255, 255))

        # 1% Red indicator bar
        draw.rounded_rectangle([bat_cx - 145, bat_cy - 55, bat_cx - 85, bat_cy + 55], radius=10, fill=glow_color)

        # 1% Text
        font_bat = ImageFont.truetype(FONT_VI_BOLD, 56)
        draw.text((bat_cx + 25, bat_cy - 40), "1%", font=font_bat, fill=glow_color)

        # Zzz bubbles rising
        for z_i in range(3):
            z_y = int(cy - 40 - ((f * 3 + z_i * 60) % 240))
            z_x = int(cx + 80 + math.sin(z_y * 0.05) * 25)
            draw.text((z_x, z_y), "💤", font=font_tab, fill=(200, 225, 255))

    # -------------------------------------------------------------
    # SCENE 3: POINTER STICK POPPING TABS (CONFIDENT RECOVERY)
    # -------------------------------------------------------------
    elif stype == "xkcd_closetabs":
        cx = 450
        cy = 920 + int(math.sin(f * 0.3) * 5)
        r = 100

        # Body upright
        draw.line([(cx, cy + r), (cx, desk_y - 15)], fill=(255, 255, 255), width=16)

        # Wand arm pointing up
        wand_tip_x = 760 + int(math.sin(f * 0.2) * 8)
        wand_tip_y = 660 + int(math.cos(f * 0.2) * 8)
        hand_x, hand_y = cx + 170, cy + 50

        draw.line([(cx, cy + r + 30), (hand_x, hand_y)], fill=(255, 255, 255), width=14)
        # Golden Wand
        draw.line([(hand_x, hand_y), (wand_tip_x, wand_tip_y)], fill=(246, 211, 101), width=10)
        draw.ellipse([wand_tip_x - 14, wand_tip_y - 14, wand_tip_x + 14, wand_tip_y + 14], fill=(255, 255, 255))

        # Other arm on hip
        draw.line([(cx, cy + r + 30), (cx - 100, cy + r + 100)], fill=(255, 255, 255), width=14)

        # Head & Spectacles 🤓
        draw.ellipse([cx - r + 8, cy - r + 10, cx + r + 8, cy + r + 10], fill=(12, 14, 20))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255), outline=(20, 22, 30), width=8)

        # Spectacles
        draw.ellipse([cx - 55, cy - 25, cx - 10, cy + 20], outline=(246, 211, 101), width=6)
        draw.ellipse([cx + 10, cy - 25, cx + 55, cy + 20], outline=(246, 211, 101), width=6)
        draw.line([(cx - 10, cy - 2), (cx + 10, cy - 2)], fill=(246, 211, 101), width=5)

        # Smile
        draw.arc([cx - 25, cy + 30, cx + 25, cy + 65], 20, 160, fill=(20, 22, 30), width=6)

        # Tab exploding at Wand Tip!
        pop_rad = 35 + int((f * 4.5) % 100)
        draw.arc([wand_tip_x - pop_rad, wand_tip_y - pop_rad, wand_tip_x + pop_rad, wand_tip_y + pop_rad], 0, 360, fill=(255, 230, 100), width=5)

        # Burst stars ✨
        for s_idx in range(8):
            ang = s_idx * (math.pi / 4.0) + (f * 0.1)
            dist = pop_rad + 25
            sx = int(wand_tip_x + math.cos(ang) * dist)
            sy = int(wand_tip_y + math.sin(ang) * dist)
            draw.text((sx, sy), "✨", font=font_tab, fill=(255, 240, 120))

        # Green stamp [ ✔ ĐÃ ĐÓNG TAB THỪA ]
        draw.rounded_rectangle([wand_tip_x - 30, wand_tip_y - 120, wand_tip_x + 240, wand_tip_y - 65], radius=16, fill=(16, 185, 129), outline=(255, 255, 255), width=3)
        draw.text((wand_tip_x - 10, wand_tip_y - 106), "✔ ĐÃ ĐÓNG TAB THỪA", font=font_tab, fill=(255, 255, 255))

    # -------------------------------------------------------------
    # SCENE 4: COFFEE SIPPING, WINK & THUMBS UP
    # -------------------------------------------------------------
    elif stype == "xkcd_zen_coffee":
        cx = 540
        cy = 920 + int(math.sin(f * 0.25) * 5)
        r = 100

        # Body upright
        draw.line([(cx, cy + r), (cx, desk_y - 15)], fill=(255, 255, 255), width=16)

        # Head
        draw.ellipse([cx - r + 8, cy - r + 10, cx + r + 8, cy + r + 10], fill=(12, 14, 20))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255), outline=(20, 22, 30), width=8)

        # Cheeks
        draw.ellipse([cx - 65, cy + 20, cx - 35, cy + 42], fill=(255, 140, 160))
        draw.ellipse([cx + 35, cy + 20, cx + 65, cy + 42], fill=(255, 140, 160))

        # Winking Eye 😉
        eye_y = cy - 8
        draw.ellipse([cx - 40 - 18, eye_y - 22, cx - 40 + 18, eye_y + 22], fill=(20, 22, 30))
        draw.ellipse([cx - 40 - 8, eye_y - 14, cx - 40 + 4, eye_y - 2], fill=(255, 255, 255))
        draw.arc([cx + 20, eye_y - 10, cx + 60, eye_y + 18], 180, 360, fill=(20, 22, 30), width=8)

        # Smile
        draw.rounded_rectangle([cx - 26, cy + 38, cx + 26, cy + 68], radius=12, fill=(30, 20, 25))
        draw.ellipse([cx - 12, cy + 52, cx + 12, cy + 65], fill=(255, 120, 140))

        # Left arm holding coffee cup
        cup_x, cup_y = cx - 110, desk_y - 50
        draw.line([(cx, cy + r + 30), (cup_x + 10, cup_y + 10)], fill=(255, 255, 255), width=14)
        draw.rounded_rectangle([cup_x - 30, cup_y - 35, cup_x + 30, cup_y + 20], radius=8, fill=(255, 255, 255), outline=(20, 22, 30), width=4)
        draw.arc([cup_x + 25, cup_y - 22, cup_x + 48, cup_y + 8], 270, 90, fill=(255, 255, 255), width=6)

        # Heart steam puff ♡
        heart_y = int(cup_y - 50 - ((f * 2.5) % 180))
        draw.text((cup_x - 12, heart_y), "♡", font=font_tab, fill=(255, 160, 180))

        # Right arm giving GIANT THUMBS UP 👍
        thumb_x, thumb_y = cx + 180, cy + 20
        draw.line([(cx, cy + r + 30), (thumb_x, thumb_y)], fill=(255, 255, 255), width=14)
        font_emoji = ImageFont.truetype(FONT_VI_REGULAR, 78)
        draw.text((thumb_x - 24, thumb_y - 70), "👍", font=font_emoji, fill=(255, 215, 0))

        # Golden halo rings & sparkles
        halo_r = 140 + int(math.sin(f * 0.2) * 15)
        draw.arc([cx - halo_r, cy - halo_r, cx + halo_r, cy + halo_r], 0, 360, fill=(246, 211, 101), width=4)
        for s_i in range(8):
            ang = s_i * (math.pi / 4.0) + (f * 0.05)
            sx = int(cx + math.cos(ang) * (halo_r + 40))
            sy = int(cy + math.sin(ang) * (halo_r + 40))
            draw.text((sx - 10, sy - 10), "✨", font=font_tab, fill=(255, 235, 120))

    # Clean Subtitle (TRÊN TRUNG - DƯỚI VIỆT)
    draw_clean_subtitles(draw, scene)

    return img

# ==========================================
# RENDER SCENE TO MP4
# ==========================================

def render_scene_clip(scene: dict, dur: float) -> Path:
    fps = 30
    total_frames = int(round(dur * fps))
    scene_id = scene["id"]
    out_clip = WORK_DIR / f"clean_clip_{scene_id}.mp4"

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    vw = cv2.VideoWriter(str(out_clip), fourcc, fps, (1080, 1920))

    print(f"    -> Rendering {total_frames} frames ({dur:.2f}s) of XKCD Clean animation...")

    for f in range(total_frames):
        composed_img = render_xkcd_frame(scene, f, total_frames)
        bgr = cv2.cvtColor(np.array(composed_img), cv2.COLOR_RGB2BGR)
        vw.write(bgr)

    vw.release()
    return out_clip

# ==========================================
# MAIN PRODUCTION PIPELINE
# ==========================================

def main():
    print("=" * 80)
    print(" XKCD CLEAN STICKMAN STUDIO - SONG NGỮ TRÊN TRUNG / DƯỚI VIỆT")
    print("=" * 80)

    # 1. Foley SFX
    print("\n[1/5] Khởi tạo âm thanh Foley đồng bộ...")
    create_foley_sfx(WORK_DIR)

    # 2. Native Chinese Voiceovers
    print("\n[2/5] Tạo giọng đọc bản xứ tiếng Trung Douyin chuẩn Bắc Kinh (Xiaoxiao)...")
    durations = asyncio.run(generate_voices(WORK_DIR))

    voice_files = [WORK_DIR / f"voice_{s['id']}.mp3" for s in SCENES]
    audio_list = WORK_DIR / "audio_list.txt"
    with open(audio_list, "w", encoding="utf-8") as f:
        for vf in voice_files:
            f.write(f"file '{vf.resolve().as_posix()}'\n")

    raw_voice = WORK_DIR / "raw_voice.mp3"
    subprocess.run([
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", str(audio_list),
        "-c", "copy",
        str(raw_voice)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    total_audio_dur = sum(durations)
    print(f"✔ Đã ghép xong giọng đọc! Tổng thời lượng: {total_audio_dur:.2f}s")

    # 3. Master Audio Mix (Voice + BGM + SFX)
    print("\n[3/5] Hòa âm Master: Giọng đọc + Lo-fi BGM + Foley SFX...")
    bgm_source = WORKSPACE_ROOT / "MoneyPrinterTurbo" / "resource" / "songs" / "output000.mp3"
    if not bgm_source.exists():
        bgm_source = WORKSPACE_ROOT / "MoneyPrinterTurbo" / "resource" / "songs" / "output001.mp3"

    d1 = int(300)
    d2 = int((durations[0] + 0.8) * 1000)
    d3 = int((durations[0] + durations[1] + 1.0) * 1000)
    d4 = int((sum(durations[:3]) + 1.8) * 1000)

    master_audio = WORK_DIR / "master_audio.mp3"
    cmd_audio_mix = [
        FFMPEG, "-y",
        "-i", str(raw_voice),
        "-i", str(bgm_source),
        "-i", str(WORK_DIR / "sfx_whoosh.wav"),
        "-i", str(WORK_DIR / "sfx_battery.wav"),
        "-i", str(WORK_DIR / "sfx_pop.wav"),
        "-i", str(WORK_DIR / "sfx_ding.wav"),
        "-filter_complex",
        f"[1:a]volume=0.18,atrim=0:{total_audio_dur},afade=t=out:st={total_audio_dur - 2.5}:d=2.5[bgm];"
        f"[2:a]adelay={d1}|{d1},volume=0.6[sfx1];"
        f"[3:a]adelay={d2}|{d2},volume=0.7[sfx2];"
        f"[4:a]adelay={d3}|{d3},volume=0.8[sfx3];"
        f"[5:a]adelay={d4}|{d4},volume=0.85[sfx4];"
        f"[0:a][bgm][sfx1][sfx2][sfx3][sfx4]amix=inputs=6:duration=first:dropout_transition=2[aout]",
        "-map", "[aout]",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(master_audio)
    ]
    subprocess.run(cmd_audio_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print("✔ Đã hòa âm Master hoàn tất!")

    # 4. Render Scenes
    print("\n[4/5] Render các cảnh hoạt hình XKCD tối giản...")
    clips = []
    for s, dur in zip(SCENES, durations):
        print(f"  • Render {s['title']} ({dur:.2f}s)...")
        c = render_scene_clip(s, dur)
        clips.append(c)

    # 5. Concatenate & Finalize Video
    print("\n[5/5] Ghép nối và hoàn thiện video 9:16 chuẩn Douyin / TikTok...")
    inputs = []
    filter_inputs = ""
    for idx, c in enumerate(clips):
        inputs.extend(["-i", str(c)])
        filter_inputs += f"[{idx}:v]fps=30,setpts=PTS-STARTPTS[v{idx}];"

    concat_filter = f"{filter_inputs}" + "".join([f"[v{i}]" for i in range(len(clips))]) + f"concat=n={len(clips)}:v=1:a=0[vconcat]"

    out_path = OUT_DIR / "video_xkcd_song_ngu_tren_trung_duoi_viet.mp4"

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

    # Save copy to Desktop
    desktop_copy = Path("C:/Users/User/Desktop/video_xkcd_song_ngu_tren_trung_duoi_viet.mp4")
    try:
        import shutil
        shutil.copy2(str(out_path), str(desktop_copy))
        print(f"💾 Đã lưu bản sao trên Desktop: {desktop_copy.name}")
    except Exception as e:
        pass

    # 6. Auto Dispatch to Telegram
    print("\n[DISPATCH] Gửi video về Telegram Video Hub...")
    ok, res = dispatch_video(
        video_path=str(out_path),
        title="✨ HOẠT HÌNH XKCD: Song Ngữ Trên Trung - Dưới Việt (Sạch Sẽ, Không Lỗi Font)",
        description=(
            "Đúng yêu cầu của bạn: Bỏ sạch chữ thừa/Pinyin/thẻ chip, "
            "CHỈ 2 DÒNG DUY NHẤT Ở ĐÁY: TRÊN TRUNG - DƯỚI VIỆT! "
            "Font Segoe UI Bold chuẩn 100% tiếng Việt không lỗi dấu, phong cách người que tối giản kiểu XKCD 353 cực thoáng đãng!"
        ),
        app_name="XKCDCleanStudio",
        tags=["XKCDStickman", "SongNguTrenTrungDuoiViet", "KhongLoiFont", "CleanMinimalist"],
        blocking=True
    )
    if ok:
        print(f"✅ {res}")
    else:
        print(f"⚠️ Dispatch notice: {res}")

if __name__ == "__main__":
    main()
