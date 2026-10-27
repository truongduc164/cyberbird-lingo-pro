#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pure 100% Animation Studio (Hoạt Hình 100% Chuyên Biệt - Siêu Sạch Sẽ, Đẳng Cấp Douyin / TikTok)
================================================================================================
- 100% Hoạt họa thuần túy (Pure Animation - Tuyệt đối không ghép video nền thật gây rối mắt).
- Thế giới hoạt hình đồng nhất, ấm cúng (Cozy Anime Room):
    + Cửa sổ nhìn ra trời chiều / mưa rơi tí tách
    + Đèn bàn anime tỏa ánh sáng vàng ấm
    + Bàn gỗ hoạt họa, kệ sách anime màu pastel
- Nhân vật Chibi / Người Que Nghệ Thuật (Artistic Chibi Stickman):
    + Mặc áo hoodie vàng mù tạt (Mustard Hoodie) hoạt hình, có túi kangaroo & dây rút
    + Chỏm tóc anime lắc lư, biểu cảm mắt to hoạt hình có catchlight long lanh
    + Cảnh 1: Gõ laptop quả táo phát sáng, não quá tải xoay vòng 🌀, 5 tab hoạt hình nảy tưng bừng.
    + Cảnh 2: Phòng chuyển tông mưa đêm, nhân vật xẹp lép chảy dài trên bàn, cột pin khổng lồ nhấp nháy đỏ [🪫 1%].
    + Cảnh 3: Bừng sáng trở lại, đeo kính trí thức 🤓, vung que chỉ bảng bấm tắt tab thừa -> sao vàng bùng nổ ✨.
    + Cảnh 4: Nhấp ngụm cà phê thơm lừng khói trái tim ♡, nháy mắt 😉 giơ ngón tay LIKE 👍 tỏa hào quang rực rỡ.
- Phụ đề chuẩn phim hoạt hình anime Netflix / Douyin (thanh thoát ở đáy, không che cảnh).
- Giọng đọc Xiaoxiao bản xứ + Lo-fi BGM + Âm thanh Foley đồng bộ 100%.
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
WORK_DIR = WORKSPACE_ROOT / "temp_pure_animation"
WORK_DIR.mkdir(exist_ok=True)
OUT_DIR = WORKSPACE_ROOT / "storage"
OUT_DIR.mkdir(exist_ok=True)

FONT_YAHEI = r"C:\Windows\Fonts\msyh.ttc"
FONT_SEGOE = r"C:\Windows\Fonts\segoeui.ttf"

SCENES = [
    {
        "id": 1,
        "type": "pure_anim_100tabs",
        "title": "Scene 1 • Não Mở 100 Tab",
        "cn": "下午三点，脑子开了100个网页。",
        "pinyin": "xià wǔ sān diǎn, nǎo zi kāi le 100 gè wǎng yè.",
        "vi": "Ba giờ chiều, não tôi đang mở 100 tab trình duyệt.",
        "chip1": "脑子 (nǎozi): Bộ não",
        "chip2": "网页 (wǎngyè): Tab web",
        "tag": "☕ CHUYỆN 3H CHIỀU • 下午三点",
        "mood": "warm",
        "extra_pad": 0.8
    },
    {
        "id": 2,
        "type": "pure_anim_lowbattery",
        "title": "Scene 2 • Pin Chỉ Còn 1%",
        "cn": "身体坐着，电量只剩百分之一。",
        "pinyin": "shēn tǐ zuò zhe, diàn liàng zhǐ shèng bǎi fēn zhī yī.",
        "vi": "Thân thể ngồi đó, nhưng pin chỉ còn đúng 1%.",
        "chip1": "身体 (shēntǐ): Thân thể",
        "chip2": "电量 (diànliàng): Mức pin",
        "tag": "🪫 CẠN PIN 1% • 电量不足",
        "mood": "rain_night",
        "extra_pad": 0.7
    },
    {
        "id": 3,
        "type": "pure_anim_closetabs",
        "title": "Scene 3 • Cứ Từ Từ, Tắt Bớt Tab Đi",
        "cn": "慢慢来，先把不需要的网页关掉。",
        "pinyin": "màn man lái, xiān bǎ bù xū yào de wǎng yè guān diào.",
        "vi": "Cứ từ từ thôi, hãy tắt bớt những tab không cần thiết đi.",
        "chip1": "慢慢来 (mànmàn lái): Từ từ thôi",
        "chip2": "关掉 (guāndiào): Tắt đi / Đóng lại",
        "tag": "🌿 TĨNH TÂM • 慢慢来",
        "mood": "warm",
        "extra_pad": 0.7
    },
    {
        "id": 4,
        "type": "pure_anim_coffee_thumbsup",
        "title": "Scene 4 • Tha Thứ Cho Bản Thân, Mọi Chuyện Còn Kịp",
        "cn": "放过自己，一切都还来得及。",
        "pinyin": "fàng guò zì jǐ, yí qiè dōu hái lái de jí.",
        "vi": "Tha thứ cho chính mình, mọi chuyện đều còn kịp.",
        "chip1": "放过 (fàngguò): Tha thứ / Bỏ qua",
        "chip2": "来得及 (láidejí): Còn kịp",
        "tag": "✨ CHỮA LÀNH • 一切都还来得及",
        "mood": "golden_hour",
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

    # 1. Pop Sound (high punchy bubble pop)
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
# 100% PURE ANIMATION GRAPHICS ENGINE
# ==========================================

def draw_cozy_anime_room(draw: ImageDraw.ImageDraw, f: int, mood: str = "warm"):
    w, h = 1080, 1920
    desk_y = 1260

    # 1. Wall with gradient
    for y in range(0, desk_y, 4):
        p = y / float(desk_y)
        if mood == "warm":
            r = int(28 + 16 * p)
            g = int(32 + 18 * p)
            b = int(46 + 26 * p)
        elif mood == "golden_hour":
            r = int(45 + 25 * p)
            g = int(36 + 18 * p)
            b = int(48 + 15 * p)
        else: # rain_night
            r = int(14 + 8 * p)
            g = int(18 + 10 * p)
            b = int(30 + 16 * p)
        draw.rectangle([0, y, w, y + 4], fill=(r, g, b))

    # 2. Window on Left
    wx1, wy1, wx2, wy2 = 70, 220, 360, 680
    draw.rounded_rectangle([wx1 - 12, wy1 - 12, wx2 + 12, wy2 + 12], radius=18, fill=(16, 18, 25))

    if mood in ["warm", "golden_hour"]:
        # Warm sunset sky
        draw.rounded_rectangle([wx1, wy1, wx2, wy2], radius=12, fill=(255, 170, 115))
        # Sun
        sun_y = 300 + int(math.sin(f * 0.05) * 5)
        draw.ellipse([wx1 + 40, sun_y, wx1 + 130, sun_y + 90], fill=(255, 245, 195))
        # Warm clouds
        cloud_x = (wx1 + 60 + int(f * 0.5)) % (wx2 - 50)
        draw.ellipse([cloud_x, wy1 + 90, cloud_x + 120, wy1 + 145], fill=(255, 205, 160))
        draw.ellipse([cloud_x + 30, wy1 + 75, cloud_x + 100, wy1 + 130], fill=(255, 220, 180))
    else: # rain night
        draw.rounded_rectangle([wx1, wy1, wx2, wy2], radius=12, fill=(22, 28, 48))
        # Animated raindrops
        for i in range(8):
            rx = int(wx1 + 20 + ((i * 37 + f * 4) % (wx2 - wx1 - 40)))
            ry = int(wy1 + 10 + ((i * 53 + f * 12) % (wy2 - wy1 - 20)))
            draw.line([(rx, ry), (rx - 10, ry + 25)], fill=(120, 160, 220), width=3)

    # Window wooden frame
    draw.line([(wx1, (wy1 + wy2) // 2), (wx2, (wy1 + wy2) // 2)], fill=(16, 18, 25), width=8)
    draw.line([((wx1 + wx2) // 2, wy1), ((wx1 + wx2) // 2, wy2)], fill=(16, 18, 25), width=8)

    # 3. Bookshelf on Right
    draw.rounded_rectangle([730, 220, 1010, 680], radius=16, fill=(38, 32, 42), outline=(52, 45, 58), width=4)
    shelf_colors = [(244, 63, 94), (59, 130, 246), (16, 185, 129), (245, 158, 11), (168, 85, 247)]
    for i, col in enumerate(shelf_colors):
        bx = 750 + i * 48
        draw.rounded_rectangle([bx, 340, bx + 38, 470], radius=5, fill=col)
        draw.rounded_rectangle([bx, 510, bx + 38, 640], radius=5, fill=shelf_colors[(i + 2) % 5])

    # Cute potted succulent on top shelf
    draw.polygon([(820, 310), (860, 310), (850, 340), (830, 340)], fill=(200, 140, 100))
    draw.ellipse([825, 285, 855, 315], fill=(52, 211, 153))

    # 4. Desk Lamp (Top Right of desk)
    lamp_x, lamp_y = 660, 840
    if mood != "rain_night":
        # Lamp stand
        draw.line([(lamp_x, desk_y), (lamp_x + 35, lamp_y + 60)], fill=(210, 170, 100), width=10)
        draw.line([(lamp_x + 35, lamp_y + 60), (lamp_x - 35, lamp_y)], fill=(210, 170, 100), width=8)
        # Lamp shade
        draw.polygon([(lamp_x - 65, lamp_y + 20), (lamp_x - 10, lamp_y - 20), (lamp_x + 20, lamp_y + 10), (lamp_x - 35, lamp_y + 50)], fill=(245, 158, 11))
        # Soft cone of warm light
        lamp_glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        lg_draw = ImageDraw.Draw(lamp_glow)
        lg_draw.polygon([(lamp_x - 35, lamp_y + 40), (250, desk_y), (850, desk_y)], fill=(255, 235, 150, 45))
        # (will composite later)

    # 5. Wooden Desk Surface
    draw.rectangle([0, desk_y - 26, w, desk_y], fill=(68, 52, 44))
    draw.line([(0, desk_y - 26), (w, desk_y - 26)], fill=(245, 185, 130), width=6)
    draw.rectangle([0, desk_y, w, h], fill=(36, 26, 22))

def draw_chibi_stickman_base(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, f: int, mood: str = "normal"):
    """Renders the Chibi Anime character with Mustard Hoodie & expressive face"""
    # 1. Hair Tuft (3 anime bangs swaying gently)
    sway = int(math.sin(f * 0.25) * 3)
    draw.polygon([(cx - 20, cy - r + 10), (cx - 45 + sway, cy - r - 45), (cx, cy - r - 15)], fill=(22, 22, 28))
    draw.polygon([(cx, cy - r + 5), (cx + 25 + sway, cy - r - 50), (cx + 35, cy - r - 10)], fill=(22, 22, 28))
    draw.polygon([(cx + 20, cy - r + 10), (cx + 55 + sway, cy - r - 38), (cx + 40, cy - r - 5)], fill=(22, 22, 28))

    # 2. Head drop shadow & main circle
    draw.ellipse([cx - r + 8, cy - r + 10, cx + r + 8, cy + r + 10], fill=(16, 18, 25))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255), outline=(22, 22, 28), width=9)

    # 3. Eyes & Expressions
    eye_offset = 44
    eye_y = cy - 10
    is_blink = (f % 60) in [0, 1, 2]

    if is_blink:
        draw.arc([cx - eye_offset - 22, eye_y - 14, cx - eye_offset + 22, eye_y + 14], 180, 360, fill=(22, 22, 28), width=8)
        draw.arc([cx + eye_offset - 22, eye_y - 14, cx + eye_offset + 22, eye_y + 14], 180, 360, fill=(22, 22, 28), width=8)
    elif mood == "exhausted":
        # Tired flat slit eyes - -
        draw.line([(cx - eye_offset - 22, eye_y), (cx - eye_offset + 22, eye_y)], fill=(22, 22, 28), width=8)
        draw.line([(cx + eye_offset - 22, eye_y), (cx + eye_offset + 22, eye_y)], fill=(22, 22, 28), width=8)
    elif mood == "wink":
        # Left eye wide cartoon, right eye winking
        draw.ellipse([cx - eye_offset - 18, eye_y - 24, cx - eye_offset + 18, eye_y + 24], fill=(22, 22, 28))
        draw.ellipse([cx - eye_offset - 8, eye_y - 16, cx - eye_offset + 4, eye_y - 4], fill=(255, 255, 255))
        draw.arc([cx + eye_offset - 24, eye_y - 12, cx + eye_offset + 24, eye_y + 20], 180, 360, fill=(22, 22, 28), width=8)
    elif mood == "spectacles":
        # Round Golden Spectacles 🤓
        draw.ellipse([cx - 65, cy - 35, cx - 12, cy + 18], outline=(245, 158, 11), width=6)
        draw.ellipse([cx + 12, cy - 35, cx + 65, cy + 18], outline=(245, 158, 11), width=6)
        draw.line([(cx - 12, cy - 8), (cx + 12, cy - 8)], fill=(245, 158, 11), width=5)
        # Eyes behind spectacles
        draw.ellipse([cx - 42, cy - 12, cx - 30, cy], fill=(22, 22, 28))
        draw.ellipse([cx + 30, cy - 12, cx + 42, cy], fill=(22, 22, 28))
    else: # normal big anime eyes
        for sign in [-1, 1]:
            ex = cx + sign * eye_offset
            draw.ellipse([ex - 20, eye_y - 25, ex + 20, eye_y + 25], fill=(22, 22, 28))
            draw.ellipse([ex - 10, eye_y - 17, ex - 1, eye_y - 5], fill=(255, 255, 255))
            draw.ellipse([ex + 4, eye_y + 5, ex + 9, eye_y + 10], fill=(255, 255, 255))

    # 4. Mouth (Animated speech phonemes)
    mouth_y = cy + 48
    if mood == "exhausted":
        draw.arc([cx - 24, mouth_y - 5, cx + 24, mouth_y + 25], 0, 180, fill=(22, 22, 28), width=6)
    elif mood in ["wink", "spectacles"]:
        draw.arc([cx - 26, mouth_y - 15, cx + 26, mouth_y + 20], 20, 160, fill=(22, 22, 28), width=6)
    else:
        # Talking open mouth
        mouth_ph = (f % 14)
        if mouth_ph < 5:
            draw.line([(cx - 22, mouth_y), (cx + 22, mouth_y)], fill=(22, 22, 28), width=7)
        elif mouth_ph < 10:
            draw.ellipse([cx - 18, mouth_y - 6, cx + 18, mouth_y + 22], fill=(35, 20, 25), outline=(22, 22, 28), width=4)
        else:
            draw.rounded_rectangle([cx - 28, mouth_y - 8, cx + 28, mouth_y + 24], radius=12, fill=(35, 20, 25), outline=(22, 22, 28), width=4)
            draw.ellipse([cx - 12, mouth_y + 8, cx + 12, mouth_y + 22], fill=(255, 110, 130))

def draw_mustard_hoodie_body(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, desk_y: int):
    """Draws the Mustard/Orange cartoon hoodie with kangaroo pocket & strings"""
    torso_top_y = cy + r - 10
    # Main hoodie torso
    draw.polygon([(cx - 170, torso_top_y + 40), (cx + 170, torso_top_y + 40), (cx + 195, desk_y), (cx - 195, desk_y)], fill=(245, 158, 11), outline=(22, 22, 28), width=8)

    # Kangaroo front pocket
    draw.rounded_rectangle([cx - 95, desk_y - 130, cx + 95, desk_y - 20], radius=14, fill=(217, 119, 6), outline=(22, 22, 28), width=6)

    # Hoodie collar V
    draw.polygon([(cx - 55, torso_top_y + 5), (cx + 55, torso_top_y + 5), (cx, torso_top_y + 70)], fill=(217, 119, 6), outline=(22, 22, 28), width=6)

    # White drawstrings
    draw.line([(cx - 28, torso_top_y + 50), (cx - 28, torso_top_y + 140)], fill=(255, 255, 255), width=6)
    draw.line([(cx + 28, torso_top_y + 50), (cx + 28, torso_top_y + 140)], fill=(255, 255, 255), width=6)
    # Silver aglets
    draw.rectangle([cx - 32, torso_top_y + 135, cx - 24, torso_top_y + 150], fill=(200, 205, 220))
    draw.rectangle([cx + 24, torso_top_y + 135, cx + 32, torso_top_y + 150], fill=(200, 205, 220))

def draw_subtitles_and_ui(draw: ImageDraw.ImageDraw, scene: dict):
    """Renders the pristine anime subtitle box, top badge, and vocab chips"""
    font_badge = ImageFont.truetype(FONT_YAHEI, 28)
    font_pinyin = ImageFont.truetype(FONT_SEGOE, 32)
    font_hanzi = ImageFont.truetype(FONT_YAHEI, 52)
    font_vi = ImageFont.truetype(FONT_SEGOE, 34)
    font_chip = ImageFont.truetype(FONT_YAHEI, 28)

    # 1. Top Badge (Anime Tag)
    badge_x1, badge_y1 = 65, 110
    badge_x2, badge_y2 = 560, 180
    draw.rounded_rectangle([badge_x1, badge_y1, badge_x2, badge_y2], radius=22, fill=(18, 22, 32, 225), outline=(255, 255, 255), width=3)
    draw.text((badge_x1 + 28, badge_y1 + 18), scene["tag"], font=font_badge, fill=(255, 230, 140))

    # 2. Subtitle Box (Frosted Glass Pill in Safe Zone)
    sub_x1, sub_y1 = 55, 1410
    sub_x2, sub_y2 = 1025, 1635
    draw.rounded_rectangle([sub_x1, sub_y1, sub_x2, sub_y2], radius=28, fill=(14, 18, 28, 235), outline=(246, 211, 101), width=3)
    # Inner gold border
    draw.rounded_rectangle([sub_x1 + 5, sub_y1 + 5, sub_x2 - 5, sub_y2 - 5], radius=24, outline=(255, 255, 255, 50), width=1)

    # Line 1: Pinyin
    draw.text((540, 1432), scene["pinyin"], font=font_pinyin, fill=(254, 230, 138), anchor="mt")

    # Line 2: Hanzi (Big, crisp, YaHei)
    draw.text((540, 1485), scene["cn"], font=font_hanzi, fill=(255, 255, 255), anchor="mt")

    # Line 3: Vietnamese Translation (Gentle healing tone)
    draw.text((540, 1565), scene["vi"], font=font_vi, fill=(226, 232, 240), anchor="mt")

    # 3. Vocab Sticky Notes (2 bottom chips)
    chip1_box = [80, 1660, 520, 1728]
    chip2_box = [560, 1660, 1000, 1728]

    draw.rounded_rectangle(chip1_box, radius=18, fill=(22, 28, 42, 240), outline=(255, 255, 255, 200), width=2)
    draw.text((chip1_box[0] + 25, chip1_box[1] + 18), f"🏷️ {scene['chip1']}", font=font_chip, fill=(255, 255, 255))

    draw.rounded_rectangle(chip2_box, radius=18, fill=(22, 28, 42, 240), outline=(255, 255, 255, 200), width=2)
    draw.text((chip2_box[0] + 25, chip2_box[1] + 18), f"🏷️ {scene['chip2']}", font=font_chip, fill=(255, 255, 255))

# ==========================================
# SCENE RENDERING PIPELINE
# ==========================================

def render_pure_animation_frame(scene: dict, f: int, total_frames: int) -> Image.Image:
    w, h = 1080, 1920
    desk_y = 1260
    stype = scene["type"]
    mood = scene.get("mood", "warm")

    img = Image.new("RGB", (w, h), (24, 26, 36))
    draw = ImageDraw.Draw(img)

    # 1. Background Anime Room
    draw_cozy_anime_room(draw, f, mood)

    font_tab = ImageFont.truetype(FONT_SEGOE, 23)

    # -----------------------------------------------------------------
    # SCENE 1: 100 TABS SWIRLING & FRANTIC TYPING ON LAPTOP
    # -----------------------------------------------------------------
    if stype == "pure_anim_100tabs":
        head_cx = 540
        head_cy = 880 + int(math.sin(f * 0.45) * 7)
        head_r = 110

        # Hoodie Body
        draw_mustard_hoodie_body(draw, head_cx, head_cy, head_r, desk_y)

        # Arms typing fast
        arm_phase = (f % 6)
        hand_l_y = desk_y - 30 + (8 if arm_phase < 3 else -6)
        hand_r_y = desk_y - 30 + (-6 if arm_phase < 3 else 8)

        draw.line([(head_cx - 140, head_cy + head_r + 40), (head_cx - 85, hand_l_y)], fill=(245, 158, 11), width=26)
        draw.line([(head_cx - 140, head_cy + head_r + 40), (head_cx - 85, hand_l_y)], fill=(22, 22, 28), width=6)

        draw.line([(head_cx + 140, head_cy + head_r + 40), (head_cx + 85, hand_r_y)], fill=(245, 158, 11), width=26)
        draw.line([(head_cx + 140, head_cy + head_r + 40), (head_cx + 85, hand_r_y)], fill=(22, 22, 28), width=6)

        # Animated Glowing Laptop on desk
        lap_x1, lap_x2 = 410, 670
        draw.polygon([(440, desk_y - 95), (640, desk_y - 95), (lap_x2, desk_y), (lap_x1, desk_y)], fill=(32, 38, 52), outline=(22, 22, 28), width=7)
        draw.polygon([(455, desk_y - 85), (625, desk_y - 85), (lap_x2 - 15, desk_y - 10), (lap_x1 + 15, desk_y - 10)], fill=(56, 189, 248))
        # Apple logo glow
        draw.ellipse([532, desk_y - 58, 548, desk_y - 40], fill=(255, 255, 255))

        # Typing sparks jumping off keys
        spark_x = (head_cx - 60) if arm_phase < 3 else (head_cx + 60)
        draw.line([(spark_x, desk_y - 40), (spark_x - 14, desk_y - 60)], fill=(255, 240, 120), width=4)
        draw.line([(spark_x, desk_y - 40), (spark_x + 14, desk_y - 60)], fill=(255, 240, 120), width=4)

        # Head & Face
        draw_chibi_stickman_base(draw, head_cx, head_cy, head_r, f, mood="normal")

        # Rotating Overload Swirl above head
        swirl_angle = (f * 15) % 360
        draw.arc([head_cx - 65, head_cy - head_r - 85, head_cx + 65, head_cy - head_r + 35], swirl_angle, swirl_angle + 270, fill=(255, 220, 80), width=7)

        # 5 Floating Colorful Browser Tab Cards
        tabs = [
            (80, 660, "🔥 TAB 99+: Báo cáo!", (239, 68, 68)),
            (700, 620, "💸 Tiền nhà tháng này?", (245, 158, 11)),
            (75, 900, "🍜 Trưa nay ăn gì?", (14, 165, 233)),
            (715, 880, "💬 Quên trả lời tin nhắn!", (168, 85, 247)),
            (380, 540, "⚠️ DEADLINE SẮP TỚI!", (236, 72, 153))
        ]
        for idx, (tx, ty, text, col) in enumerate(tabs):
            fy = int(ty + math.sin(f * 0.22 + idx * 1.3) * 14)
            # Tab shadow
            draw.rounded_rectangle([tx - 2, fy - 2, tx + 292, fy + 72], radius=18, fill=(12, 14, 20))
            draw.rounded_rectangle([tx, fy, tx + 286, fy + 64], radius=14, fill=col, outline=(255, 255, 255), width=3)
            # Mini chrome title buttons [x] [-] [+]
            draw.ellipse([tx + 14, fy + 12, tx + 24, fy + 22], fill=(255, 255, 255))
            draw.ellipse([tx + 30, fy + 12, tx + 40, fy + 22], fill=(255, 255, 255))
            draw.text((tx + 20, fy + 26), text, font=font_tab, fill=(255, 255, 255))

    # -----------------------------------------------------------------
    # SCENE 2: LOW BATTERY 1% SLUMPED ON DESK (RAIN NIGHT MOOD)
    # -----------------------------------------------------------------
    elif stype == "pure_anim_lowbattery":
        cx = 540
        cy = 1120 + int(math.sin(f * 0.15) * 4)
        r = 110

        # Slumped hoodie puddle on desk
        draw.polygon([(cx - 220, desk_y), (cx + 220, desk_y), (cx + 170, desk_y - 70), (cx - 170, desk_y - 70)], fill=(217, 119, 6), outline=(22, 22, 28), width=8)

        # Head resting flat horizontally on desk
        draw.ellipse([cx - r + 8, cy - r + 38, cx + r + 8, cy + r + 38], fill=(16, 18, 25))
        draw.ellipse([cx - r, cy - r + 30, cx + r, cy + r + 30], fill=(255, 255, 255), outline=(22, 22, 28), width=9)

        # Exhausted face
        draw_chibi_stickman_base(draw, cx, cy + 30, r, f, mood="exhausted")

        # Giant Glowing Low Battery Icon [ 🪫 1% ]
        bat_cx, bat_cy = 540, 680
        bat_pulse = (math.sin(f * 0.28) + 1.0) / 2.0
        glow_color = (int(255 * (0.8 + 0.2 * bat_pulse)), int(40 * bat_pulse), int(60 * bat_pulse))

        # Battery body shadow & body
        draw.rounded_rectangle([bat_cx - 165, bat_cy - 75, bat_cx + 165, bat_cy + 75], radius=26, fill=(12, 14, 20))
        draw.rounded_rectangle([bat_cx - 160, bat_cy - 70, bat_cx + 160, bat_cy + 70], radius=24, fill=(20, 24, 36), outline=(255, 255, 255), width=5)
        # Terminal cap
        draw.rounded_rectangle([bat_cx + 160, bat_cy - 25, bat_cx + 184, bat_cy + 25], radius=8, fill=(255, 255, 255))

        # 1% Red indicator bar
        draw.rounded_rectangle([bat_cx - 145, bat_cy - 55, bat_cx - 85, bat_cy + 55], radius=10, fill=glow_color)

        # 1% Text
        font_bat = ImageFont.truetype(FONT_SEGOE, 56)
        draw.text((bat_cx + 25, bat_cy - 38), "1%", font=font_bat, fill=glow_color)

        # Electric zaps crackling
        zap_angle = f * 0.2
        for s_idx in range(4):
            sx = int(bat_cx + math.cos(zap_angle + s_idx * 1.57) * 205)
            sy = int(bat_cy + math.sin(zap_angle + s_idx * 1.57) * 98)
            draw.text((sx, sy), "⚡", font=font_tab, fill=(255, 230, 80))

        # Zzz sleep bubbles rising
        for z_i in range(3):
            z_y = int(cy - 40 - ((f * 3 + z_i * 60) % 250))
            z_x = int(cx + 90 + math.sin(z_y * 0.05) * 25)
            draw.text((z_x, z_y), "💤", font=font_tab, fill=(200, 225, 255))

    # -----------------------------------------------------------------
    # SCENE 3: SPECTACLES, MAGIC WAND CLOSING TABS (WARM ROOM)
    # -----------------------------------------------------------------
    elif stype == "pure_anim_closetabs":
        head_cx = 450
        head_cy = 880 + int(math.sin(f * 0.3) * 5)
        head_r = 110

        # Hoodie Body
        draw_mustard_hoodie_body(draw, head_cx, head_cy, head_r, desk_y)

        # Left arm holding Golden Wand pointing UP to the tab!
        wand_tip_x = 760 + int(math.sin(f * 0.2) * 8)
        wand_tip_y = 640 + int(math.cos(f * 0.2) * 8)
        hand_x, hand_y = head_cx + 170, head_cy + 50

        draw.line([(head_cx + 140, head_cy + head_r + 30), (hand_x, hand_y)], fill=(245, 158, 11), width=24)
        draw.line([(head_cx + 140, head_cy + head_r + 30), (hand_x, hand_y)], fill=(22, 22, 28), width=6)

        # Golden Wand
        draw.line([(hand_x, hand_y), (wand_tip_x, wand_tip_y)], fill=(246, 211, 101), width=10)
        draw.ellipse([wand_tip_x - 14, wand_tip_y - 14, wand_tip_x + 14, wand_tip_y + 14], fill=(255, 255, 255))

        # Right arm on hip
        draw.line([(head_cx - 140, head_cy + head_r + 30), (head_cx - 100, head_cy + head_r + 100)], fill=(245, 158, 11), width=24)

        # Head with Spectacles 🤓
        draw_chibi_stickman_base(draw, head_cx, head_cy, head_r, f, mood="spectacles")

        # Tab exploding at Wand Tip!
        pop_rad = 35 + int((f * 4.5) % 100)
        draw.arc([wand_tip_x - pop_rad, wand_tip_y - pop_rad, wand_tip_x + pop_rad, wand_tip_y + pop_rad], 0, 360, fill=(255, 230, 100), width=5)

        # Burst stars ⭐ ✨
        for s_idx in range(8):
            ang = s_idx * (math.pi / 4.0) + (f * 0.1)
            dist = pop_rad + 25
            sx = int(wand_tip_x + math.cos(ang) * dist)
            sy = int(wand_tip_y + math.sin(ang) * dist)
            draw.text((sx, sy), "✨", font=font_tab, fill=(255, 240, 120))

        # Green success stamp [ ✔ ĐÃ ĐÓNG TAB THỪA ]
        draw.rounded_rectangle([wand_tip_x - 30, wand_tip_y - 120, wand_tip_x + 240, wand_tip_y - 65], radius=16, fill=(16, 185, 129), outline=(255, 255, 255), width=3)
        draw.text((wand_tip_x - 10, wand_tip_y - 106), "✔ ĐÃ ĐÓNG TAB THỪA", font=font_tab, fill=(255, 255, 255))

    # -----------------------------------------------------------------
    # SCENE 4: COZY COFFEE SIPPING, WINK & GIANT THUMBS UP (GOLDEN HOUR)
    # -----------------------------------------------------------------
    elif stype == "pure_anim_coffee_thumbsup":
        head_cx = 540
        head_cy = 880 + int(math.sin(f * 0.25) * 5)
        head_r = 110

        # Hoodie Body
        draw_mustard_hoodie_body(draw, head_cx, head_cy, head_r, desk_y)

        # Head with Winking eye 😉 & Blush Cheeks
        draw_chibi_stickman_base(draw, head_cx, head_cy, head_r, f, mood="wink")

        # Rosy Blush Cheeks
        draw.ellipse([head_cx - 70, head_cy + 22, head_cx - 36, head_cy + 46], fill=(255, 140, 160))
        draw.ellipse([head_cx + 36, head_cy + 22, head_cx + 70, head_cy + 46], fill=(255, 140, 160))

        # Left arm holding ceramic coffee cup
        cup_x, cup_y = head_cx - 120, desk_y - 60
        draw.line([(head_cx - 140, head_cy + head_r + 30), (cup_x + 10, cup_y + 10)], fill=(245, 158, 11), width=24)
        draw.line([(head_cx - 140, head_cy + head_r + 30), (cup_x + 10, cup_y + 10)], fill=(22, 22, 28), width=6)

        # Ceramic coffee cup
        draw.rounded_rectangle([cup_x - 32, cup_y - 38, cup_x + 32, cup_y + 22], radius=10, fill=(255, 255, 255), outline=(22, 22, 28), width=5)
        draw.arc([cup_x + 28, cup_y - 24, cup_x + 52, cup_y + 8], 270, 90, fill=(255, 255, 255), width=6)

        # Heart Steam Puff ♡
        heart_y = int(cup_y - 50 - ((f * 2.5) % 180))
        draw.text((cup_x - 14, heart_y), "♡", font=font_tab, fill=(255, 160, 180))

        # Right arm giving GIANT THUMBS UP 👍
        thumb_x, thumb_y = head_cx + 190, head_cy + 10
        draw.line([(head_cx + 140, head_cy + head_r + 30), (thumb_x, thumb_y)], fill=(245, 158, 11), width=24)
        draw.line([(head_cx + 140, head_cy + head_r + 30), (thumb_x, thumb_y)], fill=(22, 22, 28), width=6)

        font_emoji = ImageFont.truetype(FONT_SEGOE, 78)
        draw.text((thumb_x - 24, thumb_y - 70), "👍", font=font_emoji, fill=(255, 215, 0))

        # Radiating Golden Halo & Twinkling Stars
        halo_r = 150 + int(math.sin(f * 0.2) * 15)
        draw.arc([head_cx - halo_r, head_cy - halo_r, head_cx + halo_r, head_cy + halo_r], 0, 360, fill=(246, 211, 101, 180), width=5)

        for s_i in range(8):
            ang = s_i * (math.pi / 4.0) + (f * 0.05)
            sx = int(head_cx + math.cos(ang) * (halo_r + 45))
            sy = int(head_cy + math.sin(ang) * (halo_r + 45))
            draw.text((sx - 10, sy - 10), "✨", font=font_tab, fill=(255, 235, 120))

    # 3. Pristine Anime Subtitles & UI
    draw_subtitles_and_ui(draw, scene)

    return img

# ==========================================
# RENDER SCENE TO MP4
# ==========================================

def render_scene_clip(scene: dict, dur: float) -> Path:
    fps = 30
    total_frames = int(round(dur * fps))
    scene_id = scene["id"]
    out_clip = WORK_DIR / f"pure_clip_{scene_id}.mp4"

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    vw = cv2.VideoWriter(str(out_clip), fourcc, fps, (1080, 1920))

    print(f"    -> Rendering {total_frames} frames ({dur:.2f}s) of 100% pure animation...")

    for f in range(total_frames):
        composed_img = render_pure_animation_frame(scene, f, total_frames)
        bgr = cv2.cvtColor(np.array(composed_img), cv2.COLOR_RGB2BGR)
        vw.write(bgr)

    vw.release()
    return out_clip

# ==========================================
# MAIN PRODUCTION PIPELINE
# ==========================================

def main():
    print("=" * 80)
    print(" 100% PURE ANIMATION STUDIO - CHUYÊN HOẠT HÌNH THUẦN TÚY TRIỆU VIEW")
    print("=" * 80)

    # 1. Foley SFX
    print("\n[1/5] Khởi tạo âm thanh Foley đồng bộ (Pop, Whoosh, Ding, Battery)...")
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
    print("\n[3/5] Hòa âm Master: Giọng đọc + Acoustic Lo-fi BGM + Foley SFX...")
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

    out_path = OUT_DIR / "video_hoat_hinh_100pct_chuyen_nghiep.mp4"

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
    desktop_copy = Path("C:/Users/User/Desktop/video_hoat_hinh_100pct_chuyen_nghiep.mp4")
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
        title="🎬 HOẠT HÌNH 100%: Chuyện Não Mở 100 Tab Lúc 3h Chiều (Chuẩn Webtoon / Anime Douyin)",
        description=(
            "Hoạt hình thuần túy 100% chuyên biệt, không lai tạp video ngoài, không rối mắt! "
            "Căn phòng anime ấm cúng, nhân vật người que mặc áo hoodie vàng mù tạt cực cute, "
            "phụ đề song ngữ điện ảnh thanh thoát ở đáy màn hình. Rất sạch sẽ, sang trọng và thu hút!"
        ),
        app_name="PureAnimationStudio",
        tags=["HoatHinh100", "ChibiAnime", "NaoMo100Tab", "SongNguTrungViet", "DouyinViral"],
        blocking=True
    )
    if ok:
        print(f"✅ {res}")
    else:
        print(f"⚠️ Dispatch notice: {res}")

if __name__ == "__main__":
    main()
