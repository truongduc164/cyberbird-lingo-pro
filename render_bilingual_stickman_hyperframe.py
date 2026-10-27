#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilingual Stickman Hyperframe Studio (Song Ngữ Trung - Việt Đẳng Cấp Hyperframe)
================================================================================
- Chủ đề: Ẩn dụ "Não Mở 100 Tab & Cạn Pin 1% Lúc 3h Chiều"
- Bảng kính Hyperframe Glassmorphism sang trọng, viền vàng óng ánh
- Phụ đề tĩnh 100% (Rock-steady), chuẩn mực sư phạm:
    + Dòng 1: Pinyin có dấu thanh điệu chuẩn
    + Dòng 2: Hán tự (Hanzi) thư pháp YaHei trắng tinh tế
    + Dòng 3: Dịch nghĩa tiếng Việt êm dịu, dễ đọc
    + Dưới đáy: 2 Vocab Chips bóc tách từ vựng trọng tâm
- Nhân vật Người Que (Thầy Que Văn Phòng):
    + Scene 1: Gõ phím bên laptop, 100 tab bay quanh đầu
    + Scene 2: Xẹp lép mệt mỏi, biểu tượng pin đỏ nhấp nháy [🪫 1%]
    + Scene 3: Đeo kính tri thức, cầm que chỉ bảng Hyperframe, bấm tắt tab thừa
    + Scene 4: Uống cà phê ấm, nháy mắt giơ tay LIKE 👍, hào quang vàng
- Giọng đọc bản xứ tiếng Trung chuẩn Bắc Kinh (zh-CN-XiaoxiaoNeural)
- Nhạc nền Lo-fi/Acoustic êm dịu + Âm thanh Foley (Ting, Pop, Whoosh)
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
import pypinyin

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
WORK_DIR = WORKSPACE_ROOT / "temp_bilingual_hyperframe"
WORK_DIR.mkdir(exist_ok=True)
OUT_DIR = WORKSPACE_ROOT / "storage"
OUT_DIR.mkdir(exist_ok=True)

# Font paths
FONT_YAHEI = r"C:\Windows\Fonts\msyh.ttc"
FONT_SEGOE = r"C:\Windows\Fonts\segoeui.ttf"

SCENES = [
    {
        "id": 1,
        "type": "office_100tabs",
        "title": "Scene 1 • Não Mở 100 Tab",
        "cn": "下午三点，脑子开了100个网页。",
        "pinyin": "xià wǔ sān diǎn, nǎo zi kāi le 100 gè wǎng yè.",
        "vi": "Ba giờ chiều, não tôi đang mở 100 tab trình duyệt.",
        "chip1": "脑子 (nǎozi): Bộ não",
        "chip2": "网页 (wǎngyè): Tab trang web",
        "badge": "ẨN DỤ NÃO BỘ • 100 TABS"
    },
    {
        "id": 2,
        "type": "low_battery_1pct",
        "title": "Scene 2 • Pin Chỉ Còn 1%",
        "cn": "身体坐着，电量只剩百分之一。",
        "pinyin": "shēn tǐ zuò zhe, diàn liàng zhǐ shèng bǎi fēn zhī yī.",
        "vi": "Thân thể ngồi đó, nhưng pin chỉ còn đúng 1%.",
        "chip1": "身体 (shēntǐ): Thân thể",
        "chip2": "电量 (diànliàng): Mức pin",
        "badge": "HỘI CHỨNG CẠN PIN • 1%"
    },
    {
        "id": 3,
        "type": "pointer_close_tabs",
        "title": "Scene 3 • Cứ Từ Từ, Tắt Bớt Tab Đi",
        "cn": "慢慢来，先把不需要的网页关掉。",
        "pinyin": "màn man lái, xiān bǎ bù xū yào de wǎng yè guān diào.",
        "vi": "Cứ từ từ thôi, hãy tắt bớt những tab không cần thiết đi.",
        "chip1": "慢慢来 (mànmàn lái): Từ từ thôi",
        "chip2": "关掉 (guāndiào): Tắt đi / Đóng lại",
        "badge": "BÍ QUYẾT TỈNH TÁO • ĐÓNG TAB"
    },
    {
        "id": 4,
        "type": "zen_coffee_thumbsup",
        "title": "Scene 4 • Tha Thứ Cho Bản Thân, Mọi Chuyện Còn Kịp",
        "cn": "放过自己，一切都还来得及。",
        "pinyin": "fàng guò zì jǐ, yí qiè dōu hái lái de jí.",
        "vi": "Tha thứ cho chính mình, mọi chuyện đều còn kịp.",
        "chip1": "放过 (fàngguò): Tha thứ / Bỏ qua",
        "chip2": "来得及 (láidejí): Còn kịp",
        "badge": "CHÂM NGÔN SỐNG • MỌI CHUYỆN CÒN KỊP"
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
    freq = np.linspace(400, 1200, len(t))
    phase = 2 * np.pi * np.cumsum(freq) / sr
    pop = np.sin(phase) * np.exp(-38 * t)
    write_wav(work_dir / "sfx_pop.wav", pop)

    # 2. Whoosh Transition
    t_w = np.linspace(0, 0.22, int(sr * 0.22), False)
    noise = np.random.uniform(-1, 1, len(t_w))
    env_w = np.sin(np.pi * t_w / 0.22) ** 2
    whoosh = noise * env_w * 0.4
    write_wav(work_dir / "sfx_whoosh.wav", whoosh)

    # 3. Crystal Chime / Ding!
    t_d = np.linspace(0, 0.45, int(sr * 0.45), False)
    ding = (np.sin(2 * np.pi * 1480 * t_d) * 0.65 + np.sin(2 * np.pi * 2960 * t_d) * 0.35) * np.exp(-9 * t_d)
    write_wav(work_dir / "sfx_ding.wav", ding)

    # 4. Low Battery Beep (gentle warning)
    t_lb = np.linspace(0, 0.25, int(sr * 0.25), False)
    beep = np.sin(2 * np.pi * 440 * t_lb) * np.exp(-8 * t_lb)
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
            communicate = edge_tts.Communicate(s["cn"], voice, rate="-5%")
            await communicate.save(str(out_f))
        dur = get_audio_duration(out_f)
        durations.append(dur)
        print(f"  • Voice {s['id']}: {dur:.2f}s | {s['title']}")
    return durations

# ==========================================
# DRAWING THE HYPERFRAME GLASSMORPISHM BOARD
# ==========================================

def draw_hyperframe_bilingual_board(draw: ImageDraw.ImageDraw, scene: dict):
    """
    Renders the rock-steady, elegant Glassmorphism board:
    - Pinyin on top (Golden amber)
    - Chinese Hanzi (Pure crisp white)
    - Vietnamese meaning below (Soft cyan-white)
    - 2 Vocab Chips at bottom
    """
    bx0, by0, bx1, by1 = 60, 170, 1020, 890

    # 1. Glass board drop shadow & body
    draw.rounded_rectangle([bx0 + 6, by0 + 8, bx1 + 6, by1 + 8], radius=36, fill=(8, 10, 16))
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=36, fill=(18, 24, 40), outline=(246, 211, 101), width=4)
    # Inner subtle glow border
    draw.rounded_rectangle([bx0 + 8, by0 + 8, bx1 - 8, by1 - 8], radius=30, outline=(60, 80, 120), width=2)

    # 2. Golden corner accent brackets
    for cx, cy in [(bx0 + 16, by0 + 16), (bx1 - 16, by0 + 16), (bx0 + 16, by1 - 16), (bx1 - 16, by1 - 16)]:
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 225, 120))

    # 3. Top Tag Pill
    badge_text = scene.get("badge", "HỌC TIẾNG TRUNG QUA ẨN DỤ")
    draw.rounded_rectangle([200, by0 + 35, 880, by0 + 95], radius=20, fill=(12, 16, 28), outline=(246, 211, 101), width=2)
    font_badge = ImageFont.truetype(FONT_SEGOE, 28)
    draw.text((540, by0 + 65), f"✨ {badge_text}", font=font_badge, fill=(255, 230, 130), anchor="mm")

    # 4. Bilingual Typography (Rock-steady, NO jumping!)
    font_py = ImageFont.truetype(FONT_SEGOE, 34)
    font_cn = ImageFont.truetype(FONT_YAHEI, 60)
    font_vi = ImageFont.truetype(FONT_SEGOE, 34)

    # Pinyin (Gold)
    draw.text((540, by0 + 175), scene["pinyin"], font=font_py, fill=(246, 211, 101), anchor="mm")
    
    # Hanzi (Brilliant White with subtle shadow)
    draw.text((542, by0 + 262), scene["cn"], font=font_cn, fill=(10, 12, 18), anchor="mm")
    draw.text((540, by0 + 260), scene["cn"], font=font_cn, fill=(255, 255, 255), anchor="mm")

    # Divider line
    draw.line([(140, by0 + 350), (940, by0 + 350)], fill=(90, 85, 75), width=2)

    # Vietnamese Translation (Soft Cyan-White)
    draw.text((540, by0 + 420), f'"{scene["vi"]}"', font=font_vi, fill=(226, 232, 240), anchor="mm")

    # 5. Bottom Vocab Chips (2 cards)
    chip_y = by0 + 510
    # Chip 1
    draw.rounded_rectangle([100, chip_y, 520, chip_y + 110], radius=18, fill=(24, 34, 56), outline=(0, 215, 255), width=2)
    font_chip = ImageFont.truetype(FONT_YAHEI, 26)
    draw.text((310, chip_y + 55), scene["chip1"], font=font_chip, fill=(255, 255, 255), anchor="mm")

    # Chip 2
    draw.rounded_rectangle([560, chip_y, 980, chip_y + 110], radius=18, fill=(24, 34, 56), outline=(246, 211, 101), width=2)
    draw.text((770, chip_y + 55), scene["chip2"], font=font_chip, fill=(255, 255, 255), anchor="mm")

# ==========================================
# DRAWING THE STICKMAN HERO & SCENES
# ==========================================

def draw_stickman_face_base(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, f: int, mood: str = "normal"):
    # Hair tuft
    draw.polygon([(cx - 15, cy - r + 5), (cx - 45, cy - r - 40), (cx + 10, cy - r - 20)], fill=(20, 20, 25))
    draw.polygon([(cx + 10, cy - r + 5), (cx + 40, cy - r - 35), (cx + 25, cy - r - 15)], fill=(20, 20, 25))

    # Head circle
    draw.ellipse([cx - r + 6, cy - r + 8, cx + r + 6, cy + r + 8], fill=(12, 14, 20))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255), outline=(20, 20, 25), width=10)

    # DJ Headphones / Teacher Glasses
    if mood == "glasses":
        # Chic round glasses
        draw.ellipse([cx - 65, cy - 35, cx - 15, cy + 15], outline=(246, 211, 101), width=6)
        draw.ellipse([cx + 15, cy - 35, cx + 65, cy + 15], outline=(246, 211, 101), width=6)
        draw.line([(cx - 15, cy - 10), (cx + 15, cy - 10)], fill=(246, 211, 101), width=5)
    else:
        # Headphones around neck
        draw.arc([cx - r - 20, cy - r + 30, cx + r + 20, cy + r + 50], 190, 350, fill=(45, 50, 65), width=12)

    # Eyes
    eye_offset = 40
    eye_y = cy - 10
    is_blink = (f % 55) in [0, 1, 2]

    if is_blink:
        draw.arc([cx - eye_offset - 20, eye_y - 12, cx - eye_offset + 20, eye_y + 12], 180, 360, fill=(20, 20, 20), width=7)
        draw.arc([cx + eye_offset - 20, eye_y - 12, cx + eye_offset + 20, eye_y + 12], 180, 360, fill=(20, 20, 20), width=7)
    elif mood == "exhausted":
        # Slit tired eyes - -
        draw.line([(cx - eye_offset - 22, eye_y), (cx - eye_offset + 22, eye_y)], fill=(20, 20, 20), width=7)
        draw.line([(cx + eye_offset - 22, eye_y), (cx + eye_offset + 22, eye_y)], fill=(20, 20, 20), width=7)
    elif mood == "wink":
        # Left eye open with catchlight, right eye winking
        draw.ellipse([cx - eye_offset - 16, eye_y - 22, cx - eye_offset + 16, eye_y + 22], fill=(20, 20, 20))
        draw.ellipse([cx - eye_offset - 8, eye_y - 16, cx - eye_offset + 4, eye_y - 4], fill=(255, 255, 255))
        draw.arc([cx + eye_offset - 22, eye_y - 10, cx + eye_offset + 22, eye_y + 20], 180, 360, fill=(20, 20, 20), width=8)
    else:
        # Big cartoon eyes with catchlight
        for sign in [-1, 1]:
            ex = cx + sign * eye_offset
            draw.ellipse([ex - 18, eye_y - 24, ex + 18, eye_y + 24], fill=(25, 28, 38))
            draw.ellipse([ex - 10, eye_y - 16, ex - 1, eye_y - 6], fill=(255, 255, 255))

    # Mouth (Phoneme speaking)
    mouth_y = cy + 46
    mouth_phase = (f % 16)
    if mouth_phase < 5:
        draw.line([(cx - 25, mouth_y), (cx + 25, mouth_y)], fill=(20, 20, 20), width=7)
    elif mouth_phase < 10:
        draw.ellipse([cx - 16, mouth_y - 6, cx + 16, mouth_y + 20], fill=(30, 20, 25), outline=(20, 20, 20), width=4)
    else:
        draw.rounded_rectangle([cx - 28, mouth_y - 6, cx + 28, mouth_y + 22], radius=12, fill=(30, 20, 25), outline=(20, 20, 20), width=4)
        draw.ellipse([cx - 12, mouth_y + 8, cx + 12, mouth_y + 20], fill=(255, 110, 130))

def render_bilingual_scene_clip(scene: dict, dur: float) -> Path:
    fps = 30
    total_frames = int(round(dur * fps))
    scene_id = scene["id"]
    stype = scene["type"]
    out_clip = WORK_DIR / f"hyperframe_clip_{scene_id}.mp4"

    if out_clip.exists() and out_clip.stat().st_size > 100000:
        return out_clip

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    vw = cv2.VideoWriter(str(out_clip), fourcc, fps, (1080, 1920))

    font_tab = ImageFont.truetype(FONT_SEGOE, 22)

    for f in range(total_frames):
        img = Image.new("RGB", (1080, 1920), (10, 14, 24))
        draw = ImageDraw.Draw(img)

        # 1. Background radial gradient & floating particles
        for y in range(0, 1920, 6):
            p = y / 1920
            r = int(14 + 10 * p)
            g = int(18 + 14 * p)
            b = int(28 + 20 * p)
            draw.rectangle([0, y, 1080, y + 6], fill=(r, g, b))

        # Floating ambient dust particles
        for i in range(12):
            px = int((i * 123 + f * 1.5) % 1080)
            py = int((i * 187 + f * 2.2) % 1920)
            draw.ellipse([px, py, px + 4, py + 4], fill=(246, 211, 101, 100))

        # 2. Hyperframe Glassmorphism Board (Top half)
        draw_hyperframe_bilingual_board(draw, scene)

        # 3. Lower Stage: Desk & Floor
        desk_y = 1520
        draw.rectangle([0, desk_y, 1080, 1920], fill=(20, 25, 36))
        draw.line([(0, desk_y), (1080, desk_y)], fill=(246, 211, 101), width=4) # golden desk rim

        # 4. Stickman Actions per Scene
        head_cx = 540
        head_r = 130
        
        # ---------------------------------------------
        # SCENE 1: 100 TABS IN THE BRAIN (Office Laptop)
        # ---------------------------------------------
        if stype == "office_100tabs":
            head_cy = 1200 + int(math.sin(f * 0.35) * 6)
            # Body
            draw.line([(head_cx, head_cy + head_r), (head_cx, desk_y + 40)], fill=(20, 20, 25), width=18)
            # Shoulders
            draw.line([(head_cx - 160, head_cy + head_r + 40), (head_cx + 160, head_cy + head_r + 40)], fill=(20, 20, 25), width=14)
            # Arms typing on laptop
            draw.line([(head_cx - 160, head_cy + head_r + 40), (head_cx - 80, desk_y - 20)], fill=(20, 20, 25), width=14)
            draw.line([(head_cx + 160, head_cy + head_r + 40), (head_cx + 80, desk_y - 20)], fill=(20, 20, 25), width=14)

            # Laptop on desk
            draw.polygon([(460, desk_y - 100), (620, desk_y - 100), (660, desk_y), (420, desk_y)], fill=(35, 42, 58))
            draw.polygon([(475, desk_y - 90), (605, desk_y - 90), (645, desk_y - 10), (435, desk_y - 10)], fill=(0, 215, 255)) # glowing screen

            draw_stickman_face_base(draw, head_cx, head_cy, head_r, f, mood="normal")

            # Floating 100 Tabs around head
            tab_data = [
                (100, 1020, "🔥 TAB 99+: Báo cáo!", (255, 60, 80)),
                (700, 980, "💸 Tiền nhà tháng này?", (255, 170, 30)),
                (80, 1220, "🍜 Trưa nay ăn gì?", (0, 190, 255)),
                (720, 1200, "💬 Quên trả lời tin nhắn!", (180, 100, 255)),
                (380, 930, "⚠️ DEADLINE SẮP TỚI!", (255, 90, 140))
            ]
            for idx, (tx, ty, text, col) in enumerate(tab_data):
                float_y = int(ty + math.sin(f * 0.25 + idx * 1.3) * 12)
                draw.rounded_rectangle([tx - 4, float_y - 4, tx + 288, float_y + 68], radius=14, fill=(10, 10, 15))
                draw.rounded_rectangle([tx, float_y, tx + 280, float_y + 60], radius=12, fill=col, outline=(255, 255, 255), width=2)
                draw.text((tx + 18, float_y + 18), text, font=font_tab, fill=(255, 255, 255))

        # ---------------------------------------------
        # SCENE 2: LOW BATTERY 1% (Deflated stickman)
        # ---------------------------------------------
        elif stype == "low_battery_1pct":
            # Stickman slump/melted on desk
            head_cy = 1380 + int(math.sin(f * 0.15) * 4)
            # Body slumping
            draw.line([(head_cx, head_cy + head_r), (head_cx, desk_y + 50)], fill=(20, 20, 25), width=18)
            # Limbs lying flat on desk
            draw.line([(head_cx - 160, desk_y), (head_cx + 160, desk_y)], fill=(20, 20, 25), width=14)

            draw_stickman_face_base(draw, head_cx, head_cy, head_r, f, mood="exhausted")

            # Huge Low Battery Icon above head: [ 🪫 1% ]
            bat_pulse = (math.sin(f * 0.3) + 1.0) / 2.0
            bat_x, bat_y = 440, 1080
            draw.rounded_rectangle([bat_x - 10, bat_y - 8, bat_x + 210, bat_y + 88], radius=18, fill=(15, 15, 20))
            draw.rounded_rectangle([bat_x, bat_y, bat_x + 190, bat_y + 70], radius=14, fill=(30, 20, 24), outline=(255, 50, 70), width=4)
            draw.rectangle([bat_x + 190, bat_y + 20, bat_x + 202, bat_y + 50], fill=(255, 50, 70)) # battery tip
            # 1% red bar
            draw.rounded_rectangle([bat_x + 8, bat_y + 8, bat_x + 35, bat_y + 62], radius=6, fill=(255, 40, 60))
            font_bat = ImageFont.truetype(FONT_SEGOE, 32)
            draw.text((bat_x + 75, bat_y + 18), "1%", font=font_bat, fill=(255, 60, 80))

        # ---------------------------------------------
        # SCENE 3: POINTER STICK - TẮT TAB THỪA
        # ---------------------------------------------
        elif stype == "pointer_close_tabs":
            head_cy = 1200 + int(math.sin(f * 0.3) * 5)
            # Torso
            draw.line([(head_cx, head_cy + head_r), (head_cx, desk_y + 40)], fill=(20, 20, 25), width=18)
            # Left arm holding Wooden Pointer Stick pointing up to the Board!
            draw.line([(head_cx - 160, head_cy + head_r + 40), (head_cx - 240, 1150)], fill=(20, 20, 25), width=14)
            # Pointer stick (Gold/Wood stick pointing up)
            draw.line([(head_cx - 240, 1150), (head_cx - 320, 890)], fill=(246, 211, 101), width=8)
            draw.ellipse([head_cx - 330, 880, head_cx - 310, 900], fill=(255, 255, 255)) # pointer tip glow!

            # Right arm pushing Red Button [ ❌ TẮT TAB ]
            draw.line([(head_cx + 160, head_cy + head_r + 40), (head_cx + 250, desk_y - 40)], fill=(20, 20, 25), width=14)
            # Red close button
            draw.rounded_rectangle([head_cx + 210, desk_y - 65, head_cx + 330, desk_y - 15], radius=14, fill=(255, 50, 70), outline=(255, 255, 255), width=3)
            font_btn = ImageFont.truetype(FONT_SEGOE, 22)
            draw.text((head_cx + 270, desk_y - 40), "❌ TẮT", font=font_btn, fill=(255, 255, 255), anchor="mm")

            draw_stickman_face_base(draw, head_cx, head_cy, head_r, f, mood="glasses")

            # Pop effect (closing tabs disappearing)
            for idx, px in enumerate([180, 850]):
                py = 1050 + idx * 60
                draw.arc([px - 40, py - 40, px + 40, py + 40], 0, 360, fill=(0, 215, 255), width=3)

        # ---------------------------------------------
        # SCENE 4: ZEN COFFEE & THUMBS UP
        # ---------------------------------------------
        elif stype == "zen_coffee_thumbsup":
            head_cy = 1200 + int(math.sin(f * 0.3) * 5)
            draw.line([(head_cx, head_cy + head_r), (head_cx, desk_y + 40)], fill=(20, 20, 25), width=18)
            
            # Left hand holding steaming coffee cup
            draw.line([(head_cx - 160, head_cy + head_r + 40), (head_cx - 220, desk_y - 30)], fill=(20, 20, 25), width=14)
            # Coffee cup
            cup_x, cup_y = head_cx - 220, desk_y - 45
            draw.rounded_rectangle([cup_x - 22, cup_y - 35, cup_x + 22, cup_y + 15], radius=8, fill=(240, 240, 245), outline=(180, 180, 190), width=3)
            draw.arc([cup_x + 18, cup_y - 25, cup_x + 36, cup_y + 5], 270, 90, fill=(200, 200, 210), width=4) # handle
            # Rising steam
            steam_p = (f * 3) % 40
            draw.arc([cup_x - 10, cup_y - 45 - steam_p, cup_x + 10, cup_y - 25 - steam_p], 180, 360, fill=(255, 255, 255), width=3)

            # Right hand: BIG THUMBS UP!
            draw.line([(head_cx + 160, head_cy + head_r + 40), (head_cx + 250, desk_y - 60)], fill=(20, 20, 25), width=14)
            draw.line([(head_cx + 250, desk_y - 60), (head_cx + 280, desk_y - 120)], fill=(20, 20, 25), width=14)
            # Thumbs up glove
            draw.ellipse([head_cx + 255, desk_y - 150, head_cx + 310, desk_y - 105], fill=(255, 255, 255), outline=(20, 20, 25), width=6)
            draw.line([(head_cx + 282, desk_y - 135), (head_cx + 282, desk_y - 185)], fill=(20, 20, 25), width=12) # thumb
            # Sparkles
            sp_x, sp_y = head_cx + 315, desk_y - 190
            draw.line([(sp_x - 15, sp_y), (sp_x + 15, sp_y)], fill=(246, 211, 101), width=4)
            draw.line([(sp_x, sp_y - 15), (sp_x, sp_y + 15)], fill=(246, 211, 101), width=4)

            draw_stickman_face_base(draw, head_cx, head_cy, head_r, f, mood="wink")

        # Convert to OpenCV BGR
        frame_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # Subtle camera breath (1.00 to 1.03)
        p = f / max(1, total_frames - 1)
        zoom = 1.0 + 0.03 * p
        if zoom > 1.005:
            nw = int(1080 * zoom)
            nh = int(1920 * zoom)
            res = cv2.resize(frame_cv, (nw, nh), interpolation=cv2.INTER_LINEAR)
            ox = (nw - 1080) // 2
            oy = (nh - 1920) // 2
            frame_cv = res[oy:oy+1920, ox:ox+1080]

        vw.write(frame_cv)

    vw.release()
    return out_clip

def main():
    print("=" * 75)
    print("🌟 KHỞI TẠO VIDEO SONG NGỮ TRUNG - VIỆT HYPERFRAME + NGƯỜI QUE")
    print("   -> Ẩn dụ: Não Mở 100 Tab & Cạn Pin 1% Lúc 3h Chiều")
    print("   -> Bảng kính Hyperframe Glassmorphism sang trọng, viền vàng")
    print("   -> Phụ đề tĩnh tuyệt đối (Rock-steady): Pinyin + Hán tự + Tiếng Việt")
    print("   -> Nhân vật Thầy Que biểu cảm, gõ thước, bấm nút tắt tab, thumbs up")
    print("=" * 75)

    # 1. Foley SFX
    print("\n[1/5] Khởi tạo âm thanh Foley...")
    create_foley_sfx(WORK_DIR)

    # 2. Native Chinese Voiceovers
    print("\n[2/5] Tạo giọng đọc bản xứ tiếng Trung chuẩn Bắc Kinh...")
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
    total_audio_dur = get_audio_duration(raw_voice)
    print(f"✔ Đã ghép xong giọng đọc ({total_audio_dur:.2f}s)")

    # 3. Mix BGM Lo-Fi + SFX
    bgm_source = WORKSPACE_ROOT / "BilingualStoryStudio" / "audio" / "douyin_bgm.mp3"
    if not bgm_source.exists():
        bgm_source = WORKSPACE_ROOT / "MoneyPrinterTurbo" / "resource" / "songs" / "output000.mp3"
        
    master_audio = WORK_DIR / "master_audio.mp3"
    cmd_audio_mix = [
        FFMPEG, "-y",
        "-i", str(raw_voice),
        "-i", str(bgm_source),
        "-i", str(WORK_DIR / "sfx_pop.wav"),
        "-i", str(WORK_DIR / "sfx_ding.wav"),
        "-filter_complex",
        f"[1:a]volume=0.15,atrim=0:{total_audio_dur},afade=t=out:st={total_audio_dur-2.0}:d=2.0[bgm];"
        f"[2:a]adelay=300|300,volume=0.7[sfx_pop];"
        f"[3:a]adelay={int((total_audio_dur - 3.5)*1000)}|{int((total_audio_dur - 3.5)*1000)},volume=0.8[sfx_ding];"
        f"[0:a][bgm][sfx_pop][sfx_ding]amix=inputs=4:duration=first:dropout_transition=2[aout]",
        "-map", "[aout]",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(master_audio)
    ]
    subprocess.run(cmd_audio_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print("✔ Đã hòa âm Master: Giọng đọc bản xứ + Nhạc nền Lo-fi êm dịu + Foley SFX!")

    # 4. Render Scenes
    print("\n[3/5] Render từng cảnh Người Que & Bảng Hyperframe tĩnh...")
    clips = []
    for s, dur in zip(SCENES, durations):
        print(f"  • Render Scene {s['id']}: {s['title']} ({dur:.2f}s)...")
        c = render_bilingual_scene_clip(s, dur)
        clips.append(c)

    # 5. Concatenate & Finalize MP4
    print("\n[4/5] Ghép nối và hoàn thiện video 9:16...")
    inputs = []
    filter_inputs = ""
    for idx, c in enumerate(clips):
        inputs.extend(["-i", str(c)])
        filter_inputs += f"[{idx}:v]fps=30,setpts=PTS-STARTPTS[v{idx}];"

    concat_filter = f"{filter_inputs}" + "".join([f"[v{i}]" for i in range(len(clips))]) + f"concat=n={len(clips)}:v=1:a=0[vconcat]"

    out_path = OUT_DIR / "video_song_ngu_nguoi_que_hyperframe.mp4"

    cmd_final = [
        FFMPEG, "-y",
        *inputs,
        "-i", str(master_audio),
        "-filter_complex", concat_filter,
        "-map", "[vconcat]",
        "-map", f"{len(clips)}:a",
        "-c:v", "libx264", "-crf", "17", "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(out_path)
    ]
    subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"\n🎉 Xuất video thành công: {out_path.name} ({size_mb:.1f} MB)")

    # Save copy to Desktop
    desktop_copy = Path("C:/Users/User/Desktop/video_song_ngu_nguoi_que_hyperframe.mp4")
    try:
        import shutil
        shutil.copy2(str(out_path), str(desktop_copy))
        print(f"💾 Đã lưu bản sao trên Desktop: {desktop_copy.name}")
    except Exception as e:
        pass

    # 6. Dispatch to Telegram
    print("\n[5/5] Gửi video về Telegram Video Hub...")
    ok, res = dispatch_video(
        video_path=str(out_path),
        title="🌟 Siêu Phẩm Song Ngữ Trung - Việt: Hoạt Hình Người Que + Bảng Hyperframe",
        description="Chủ đề ẩn dụ não mở 100 tab & cạn pin 1% cực hài hước. Bảng kính Hyperframe sang trọng, phụ đề tĩnh 100% chuẩn mực HSK (Pinyin + Hán tự + Tiếng Việt), Thầy Que cầm thước chỉ bảng và bấm tắt tab thừa.",
        app_name="Bilingual-HyperframeStickman",
        tags=["SongNguTrungViet", "Hyperframe", "HoatHinhNguoiQue", "NaoMo100Tab", "HSK3", "TikTokViral"],
        blocking=True
    )
    if ok:
        print(f"✅ {res}")
    else:
        print(f"⚠️ Dispatch notice: {res}")

if __name__ == "__main__":
    main()
