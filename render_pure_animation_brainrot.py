#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pure 100% Animation Studio - Episode 2: "HỘI CHỨNG THỐI NÃO" (BRAINROT • 脑腐)
=============================================================================
- Chủ đề: Lướt điện thoại 2 tiếng trong đêm đến mức "thối não" / mụ mẫm đầu óc
- 100% Hoạt hình Chibi Người Que thuần túy:
    + Cảnh 1: Phòng tối 1h sáng, mặt phát sáng xanh lét từ điện thoại, kim đồng hồ quay tít.
    + Cảnh 2: Não chập mạch "thối não" bốc khói xì xèo, mắt xoắn ốc 🌀, chảy nước dãi ngơ ngác.
    + Cảnh 3: Bừng tỉnh ném điện thoại bay vèo, mở rèm hít thở gió đêm mát lành.
    + Cảnh 4: Trùm chăn ấm đội mũ ngủ, giải cứu bộ não, nháy mắt 😉 giơ tay LIKE 👍.
- Phụ đề Song Ngữ Douyin / Netflix chuẩn mực ở đáy.
- Master Audio: Giọng Xiaoxiao + Lo-fi BGM + Foley SFX (Swipe, Clock, Sizzle, Ding).
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
WORK_DIR = WORKSPACE_ROOT / "temp_pure_animation_ep2"
WORK_DIR.mkdir(exist_ok=True)
OUT_DIR = WORKSPACE_ROOT / "storage"
OUT_DIR.mkdir(exist_ok=True)

FONT_YAHEI = r"C:\Windows\Fonts\msyh.ttc"
FONT_SEGOE = r"C:\Windows\Fonts\segoeui.ttf"

SCENES = [
    {
        "id": 1,
        "type": "ep2_phone_scroll",
        "title": "Scene 1 • Lướt Điện Thoại Trong Đêm",
        "cn": "本来只想看一分钟手机，结果两个小时过去了。",
        "pinyin": "běn lái zhǐ xiǎng kàn yì fēn zhōng shǒu jī, jié guǒ liǎng gè xiǎo shí guò qù le.",
        "vi": "Ban đầu chỉ tính cầm máy 1 phút, ai ngờ 2 tiếng trôi qua lúc nào không hay.",
        "chip1": "手机 (shǒujī): Điện thoại",
        "chip2": "过去 (guòqù): Trôi qua",
        "tag": "📱 NỖI ĐAU GEN Z • 刷手机",
        "extra_pad": 0.6
    },
    {
        "id": 2,
        "type": "ep2_brainrot_melt",
        "title": "Scene 2 • Hội Chứng Thối Não",
        "cn": "脑子开始短路，整个人变得呆呆的。",
        "pinyin": "nǎo zi kāi shǐ duǎn lù, zhěng gè rén biàn de dāi dāi de.",
        "vi": "Não bắt đầu chập mạch 'thối não', cả người ngơ ngác đờ đẫn.",
        "chip1": "短路 (duǎnlù): Chập mạch / Đơ não",
        "chip2": "呆呆的 (dāidāi de): Ngơ ngác / Đờ đẫn",
        "tag": "🧠 HỘI CHỨNG THỐI NÃO • 脑子短路",
        "extra_pad": 0.6
    },
    {
        "id": 3,
        "type": "ep2_wake_throw_phone",
        "title": "Scene 3 • Dừng Lại & Hít Thở",
        "cn": "停下来吧！放下手机，深呼吸一口气。",
        "pinyin": "tíng xià lai ba! fàng xià shǒu jī, shēn hū xī yì kǒu qì.",
        "vi": "Dừng lại thôi nào! Bỏ điện thoại xuống, hít một hơi thật sâu.",
        "chip1": "停下来 (tíngxiàlai): Dừng lại đi",
        "chip2": "深呼吸 (shēnhūxī): Hít thở sâu",
        "tag": "🌿 TỈNH TÁO LẠI • 放下手机",
        "extra_pad": 0.6
    },
    {
        "id": 4,
        "type": "ep2_sleep_thumbsup",
        "title": "Scene 4 • Giải Cứu Bộ Não & Ngủ Sớm",
        "cn": "拯救你的大脑，今晚早点睡觉吧！",
        "pinyin": "zhěng jiù nǐ de dà nǎo, jīn wǎn zǎo diǎn shuì jiào ba!",
        "vi": "Cứu lấy bộ não của bạn, tối nay hãy đi ngủ sớm nhé!",
        "chip1": "拯救 (zhěngjiù): Giải cứu",
        "chip2": "睡觉 (shuìjiào): Đi ngủ",
        "tag": "✨ ĐI NGỦ SỚM • 早点睡觉",
        "extra_pad": 0.9
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

    # 1. Phone Swipe Whoosh
    t_w = np.linspace(0, 0.16, int(sr * 0.16), False)
    noise = np.random.uniform(-1, 1, len(t_w))
    env_w = np.sin(np.pi * t_w / 0.16) ** 2
    whoosh = noise * env_w * 0.4
    write_wav(work_dir / "sfx_swipe.wav", whoosh)

    # 2. Electric Glitch / Brain Short-circuit
    t_g = np.linspace(0, 0.35, int(sr * 0.35), False)
    glitch = np.sign(np.sin(2 * np.pi * 320 * t_g)) * 0.3 + np.random.uniform(-0.2, 0.2, len(t_g))
    write_wav(work_dir / "sfx_glitch.wav", glitch * np.exp(-4 * t_g))

    # 3. Phone Throw / Pop Thud
    t_t = np.linspace(0, 0.18, int(sr * 0.18), False)
    thud = np.sin(2 * np.pi * 85 * t_t) * np.exp(-18 * t_t)
    write_wav(work_dir / "sfx_thud.wav", thud)

    # 4. Crystal Chime / Ding!
    t_d = np.linspace(0, 0.50, int(sr * 0.50), False)
    ding = (np.sin(2 * np.pi * 1480 * t_d) * 0.65 + np.sin(2 * np.pi * 2960 * t_d) * 0.35) * np.exp(-8 * t_d)
    write_wav(work_dir / "sfx_ding.wav", ding)

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
            communicate = edge_tts.Communicate(s["cn"], voice, rate="-2%")
            await communicate.save(str(out_f))
        dur = get_audio_duration(out_f)
        total_dur = dur + s.get("extra_pad", 0.6)
        durations.append(total_dur)
        print(f"  • Voice {s['id']}: {dur:.2f}s (Clip: {total_dur:.2f}s) | {s['title']}")
    return durations

# ==========================================
# 100% PURE ANIMATION GRAPHICS ENGINE
# ==========================================

def draw_subtitles_and_ui(draw: ImageDraw.ImageDraw, scene: dict):
    """Renders the pristine anime subtitle box, top badge, and vocab sticky notes"""
    font_badge = ImageFont.truetype(FONT_YAHEI, 28)
    font_pinyin = ImageFont.truetype(FONT_SEGOE, 32)
    font_hanzi = ImageFont.truetype(FONT_YAHEI, 52)
    font_vi = ImageFont.truetype(FONT_SEGOE, 34)
    font_chip = ImageFont.truetype(FONT_YAHEI, 28)

    # 1. Top Badge
    badge_x1, badge_y1 = 65, 110
    badge_x2, badge_y2 = 570, 180
    draw.rounded_rectangle([badge_x1, badge_y1, badge_x2, badge_y2], radius=22, fill=(18, 22, 34, 230), outline=(255, 255, 255), width=3)
    draw.text((badge_x1 + 28, badge_y1 + 18), scene["tag"], font=font_badge, fill=(255, 230, 140))

    # 2. Subtitle Box
    sub_x1, sub_y1 = 55, 1410
    sub_x2, sub_y2 = 1025, 1635
    draw.rounded_rectangle([sub_x1, sub_y1, sub_x2, sub_y2], radius=28, fill=(14, 18, 28, 235), outline=(246, 211, 101), width=3)
    draw.rounded_rectangle([sub_x1 + 5, sub_y1 + 5, sub_x2 - 5, sub_y2 - 5], radius=24, outline=(255, 255, 255, 50), width=1)

    # Line 1: Pinyin
    draw.text((540, 1432), scene["pinyin"], font=font_pinyin, fill=(254, 230, 138), anchor="mt")

    # Line 2: Hanzi
    draw.text((540, 1485), scene["cn"], font=font_hanzi, fill=(255, 255, 255), anchor="mt")

    # Line 3: Vietnamese
    draw.text((540, 1565), scene["vi"], font=font_vi, fill=(226, 232, 240), anchor="mt")

    # 3. Vocab Sticky Notes
    chip1_box = [80, 1660, 520, 1728]
    chip2_box = [560, 1660, 1000, 1728]

    draw.rounded_rectangle(chip1_box, radius=18, fill=(22, 28, 42, 240), outline=(255, 255, 255, 200), width=2)
    draw.text((chip1_box[0] + 25, chip1_box[1] + 18), f"🏷️ {scene['chip1']}", font=font_chip, fill=(255, 255, 255))

    draw.rounded_rectangle(chip2_box, radius=18, fill=(22, 28, 42, 240), outline=(255, 255, 255, 200), width=2)
    draw.text((chip2_box[0] + 25, chip2_box[1] + 18), f"🏷️ {scene['chip2']}", font=font_chip, fill=(255, 255, 255))

def render_ep2_frame(scene: dict, f: int, total_frames: int) -> Image.Image:
    w, h = 1080, 1920
    bed_y = 1260
    stype = scene["type"]

    img = Image.new("RGB", (w, h), (14, 16, 26))
    draw = ImageDraw.Draw(img)

    font_tab = ImageFont.truetype(FONT_SEGOE, 24)

    # -------------------------------------------------------------
    # SCENE 1: BEDROOM 1:00 AM - SWIPING PHONE, CLOCK SPINNING
    # -------------------------------------------------------------
    if stype == "ep2_phone_scroll":
        # Dark room gradient
        for y in range(0, bed_y, 4):
            p = y / float(bed_y)
            r = int(12 + 8 * p)
            g = int(14 + 10 * p)
            b = int(24 + 16 * p)
            draw.rectangle([0, y, w, y + 4], fill=(r, g, b))

        # Wall Clock spinning on top right
        clock_cx, clock_cy, clock_r = 860, 360, 95
        draw.ellipse([clock_cx - clock_r, clock_cy - clock_r, clock_cx + clock_r, clock_cy + clock_r], fill=(25, 30, 45), outline=(200, 210, 230), width=6)
        # Hour marks
        for i in range(12):
            ang = i * (math.pi / 6.0)
            mx = clock_cx + math.sin(ang) * (clock_r - 15)
            my = clock_cy - math.cos(ang) * (clock_r - 15)
            draw.ellipse([mx - 3, my - 3, mx + 3, my + 3], fill=(255, 255, 255))

        # Hands spinning fast!
        spin_ang = f * 0.45
        draw.line([(clock_cx, clock_cy), (clock_cx + math.sin(spin_ang * 0.1) * 45, clock_cy - math.cos(spin_ang * 0.1) * 45)], fill=(255, 220, 100), width=7)
        draw.line([(clock_cx, clock_cy), (clock_cx + math.sin(spin_ang) * 70, clock_cy - math.cos(spin_ang) * 70)], fill=(255, 80, 100), width=5)
        # Digital Time Tag below clock
        time_text = "01:45 AM" if (f % 40 < 20) else "02:30 AM ⚠️"
        draw.rounded_rectangle([clock_cx - 90, clock_cy + clock_r + 15, clock_cx + 90, clock_cy + clock_r + 60], radius=10, fill=(20, 24, 36), outline=(255, 80, 100), width=2)
        draw.text((clock_cx - 65, clock_cy + clock_r + 22), time_text, font=font_tab, fill=(255, 100, 120))

        # Bed in foreground
        draw.rectangle([0, bed_y, w, h], fill=(30, 35, 52))
        # Warm comfy quilt
        draw.polygon([(0, bed_y), (w, bed_y), (w, bed_y + 180), (0, bed_y + 180)], fill=(45, 55, 80))
        draw.line([(0, bed_y), (w, bed_y)], fill=(245, 158, 11), width=6)

        # Character sitting in bed holding phone
        cx = 500
        cy = 960 + int(math.sin(f * 0.3) * 4)
        r = 100

        # Hoodie Body
        draw.polygon([(cx - 140, cy + r + 20), (cx + 140, cy + r + 20), (cx + 170, bed_y), (cx - 170, bed_y)], fill=(245, 158, 11), outline=(22, 22, 28), width=8)

        # Arms holding phone
        phone_x, phone_y = cx + 80, cy + r + 10
        draw.line([(cx - 120, cy + r + 30), (phone_x - 40, phone_y + 40)], fill=(245, 158, 11), width=22)
        draw.line([(cx + 120, cy + r + 30), (phone_x + 40, phone_y + 40)], fill=(245, 158, 11), width=22)

        # Glowing Smartphone
        draw.rounded_rectangle([phone_x - 38, phone_y - 75, phone_x + 38, phone_y + 75], radius=14, fill=(20, 24, 32), outline=(255, 255, 255), width=4)
        # Screen glow
        draw.rounded_rectangle([phone_x - 32, phone_y - 68, phone_x + 32, phone_y + 68], radius=10, fill=(56, 189, 248))

        # Light beam illuminating character's face!
        glow_cone = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(glow_cone)
        g_draw.polygon([(phone_x, phone_y), (cx - 120, cy - 80), (cx + 80, cy - 80)], fill=(56, 189, 248, 55))
        img.paste(Image.alpha_composite(img.convert("RGBA"), glow_cone).convert("RGB"))

        # Fast swiping thumb lines
        swipe_phase = (f % 12)
        swipe_y = phone_y + 30 - swipe_phase * 6
        draw.line([(phone_x, swipe_y), (phone_x, swipe_y - 25)], fill=(255, 255, 255), width=4)

        # Head & Dazed eyes staring at phone
        draw.ellipse([cx - r + 8, cy - r + 10, cx + r + 8, cy + r + 10], fill=(16, 18, 25))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255), outline=(22, 22, 28), width=9)

        # Hair
        draw.polygon([(cx - 20, cy - r + 10), (cx - 45, cy - r - 40), (cx, cy - r - 15)], fill=(22, 22, 28))
        draw.polygon([(cx, cy - r + 5), (cx + 25, cy - r - 45), (cx + 35, cy - r - 10)], fill=(22, 22, 28))

        # Staring eyes with blue screen reflection
        eye_y = cy - 8
        draw.ellipse([cx - 40 - 18, eye_y - 22, cx - 40 + 18, eye_y + 22], fill=(22, 22, 28))
        draw.ellipse([cx - 40 - 8, eye_y - 14, cx - 40 + 4, eye_y - 2], fill=(56, 189, 248)) # blue screen reflection!
        draw.ellipse([cx + 30 - 18, eye_y - 22, cx + 30 + 18, eye_y + 22], fill=(22, 22, 28))
        draw.ellipse([cx + 30 - 8, eye_y - 14, cx + 30 + 4, eye_y - 2], fill=(56, 189, 248))

        # Slightly open hypnotized mouth
        draw.ellipse([cx - 15, cy + 45, cx + 15, cy + 68], fill=(30, 20, 25))

        # Floating Video Feed Badges flying out of screen
        feed_items = [
            (110, 680, "🐱 Video Mèo Hài 01:00", (245, 158, 11)),
            (680, 720, "💃 Douyin Dance Trend", (236, 72, 153)),
            (100, 920, "🍜 Đồ Ăn Đêm Siêu Ngon", (16, 185, 129)),
            (690, 940, "💬 Tin Nhắn Lúc 2h Sáng", (168, 85, 247))
        ]
        for idx, (fx, fy, ftxt, fcol) in enumerate(feed_items):
            float_y = int(fy + math.sin(f * 0.2 + idx * 1.5) * 12)
            draw.rounded_rectangle([fx, float_y, fx + 280, float_y + 60], radius=14, fill=fcol, outline=(255, 255, 255), width=2)
            draw.text((fx + 16, float_y + 16), ftxt, font=font_tab, fill=(255, 255, 255))

    # -------------------------------------------------------------
    # SCENE 2: BRAINROT MELTDOWN - SIZZLING SMOKING BRAIN & DERP FACE
    # -------------------------------------------------------------
    elif stype == "ep2_brainrot_melt":
        # Glitch background lines
        for y in range(0, h, 60):
            draw.line([(0, y), (w, y)], fill=(20, 25, 40), width=1)

        cx, cy = 540, 920
        r = 135

        # Hoodie Shoulders
        draw.polygon([(cx - 200, 1120), (cx + 200, 1120), (cx + 240, h), (cx - 240, h)], fill=(245, 158, 11), outline=(22, 22, 28), width=8)

        # Head Circle
        draw.ellipse([cx - r + 8, cy - r + 10, cx + r + 8, cy + r + 10], fill=(16, 18, 25))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255), outline=(22, 22, 28), width=10)

        # Dizzy Spiral Eyes 🌀 🌀
        eye_y = cy - 15
        for sign in [-1, 1]:
            ex = cx + sign * 55
            # Draw spinning spiral
            for a_deg in range(0, 720, 20):
                rad = math.radians(a_deg + f * 18)
                dist = (a_deg / 720.0) * 32
                px = int(ex + math.cos(rad) * dist)
                py = int(eye_y + math.sin(rad) * dist)
                draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(239, 68, 68))

        # Derp Mouth with Drool dripping down ( ゜ρ ゜)
        mouth_y = cy + 55
        draw.rounded_rectangle([cx - 30, mouth_y, cx + 30, mouth_y + 35], radius=14, fill=(40, 25, 30), outline=(22, 22, 28), width=5)
        # Blue drool drop
        drool_len = int((f * 4) % 65)
        draw.line([(cx + 18, mouth_y + 25), (cx + 18, mouth_y + 35 + drool_len)], fill=(56, 189, 248), width=6)
        draw.ellipse([cx + 14, mouth_y + 32 + drool_len, cx + 22, mouth_y + 44 + drool_len], fill=(56, 189, 248))

        # Sizzling Melted Pink Brain on Top of Head!
        brain_y = cy - r - 45 + int(math.sin(f * 0.4) * 6)
        # Melted brain lobed shape
        draw.ellipse([cx - 85, brain_y - 45, cx - 10, brain_y + 35], fill=(255, 140, 170), outline=(22, 22, 28), width=5)
        draw.ellipse([cx - 35, brain_y - 65, cx + 35, brain_y + 25], fill=(255, 150, 180), outline=(22, 22, 28), width=5)
        draw.ellipse([cx + 10, brain_y - 45, cx + 85, brain_y + 35], fill=(255, 140, 170), outline=(22, 22, 28), width=5)
        # Brain wrinkles
        draw.arc([cx - 65, brain_y - 30, cx - 25, brain_y + 15], 30, 220, fill=(210, 80, 120), width=4)
        draw.arc([cx + 25, brain_y - 30, cx + 65, brain_y + 15], 320, 150, fill=(210, 80, 120), width=4)

        # Sizzling Steam Puffs ♨️
        for s_i in range(3):
            puff_y = int(brain_y - 70 - ((f * 3 + s_i * 45) % 150))
            puff_x = int(cx - 30 + s_i * 30 + math.sin(puff_y * 0.08) * 15)
            draw.text((puff_x, puff_y), "♨️", font=font_tab, fill=(255, 200, 120))

        # Giant Flashing Brainrot Alarm Badge!
        alarm_pulse = (math.sin(f * 0.35) + 1.0) / 2.0
        alarm_col = (int(255 * (0.85 + 0.15 * alarm_pulse)), int(40 * alarm_pulse), int(60 * alarm_pulse))
        draw.rounded_rectangle([120, 480, 960, 570], radius=24, fill=(20, 22, 34), outline=alarm_col, width=5)
        font_alarm = ImageFont.truetype(FONT_YAHEI, 38)
        draw.text((540, 502), "⚠️ CẢNH BÁO: THỐI NÃO 99%!", font=font_alarm, fill=alarm_col, anchor="mt")

    # -------------------------------------------------------------
    # SCENE 3: SNAP AWAKE, THROW PHONE AWAY & OPEN WINDOW
    # -------------------------------------------------------------
    elif stype == "ep2_wake_throw_phone":
        # Moonlit blue night room
        for y in range(0, bed_y, 4):
            p = y / float(bed_y)
            r = int(18 + 12 * p)
            g = int(24 + 16 * p)
            b = int(42 + 24 * p)
            draw.rectangle([0, y, w, y + 4], fill=(r, g, b))

        # Big Open Window in center with Crescent Moon 🌙
        wx1, wy1, wx2, wy2 = 280, 220, 800, 680
        draw.rounded_rectangle([wx1 - 12, wy1 - 12, wx2 + 12, wy2 + 12], radius=20, fill=(18, 22, 34))
        draw.rounded_rectangle([wx1, wy1, wx2, wy2], radius=14, fill=(24, 34, 58))
        # Crescent Moon
        draw.ellipse([wx1 + 80, wy1 + 60, wx1 + 170, wy1 + 150], fill=(255, 235, 140))
        draw.ellipse([wx1 + 110, wy1 + 50, wx1 + 190, wy1 + 140], fill=(24, 34, 58)) # moon cutout
        # Twinkling Stars
        for i, (sx, sy) in enumerate([(480, 320), (620, 280), (710, 380), (550, 450), (680, 520)]):
            star_twinkle = (math.sin(f * 0.2 + i) + 1.0) / 2.0
            col_s = (int(255 * star_twinkle), int(240 * star_twinkle), int(160 * star_twinkle))
            draw.text((sx, sy), "✦", font=font_tab, fill=col_s)

        # Character Standing Tall taking a Deep Breath!
        cx = 540
        breath = math.sin(f * 0.25) * 8
        cy = 920 + int(breath)
        r = 110

        # Hoodie Body (chest expanding)
        draw.polygon([(cx - 160 - int(breath), 1080), (cx + 160 + int(breath), 1080), (cx + 190, bed_y), (cx - 190, bed_y)], fill=(245, 158, 11), outline=(22, 22, 28), width=8)

        # Arms spread wide breathing fresh air!
        draw.line([(cx - 140, 1080), (cx - 240, 980)], fill=(245, 158, 11), width=24)
        draw.line([(cx - 140, 1080), (cx - 240, 980)], fill=(22, 22, 28), width=6)
        draw.line([(cx + 140, 1080), (cx + 240, 980)], fill=(245, 158, 11), width=24)
        draw.line([(cx + 140, 1080), (cx + 240, 980)], fill=(22, 22, 28), width=6)

        # Phone flying away on left with speed lines! *WHOOSH*
        fly_x = int(140 + math.sin(f * 0.2) * 15)
        fly_y = int(720 + math.cos(f * 0.2) * 15)
        draw.rounded_rectangle([fly_x - 30, fly_y - 50, fly_x + 30, fly_y + 50], radius=10, fill=(30, 35, 48), outline=(255, 255, 255), width=3)
        draw.text((fly_x - 12, fly_y - 18), "📱", font=font_tab, fill=(255, 255, 255))
        # Speed lines
        draw.line([(fly_x + 45, fly_y - 20), (fly_x + 100, fly_y - 35)], fill=(255, 255, 255), width=4)
        draw.line([(fly_x + 45, fly_y + 10), (fly_x + 110, fly_y + 10)], fill=(255, 255, 255), width=4)
        draw.line([(fly_x + 40, fly_y + 35), (fly_x + 95, fly_y + 50)], fill=(255, 255, 255), width=4)

        # Head & Serene Relieved Face
        draw.ellipse([cx - r + 8, cy - r + 10, cx + r + 8, cy + r + 10], fill=(16, 18, 25))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255), outline=(22, 22, 28), width=9)
        # Hair
        draw.polygon([(cx - 20, cy - r + 10), (cx - 45, cy - r - 40), (cx, cy - r - 15)], fill=(22, 22, 28))
        draw.polygon([(cx, cy - r + 5), (cx + 25, cy - r - 45), (cx + 35, cy - r - 10)], fill=(22, 22, 28))

        # Closed eyes smiling in fresh air ( ^ ‿ ^ )
        draw.arc([cx - 65, cy - 25, cx - 20, cy + 10], 180, 360, fill=(22, 22, 28), width=8)
        draw.arc([cx + 20, cy - 25, cx + 65, cy + 10], 180, 360, fill=(22, 22, 28), width=8)

        # Serene smiling mouth
        draw.arc([cx - 25, cy + 30, cx + 25, cy + 65], 20, 160, fill=(22, 22, 28), width=6)

        # Inhaling fresh air breeze spirals
        for b_i in range(3):
            b_y = 860 + b_i * 40
            b_x = int(cx + math.sin(f * 0.2 + b_i) * 20)
            draw.text((b_x - 30, b_y), "༄", font=font_tab, fill=(160, 220, 255))

    # -------------------------------------------------------------
    # SCENE 4: HEALTHY RECHARGED BRAIN, NIGHTCAP & THUMBS UP!
    # -------------------------------------------------------------
    elif stype == "ep2_sleep_thumbsup":
        # Warm twilight bedroom
        for y in range(0, bed_y, 4):
            p = y / float(bed_y)
            r = int(32 + 16 * p)
            g = int(36 + 18 * p)
            b = int(50 + 22 * p)
            draw.rectangle([0, y, w, y + 4], fill=(r, g, b))

        cx, cy = 540, 920
        r = 110

        # Cozy blanket covering body
        draw.rectangle([0, bed_y - 60, w, h], fill=(36, 46, 70))
        draw.line([(0, bed_y - 60), (w, bed_y - 60)], fill=(245, 158, 11), width=6)

        # Head with cute Nightcap (Mũ ngủ có cục bông pom-pom)
        cap_tip_x = cx + 80 + int(math.sin(f * 0.2) * 8)
        cap_tip_y = cy - r - 75
        draw.polygon([(cx - 70, cy - r + 15), (cx + 70, cy - r + 15), (cap_tip_x, cap_tip_y)], fill=(239, 68, 68), outline=(22, 22, 28), width=5)
        # White pom-pom
        draw.ellipse([cap_tip_x - 18, cap_tip_y - 18, cap_tip_x + 18, cap_tip_y + 18], fill=(255, 255, 255), outline=(22, 22, 28), width=4)

        # Head circle
        draw.ellipse([cx - r + 8, cy - r + 10, cx + r + 8, cy + r + 10], fill=(16, 18, 25))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255), outline=(22, 22, 28), width=9)

        # Recharged Cute Pink Brain hovering with Champion Headband!
        brain_y = cy - r - 120 + int(math.sin(f * 0.25) * 6)
        draw.ellipse([cx - 65, brain_y - 35, cx - 10, brain_y + 25], fill=(255, 160, 190), outline=(22, 22, 28), width=4)
        draw.ellipse([cx - 25, brain_y - 50, cx + 25, brain_y + 20], fill=(255, 170, 200), outline=(22, 22, 28), width=4)
        draw.ellipse([cx + 10, brain_y - 35, cx + 65, brain_y + 25], fill=(255, 160, 190), outline=(22, 22, 28), width=4)
        # Headband with Red Star ⭐
        draw.rounded_rectangle([cx - 55, brain_y - 15, cx + 55, brain_y + 8], radius=6, fill=(245, 158, 11), outline=(22, 22, 28), width=3)
        draw.text((cx - 8, brain_y - 14), "⭐", font=font_tab, fill=(255, 255, 255))

        # Winking Eye 😉 & Rosy Cheeks
        eye_y = cy - 8
        draw.ellipse([cx - 40 - 18, eye_y - 22, cx - 40 + 18, eye_y + 22], fill=(22, 22, 28))
        draw.ellipse([cx - 40 - 8, eye_y - 14, cx - 40 + 4, eye_y - 2], fill=(255, 255, 255))
        draw.arc([cx + 20, eye_y - 10, cx + 60, eye_y + 18], 180, 360, fill=(22, 22, 28), width=8)

        # Cheeks
        draw.ellipse([cx - 70, cy + 22, cx - 36, cy + 46], fill=(255, 140, 160))
        draw.ellipse([cx + 36, cy + 22, cx + 70, cy + 46], fill=(255, 140, 160))

        # Smile
        draw.rounded_rectangle([cx - 26, cy + 38, cx + 26, cy + 68], radius=12, fill=(35, 20, 25))
        draw.ellipse([cx - 12, cy + 52, cx + 12, cy + 65], fill=(255, 120, 140))

        # Hand giving GIANT THUMBS UP 👍
        thumb_x, thumb_y = cx + 190, cy + 20
        font_emoji = ImageFont.truetype(FONT_SEGOE, 78)
        draw.text((thumb_x - 24, thumb_y - 70), "👍", font=font_emoji, fill=(255, 215, 0))

        # Zzz Sleep Bubbles floating
        for z_i in range(3):
            z_y = int(cy - 60 - ((f * 2.5 + z_i * 65) % 220))
            z_x = int(cx - 120 + math.sin(z_y * 0.05) * 20)
            draw.text((z_x, z_y), "💤", font=font_tab, fill=(200, 225, 255))

        # Golden radiating sparkles ✨
        for s_i in range(8):
            ang = s_i * (math.pi / 4.0) + (f * 0.05)
            sx = int(cx + math.cos(ang) * 195)
            sy = int(cy + math.sin(ang) * 195)
            draw.text((sx - 10, sy - 10), "✨", font=font_tab, fill=(255, 235, 120))

    # 3. Subtitles & UI
    draw_subtitles_and_ui(draw, scene)

    return img

# ==========================================
# RENDER SCENE TO MP4
# ==========================================

def render_scene_clip(scene: dict, dur: float) -> Path:
    fps = 30
    total_frames = int(round(dur * fps))
    scene_id = scene["id"]
    out_clip = WORK_DIR / f"pure_ep2_clip_{scene_id}.mp4"

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    vw = cv2.VideoWriter(str(out_clip), fourcc, fps, (1080, 1920))

    print(f"    -> Rendering {total_frames} frames ({dur:.2f}s) of Episode 2 animation...")

    for f in range(total_frames):
        composed_img = render_ep2_frame(scene, f, total_frames)
        bgr = cv2.cvtColor(np.array(composed_img), cv2.COLOR_RGB2BGR)
        vw.write(bgr)

    vw.release()
    return out_clip

# ==========================================
# MAIN PRODUCTION PIPELINE
# ==========================================

def main():
    print("=" * 80)
    print(" STICKMAN STUDIO - EPISODE 2: HỘI CHỨNG THỐI NÃO (BRAINROT • 脑腐)")
    print("=" * 80)

    # 1. Foley SFX
    print("\n[1/5] Khởi tạo âm thanh Foley (Swipe, Glitch, Thud, Ding)...")
    create_foley_sfx(WORK_DIR)

    # 2. Native Chinese Voiceovers
    print("\n[2/5] Tạo giọng đọc bản xứ tiếng Trung Douyin chuẩn Bắc Kinh (Xiaoxiao)...")
    durations = asyncio.run(generate_voices(WORK_DIR))

    # Concatenate voice tracks with pad
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
    bgm_source = WORKSPACE_ROOT / "MoneyPrinterTurbo" / "resource" / "songs" / "output002.mp3"
    if not bgm_source.exists():
        bgm_source = WORKSPACE_ROOT / "MoneyPrinterTurbo" / "resource" / "songs" / "output000.mp3"

    d1 = int(250)
    d2 = int((durations[0] + 0.6) * 1000)
    d3 = int((durations[0] + durations[1] + 0.8) * 1000)
    d4 = int((sum(durations[:3]) + 1.6) * 1000)

    master_audio = WORK_DIR / "master_audio.mp3"
    cmd_audio_mix = [
        FFMPEG, "-y",
        "-i", str(raw_voice),
        "-i", str(bgm_source),
        "-i", str(WORK_DIR / "sfx_swipe.wav"),
        "-i", str(WORK_DIR / "sfx_glitch.wav"),
        "-i", str(WORK_DIR / "sfx_thud.wav"),
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

    # 4. Render 100% Pure Animation Scenes
    print("\n[4/5] Render 4 cảnh Hoạt Hình 100% thuần túy...")
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

    out_path = OUT_DIR / "video_hoat_hinh_tap2_thoi_nao_brainrot.mp4"

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
    desktop_copy = Path("C:/Users/User/Desktop/video_hoat_hinh_tap2_thoi_nao_brainrot.mp4")
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
        title="🧠 [TẬP 2] HOẠT HÌNH: Hội Chứng 'Thối Não' (Brainrot) Vì Lướt Mạng Xã Hội Đêm",
        description=(
            "Tập 2 cực hài hước & chữa lành: 'Định cầm máy 1 phút, ai ngờ lướt luôn 2 tiếng'. "
            "Hiện tượng não bốc khói xì xèo, mắt xoắn ốc ngơ ngác, và lời khuyên bỏ điện thoại đi ngủ sớm! "
            "100% Hoạt hình Chibi thuần túy, phụ đề song ngữ HSK siêu chất lượng!"
        ),
        app_name="StickmanAnimationEp2",
        tags=["HoatHinhTap2", "ThoiNao", "Brainrot", "NaoHu", "SongNguTrungViet", "DouyinViral"],
        blocking=True
    )
    if ok:
        print(f"✅ {res}")
    else:
        print(f"⚠️ Dispatch notice: {res}")

if __name__ == "__main__":
    main()
