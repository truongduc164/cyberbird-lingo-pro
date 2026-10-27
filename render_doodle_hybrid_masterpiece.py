#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Doodle Hybrid Masterpiece Studio (Người Que Vẽ Tay Tương Tác Nền Video Thật Triệu View)
=======================================================================================
- Nền: 100% Video Đời Thực Thẩm Mỹ Cao (Cozy Cafe, Rainy Window, Steaming Coffee)
- Nhân vật & Chi tiết: Doodle hoạt họa vẽ tay mực trắng (White ink line-art) với bóng đổ mềm
  tương tác trực tiếp trong không gian thế giới thực:
    + Scene 1: Chú người que ngồi trên mặt bàn quán cà phê, tay gõ phím doodle lia lịa,
               100 tab trình duyệt doodle bay lơ lửng quanh đầu.
    + Scene 2: Chú người que xẹp lép mệt mỏi nằm dài trên bậu cửa sổ ngắm mưa rơi,
               cột pin khổng lồ nhấp nháy đỏ [🪫 1%].
    + Scene 3: Chú người que đeo kính trí thức, vẫy đũa thần đóng tab thừa,
               tab nổ tung thành chùm sao lấp lánh ✨.
    + Scene 4: Chú người que ngồi ôm tách cà phê thật, nhấp một ngụm ấm áp,
               nháy mắt giơ ngón tay LIKE 👍 tỏa hào quang vàng rực rỡ.
- Phụ đề Song Ngữ Douyin / TikTok Chuẩn Điện Ảnh (Safe Zone 9:16):
    + Dòng 1: Pinyin chuẩn thanh điệu vàng kem (#FDE68A)
    + Dòng 2: Hán tự thư pháp YaHei trắng tinh tế (#FFFFFF)
    + Dòng 3: Dịch nghĩa Tiếng Việt chữa lành (#E2E8F0)
    + Dưới cùng: 2 Thẻ từ vựng (Vocab Chips) dán góc như Sticky Note
- Âm thanh:
    + Giọng đọc bản xứ tiếng Trung Douyin ấm áp (zh-CN-XiaoxiaoNeural)
    + Nhạc nền Acoustic Guitar Lo-fi êm dịu (MoneyPrinterTurbo songs)
    + Âm thanh Foley: Tiếng gõ phím, bíp pin yếu, pop đóng tab, ding pha lê
- Xuất chuẩn 1080x1920 (9:16) @ 30fps -> Gửi thẳng về Telegram Bot
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
WORK_DIR = WORKSPACE_ROOT / "temp_doodle_hybrid"
WORK_DIR.mkdir(exist_ok=True)
OUT_DIR = WORKSPACE_ROOT / "storage"
OUT_DIR.mkdir(exist_ok=True)
ASSETS_DIR = WORKSPACE_ROOT / "realistic_assets"

FONT_YAHEI = r"C:\Windows\Fonts\msyh.ttc"
FONT_SEGOE = r"C:\Windows\Fonts\segoeui.ttf"

SCENES = [
    {
        "id": 1,
        "type": "doodle_100tabs",
        "video_file": "cozy_laptop.mp4",
        "title": "Scene 1 • Não Mở 100 Tab",
        "cn": "下午三点，脑子开了100个网页。",
        "pinyin": "xià wǔ sān diǎn, nǎo zi kāi le 100 gè wǎng yè.",
        "vi": "Ba giờ chiều, não tôi đang mở 100 tab trình duyệt.",
        "chip1": "脑子 (nǎozi): Bộ não",
        "chip2": "网页 (wǎngyè): Tab web",
        "tag": "☕ CHUYỆN 3H CHIỀU • 下午三点",
        "extra_pad": 0.8
    },
    {
        "id": 2,
        "type": "doodle_lowbattery",
        "video_file": "cozy_window_rain.mp4",
        "title": "Scene 2 • Pin Chỉ Còn 1%",
        "cn": "身体坐着，电量只剩百分之一。",
        "pinyin": "shēn tǐ zuò zhe, diàn liàng zhǐ shèng bǎi fēn zhī yī.",
        "vi": "Thân thể ngồi đó, nhưng pin chỉ còn đúng 1%.",
        "chip1": "身体 (shēntǐ): Thân thể",
        "chip2": "电量 (diànliàng): Mức pin",
        "tag": "🪫 CẠN PIN 1% • 电量不足",
        "extra_pad": 0.7
    },
    {
        "id": 3,
        "type": "doodle_closetabs",
        "video_file": "typing_laptop.mp4",
        "title": "Scene 3 • Cứ Từ Từ, Tắt Bớt Tab Đi",
        "cn": "慢慢来，先把不需要的网页关掉。",
        "pinyin": "màn man lái, xiān bǎ bù xū yào de wǎng yè guān diào.",
        "vi": "Cứ từ từ thôi, hãy tắt bớt những tab không cần thiết đi.",
        "chip1": "慢慢来 (mànmàn lái): Từ từ thôi",
        "chip2": "关掉 (guāndiào): Tắt đi / Đóng lại",
        "tag": "🌿 TĨNH TÂM • 慢慢来",
        "extra_pad": 0.7
    },
    {
        "id": 4,
        "type": "doodle_zen_coffee",
        "video_file": "coffee_steam.mp4",
        "title": "Scene 4 • Tha Thứ Cho Bản Thân, Mọi Chuyện Còn Kịp",
        "cn": "放过自己，一切都还来得及。",
        "pinyin": "fàng guò zì jǐ, yí qiè dōu hái lái de jí.",
        "vi": "Tha thứ cho chính mình, mọi chuyện đều còn kịp.",
        "chip1": "放过 (fàngguò): Tha thứ / Bỏ qua",
        "chip2": "来得及 (láidejí): Còn kịp",
        "tag": "✨ CHỮA LÀNH • 一切都还来得及",
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

    # 1. Pop Sound (punchy bubble pop when closing tabs)
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

    # 4. Low Battery Beep (gentle warning)
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
# VIDEO FRAME SAMPLER & COMPOSITOR
# ==========================================

class VideoLooper:
    def __init__(self, video_path: Path):
        self.cap = cv2.VideoCapture(str(video_path))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 100
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 24.0
        self.orig_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.orig_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.cached_frame = None

    def get_frame(self, frame_idx: int) -> np.ndarray:
        target_f = frame_idx % self.total_frames
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, target_f)
        ret, frame = self.cap.read()
        if ret:
            self.cached_frame = frame
            return frame
        if self.cached_frame is not None:
            return self.cached_frame
        return np.zeros((1080, 1920, 3), dtype=np.uint8)

    def release(self):
        self.cap.release()

def process_background_frame(frame: np.ndarray, frame_idx: int, total_frames: int) -> Image.Image:
    """Scales, center crops to 1080x1920, applies gentle color grade & contrast dimmers."""
    h, w = frame.shape[:2]
    
    # Slight slow camera drift for cinematic feeling
    progress = frame_idx / max(total_frames, 1)
    drift_zoom = 1.0 + 0.04 * math.sin(progress * math.pi)

    scale = max(1080.0 / w, 1920.0 / h) * drift_zoom
    nw = int(round(w * scale))
    nh = int(round(h * scale))
    resized = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_LINEAR)

    x1 = max(0, (nw - 1080) // 2)
    y1 = max(0, (nh - 1920) // 2)
    cropped = resized[y1:y1 + 1920, x1:x1 + 1080]

    if cropped.shape[0] != 1920 or cropped.shape[1] != 1080:
        cropped = cv2.resize(cropped, (1080, 1920))

    # Convert BGR to RGB
    rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
    base_img = Image.fromarray(rgb).convert("RGBA")

    # Dark gradient overlays for readability
    dimmer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d_draw = ImageDraw.Draw(dimmer)

    # Bottom gradient for subtitles (Y: 1250 -> 1920)
    for y in range(1250, 1920, 4):
        p = (y - 1250) / 670.0
        alpha = int(160 * (p ** 1.3))
        d_draw.rectangle([0, y, 1080, y + 4], fill=(10, 14, 22, alpha))

    # Top gradient for top badge (Y: 0 -> 320)
    for y in range(0, 320, 4):
        p = 1.0 - (y / 320.0)
        alpha = int(110 * (p ** 1.2))
        d_draw.rectangle([0, y, 1080, y + 4], fill=(10, 14, 22, alpha))

    return Image.alpha_composite(base_img, dimmer)

# ==========================================
# DRAWING DOODLE ELEMENTS (WHITE INK + SHADOW)
# ==========================================

def draw_doodle_text_ui(doodle_draw: ImageDraw.ImageDraw, scene: dict, f: int):
    """Renders the top badge, subtitles box, and vocab sticky notes."""
    font_badge = ImageFont.truetype(FONT_YAHEI, 28)
    font_pinyin = ImageFont.truetype(FONT_SEGOE, 32)
    font_hanzi = ImageFont.truetype(FONT_YAHEI, 54)
    font_vi = ImageFont.truetype(FONT_SEGOE, 34)
    font_chip = ImageFont.truetype(FONT_YAHEI, 28)

    # 1. Top Badge (Doodle Tape)
    badge_x1, badge_y1 = 60, 110
    badge_x2, badge_y2 = 540, 180
    doodle_draw.rounded_rectangle([badge_x1, badge_y1, badge_x2, badge_y2], radius=22, fill=(18, 22, 32, 220), outline=(255, 255, 255, 240), width=3)
    doodle_draw.text((badge_x1 + 30, badge_y1 + 18), scene["tag"], font=font_badge, fill=(255, 230, 140, 255))

    # 2. Subtitle Box (Frosted Glass Pill in Safe Zone)
    sub_x1, sub_y1 = 55, 1400
    sub_x2, sub_y2 = 1025, 1630
    doodle_draw.rounded_rectangle([sub_x1, sub_y1, sub_x2, sub_y2], radius=28, fill=(12, 16, 26, 225), outline=(246, 211, 101, 210), width=3)

    # Subtle inner gold border
    doodle_draw.rounded_rectangle([sub_x1 + 5, sub_y1 + 5, sub_x2 - 5, sub_y2 - 5], radius=24, outline=(255, 255, 255, 60), width=1)

    # Line 1: Pinyin
    doodle_draw.text((540, 1422), scene["pinyin"], font=font_pinyin, fill=(254, 230, 138), anchor="mt")

    # Line 2: Hanzi (Big, crisp, YaHei)
    doodle_draw.text((540, 1475), scene["cn"], font=font_hanzi, fill=(255, 255, 255), anchor="mt")

    # Line 3: Vietnamese Translation (Gentle healing tone)
    doodle_draw.text((540, 1555), scene["vi"], font=font_vi, fill=(226, 232, 240), anchor="mt")

    # 3. Vocab Sticky Notes (2 bottom chips)
    chip1_box = [80, 1655, 520, 1725]
    chip2_box = [560, 1655, 1000, 1725]

    doodle_draw.rounded_rectangle(chip1_box, radius=18, fill=(22, 28, 40, 235), outline=(255, 255, 255, 190), width=2)
    doodle_draw.text((chip1_box[0] + 25, chip1_box[1] + 18), f"🏷️ {scene['chip1']}", font=font_chip, fill=(255, 255, 255))

    doodle_draw.rounded_rectangle(chip2_box, radius=18, fill=(22, 28, 40, 235), outline=(255, 255, 255, 190), width=2)
    doodle_draw.text((chip2_box[0] + 25, chip2_box[1] + 18), f"🏷️ {scene['chip2']}", font=font_chip, fill=(255, 255, 255))

def render_doodle_hybrid_frame(bg_frame: np.ndarray, scene: dict, f: int, total_frames: int) -> Image.Image:
    """Renders a single high-definition Doodle Hybrid frame combining realistic video + hand-drawn white ink doodle."""
    # 1. Base realistic video background
    base_img = process_background_frame(bg_frame, f, total_frames)

    # 2. Hand-drawn Doodle Layer
    doodle_layer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d_draw = ImageDraw.Draw(doodle_layer)

    stype = scene["type"]
    font_tab = ImageFont.truetype(FONT_SEGOE, 23)

    # Hand-drawn line jitter (boil effect)
    jx = int(math.sin(f * 1.5) * 1.5)
    jy = int(math.cos(f * 1.7) * 1.5)

    # -------------------------------------------------------------
    # SCENE 1: DOODLE LAPTOP + 100 TABS SWIRLING IN CAFE
    # -------------------------------------------------------------
    if stype == "doodle_100tabs":
        desk_y = 1260
        cx = 540 + jx
        cy = 920 + int(math.sin(f * 0.45) * 7) + jy
        r = 100

        # Doodle Laptop on real table
        lap_x1, lap_x2 = 420, 660
        d_draw.polygon([(450, desk_y - 85), (630, desk_y - 85), (lap_x2, desk_y), (lap_x1, desk_y)], fill=(25, 30, 42, 230), outline=(255, 255, 255), width=4)
        d_draw.polygon([(465, desk_y - 75), (615, desk_y - 75), (lap_x2 - 15, desk_y - 10), (lap_x1 + 15, desk_y - 10)], fill=(56, 189, 248, 255))

        # Stickman Body
        d_draw.line([(cx, cy + r), (cx, desk_y - 15)], fill=(255, 255, 255), width=16)

        # Arms typing fast with keyboard sparks
        arm_phase = (f % 6)
        arm_l_y = desk_y - 25 + (6 if arm_phase < 3 else -4)
        arm_r_y = desk_y - 25 + (-4 if arm_phase < 3 else 6)
        d_draw.line([(cx, cy + r + 25), (cx - 130, desk_y - 50)], fill=(255, 255, 255), width=14)
        d_draw.line([(cx - 130, desk_y - 50), (cx - 65, arm_l_y)], fill=(255, 255, 255), width=14)
        d_draw.line([(cx, cy + r + 25), (cx + 130, desk_y - 50)], fill=(255, 255, 255), width=14)
        d_draw.line([(cx + 130, desk_y - 50), (cx + 65, arm_r_y)], fill=(255, 255, 255), width=14)

        # Typing spark particles on desk
        spark_x = (cx - 50) if arm_phase < 3 else (cx + 50)
        d_draw.line([(spark_x, desk_y - 35), (spark_x - 12, desk_y - 50)], fill=(255, 240, 120), width=3)
        d_draw.line([(spark_x, desk_y - 35), (spark_x + 12, desk_y - 50)], fill=(255, 240, 120), width=3)

        # Stickman Head
        d_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 245), outline=(20, 20, 25), width=7)

        # Overwhelmed Eyes
        eye_y = cy - 8
        d_draw.ellipse([cx - 45 - 18, eye_y - 22, cx - 45 + 18, eye_y + 22], fill=(20, 20, 25))
        d_draw.ellipse([cx - 45 - 8, eye_y - 14, cx - 45 + 4, eye_y - 2], fill=(255, 255, 255))
        d_draw.ellipse([cx + 45 - 18, eye_y - 22, cx + 45 + 18, eye_y + 22], fill=(20, 20, 25))
        d_draw.ellipse([cx + 45 - 8, eye_y - 14, cx + 45 + 4, eye_y - 2], fill=(255, 255, 255))

        # Open screaming/overload mouth
        d_draw.ellipse([cx - 24, cy + 38, cx + 24, cy + 78], fill=(25, 20, 25))

        # Brain overload Swirl above head
        swirl_angle = (f * 15) % 360
        d_draw.arc([cx - 60, cy - r - 80, cx + 60, cy - r + 30], swirl_angle, swirl_angle + 270, fill=(255, 220, 80), width=6)

        # Floating 100 Tabs with bright doodle colors
        tab_list = [
            (90, 680, "🔥 TAB 99+: Báo cáo!", (239, 68, 68)),
            (690, 640, "💸 Tiền nhà tháng này?", (245, 158, 11)),
            (80, 920, "🍜 Trưa nay ăn gì?", (14, 165, 233)),
            (710, 900, "💬 Quên trả lời tin nhắn!", (168, 85, 247)),
            (380, 560, "⚠️ DEADLINE SẮP TỚI!", (236, 72, 153))
        ]
        for idx, (tx, ty, text, col) in enumerate(tab_list):
            fy = int(ty + math.sin(f * 0.22 + idx * 1.3) * 14)
            d_draw.rounded_rectangle([tx - 4, fy - 4, tx + 288, fy + 68], radius=16, fill=(15, 18, 25, 235), outline=(255, 255, 255), width=3)
            d_draw.rounded_rectangle([tx, fy, tx + 280, fy + 60], radius=12, fill=col)
            d_draw.text((tx + 16, fy + 17), text, font=font_tab, fill=(255, 255, 255))

    # -------------------------------------------------------------
    # SCENE 2: LOW BATTERY 1% SLUMPED ON WINDOW SILL (RAIN)
    # -------------------------------------------------------------
    elif stype == "doodle_lowbattery":
        bench_y = 1260
        cx = 500 + jx
        cy = 1100 + int(math.sin(f * 0.15) * 4) + jy
        r = 100

        # Stickman lying flat / deflated on surface
        d_draw.line([(cx - 180, bench_y - 20), (cx + 220, bench_y - 20)], fill=(255, 255, 255), width=16)
        # Limbs hanging off
        d_draw.line([(cx - 180, bench_y - 20), (cx - 240, bench_y + 60)], fill=(255, 255, 255), width=14)
        d_draw.line([(cx + 220, bench_y - 20), (cx + 280, bench_y + 60)], fill=(255, 255, 255), width=14)

        # Head resting flat on surface
        d_draw.ellipse([cx - r, cy - r + 30, cx + r, cy + r + 30], fill=(255, 255, 255, 245), outline=(20, 20, 25), width=7)

        # Exhausted slit eyes: - -
        d_draw.line([(cx - 45 - 20, cy + 20), (cx - 45 + 20, cy + 20)], fill=(20, 20, 25), width=8)
        d_draw.line([(cx + 45 - 20, cy + 20), (cx + 45 + 20, cy + 20)], fill=(20, 20, 25), width=8)

        # Drooping mouth
        d_draw.arc([cx - 25, cy + 50, cx + 25, cy + 85], 0, 180, fill=(20, 20, 25), width=6)

        # Giant Glowing Low Battery Icon [ 🪫 1% ]
        bat_cx, bat_cy = 540, 680
        bat_pulse = (math.sin(f * 0.28) + 1.0) / 2.0
        glow_color = (int(255 * (0.8 + 0.2 * bat_pulse)), int(40 * bat_pulse), int(60 * bat_pulse))

        # Battery body
        d_draw.rounded_rectangle([bat_cx - 160, bat_cy - 70, bat_cx + 160, bat_cy + 70], radius=24, fill=(18, 20, 28, 235), outline=(255, 255, 255), width=4)
        # Battery terminal
        d_draw.rounded_rectangle([bat_cx + 160, bat_cy - 25, bat_cx + 182, bat_cy + 25], radius=8, fill=(255, 255, 255))

        # 1% Red indicator bar
        d_draw.rounded_rectangle([bat_cx - 145, bat_cy - 55, bat_cx - 85, bat_cy + 55], radius=10, fill=glow_color)

        # 1% Text
        font_bat = ImageFont.truetype(FONT_SEGOE, 54)
        d_draw.text((bat_cx + 25, bat_cy - 36), "1%", font=font_bat, fill=glow_color)

        # Sparks around battery
        spark_angle = f * 0.2
        for s_idx in range(4):
            sx = int(bat_cx + math.cos(spark_angle + s_idx * 1.57) * 200)
            sy = int(bat_cy + math.sin(spark_angle + s_idx * 1.57) * 95)
            d_draw.text((sx, sy), "⚡", font=font_tab, fill=(255, 230, 80))

        # Zzz sleep bubbles rising
        for z_i in range(3):
            z_y = int(cy - 40 - ((f * 3 + z_i * 60) % 240))
            z_x = int(cx + 80 + math.sin(z_y * 0.05) * 25)
            d_draw.text((z_x, z_y), "💤", font=font_tab, fill=(200, 220, 255))

    # -------------------------------------------------------------
    # SCENE 3: POINTER WAND POPPING TABS (TYPING DESK)
    # -------------------------------------------------------------
    elif stype == "doodle_closetabs":
        desk_y = 1260
        cx = 440 + jx
        cy = 900 + int(math.sin(f * 0.3) * 5) + jy
        r = 100

        # Stickman Body (Standing upright, confident)
        d_draw.line([(cx, cy + r), (cx, desk_y - 15)], fill=(255, 255, 255), width=16)

        # Left arm holding wand pointing UP to the tab!
        wand_tip_x = 750 + int(math.sin(f * 0.2) * 8)
        wand_tip_y = 660 + int(math.cos(f * 0.2) * 8)
        hand_x, hand_y = cx + 160, cy + 40
        d_draw.line([(cx, cy + r + 25), (hand_x, hand_y)], fill=(255, 255, 255), width=14)
        # Golden Wand
        d_draw.line([(hand_x, hand_y), (wand_tip_x, wand_tip_y)], fill=(246, 211, 101), width=9)
        d_draw.ellipse([wand_tip_x - 12, wand_tip_y - 12, wand_tip_x + 12, wand_tip_y + 12], fill=(255, 255, 255))

        # Right arm on hip
        d_draw.line([(cx, cy + r + 25), (cx - 110, cy + r + 80)], fill=(255, 255, 255), width=14)
        d_draw.line([(cx - 110, cy + r + 80), (cx - 40, cy + r + 100)], fill=(255, 255, 255), width=14)

        # Stickman Head
        d_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 245), outline=(20, 20, 25), width=7)

        # Cute Golden Spectacles 👓
        d_draw.ellipse([cx - 55, cy - 25, cx - 10, cy + 20], outline=(246, 211, 101), width=6)
        d_draw.ellipse([cx + 10, cy - 25, cx + 55, cy + 20], outline=(246, 211, 101), width=6)
        d_draw.line([(cx - 10, cy - 2), (cx + 10, cy - 2)], fill=(246, 211, 101), width=5)

        # Eyes behind spectacles
        d_draw.ellipse([cx - 38, cy - 10, cx - 26, cy + 2], fill=(20, 20, 25))
        d_draw.ellipse([cx + 26, cy - 10, cx + 38, cy + 2], fill=(20, 20, 25))

        # Relieved gentle smile
        d_draw.arc([cx - 28, cy + 30, cx + 28, cy + 65], 20, 160, fill=(20, 20, 25), width=6)

        # Popping Tab Explosion at Wand Tip!
        pop_rad = 40 + int((f * 4) % 90)
        d_draw.arc([wand_tip_x - pop_rad, wand_tip_y - pop_rad, wand_tip_x + pop_rad, wand_tip_y + pop_rad], 0, 360, fill=(255, 230, 100, 180), width=4)

        # Burst stars ✨
        for s_idx in range(8):
            ang = s_idx * (math.pi / 4.0) + (f * 0.1)
            dist = pop_rad + 20
            sx = int(wand_tip_x + math.cos(ang) * dist)
            sy = int(wand_tip_y + math.sin(ang) * dist)
            d_draw.text((sx, sy), "✨", font=font_tab, fill=(255, 240, 120))

        # Green success stamp [ ✔ ĐÃ ĐÓNG TAB THỪA ]
        d_draw.rounded_rectangle([wand_tip_x - 30, wand_tip_y - 120, wand_tip_x + 230, wand_tip_y - 65], radius=14, fill=(16, 185, 129, 230), outline=(255, 255, 255), width=3)
        d_draw.text((wand_tip_x - 12, wand_tip_y - 108), "✔ ĐÃ ĐÓNG TAB THỪA", font=font_tab, fill=(255, 255, 255))

    # -------------------------------------------------------------
    # SCENE 4: COFFEE STEAM BLISS & THUMBS UP (HEALING OUTRO)
    # -------------------------------------------------------------
    elif stype == "doodle_zen_coffee":
        desk_y = 1260
        cx = 540 + jx
        cy = 900 + int(math.sin(f * 0.25) * 5) + jy
        r = 100

        # Stickman Body
        d_draw.line([(cx, cy + r), (cx, desk_y - 15)], fill=(255, 255, 255), width=16)

        # Head
        d_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 245), outline=(20, 20, 25), width=7)

        # Rosy Blush Cheeks (Cute Doodle)
        d_draw.ellipse([cx - 65, cy + 20, cx - 35, cy + 42], fill=(255, 150, 165, 200))
        d_draw.ellipse([cx + 35, cy + 20, cx + 65, cy + 42], fill=(255, 150, 165, 200))

        # Winking eye 😉 + open eye with sparkle catchlight
        eye_y = cy - 8
        d_draw.ellipse([cx - 40 - 18, eye_y - 22, cx - 40 + 18, eye_y + 22], fill=(20, 20, 25))
        d_draw.ellipse([cx - 40 - 8, eye_y - 14, cx - 40 + 4, eye_y - 2], fill=(255, 255, 255))
        # Winking eye arc
        d_draw.arc([cx + 20, eye_y - 10, cx + 60, eye_y + 18], 180, 360, fill=(20, 20, 25), width=8)

        # Happy open smile
        d_draw.rounded_rectangle([cx - 26, cy + 38, cx + 26, cy + 68], radius=12, fill=(30, 20, 25))
        d_draw.ellipse([cx - 12, cy + 52, cx + 12, cy + 65], fill=(255, 120, 140))

        # Left arm holding coffee cup
        d_draw.line([(cx, cy + r + 25), (cx - 110, desk_y - 60)], fill=(255, 255, 255), width=14)
        # Doodle coffee cup
        cup_x, cup_y = cx - 110, desk_y - 60
        d_draw.rounded_rectangle([cup_x - 30, cup_y - 35, cup_x + 30, cup_y + 20], radius=8, fill=(255, 255, 255), outline=(20, 20, 25), width=4)
        d_draw.arc([cup_x + 25, cup_y - 22, cup_x + 48, cup_y + 8], 270, 90, fill=(255, 255, 255), width=6)

        # Doodle Heart Steam floating from cup
        heart_y = int(cup_y - 50 - ((f * 2.5) % 180))
        d_draw.text((cup_x - 12, heart_y), "♡", font=font_tab, fill=(255, 160, 180))

        # Right arm giving GIANT THUMBS UP 👍
        thumb_x, thumb_y = cx + 180, cy + 20
        d_draw.line([(cx, cy + r + 25), (thumb_x, thumb_y)], fill=(255, 255, 255), width=14)
        font_emoji = ImageFont.truetype(FONT_SEGOE, 72)
        d_draw.text((thumb_x - 20, thumb_y - 65), "👍", font=font_emoji, fill=(255, 215, 0))

        # Radiating Golden Halo Rings & Sparkles around head
        halo_r = 140 + int(math.sin(f * 0.2) * 15)
        d_draw.arc([cx - halo_r, cy - halo_r, cx + halo_r, cy + halo_r], 0, 360, fill=(246, 211, 101, 160), width=4)

        for s_i in range(8):
            ang = s_i * (math.pi / 4.0) + (f * 0.05)
            sx = int(cx + math.cos(ang) * (halo_r + 40))
            sy = int(cy + math.sin(ang) * (halo_r + 40))
            d_draw.text((sx - 10, sy - 10), "✨", font=font_tab, fill=(255, 235, 120))

    # 3. Draw Subtitles and Sticky UI
    draw_doodle_text_ui(d_draw, scene, f)

    # 4. Composite Doodle Layer onto Base with Soft Drop Shadow
    # Extract alpha mask of the doodle layer
    doodle_alpha = doodle_layer.split()[3]
    shadow_mask = doodle_alpha.filter(ImageFilter.GaussianBlur(radius=5))

    # Black shadow layer
    shadow_layer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    shadow_layer.paste((0, 0, 0, 175), mask=shadow_mask)

    # Offset shadow by +4px X, +5px Y for depth
    offset_shadow = shadow_layer.transform(shadow_layer.size, Image.AFFINE, (1, 0, -4, 0, 1, -5))

    # Combine: Base + Shadow + Doodle
    comp = Image.alpha_composite(base_img, offset_shadow)
    final_frame = Image.alpha_composite(comp, doodle_layer)

    return final_frame

# ==========================================
# RENDER SCENE TO MP4
# ==========================================

def render_scene_clip(scene: dict, dur: float) -> Path:
    fps = 30
    total_frames = int(round(dur * fps))
    scene_id = scene["id"]
    out_clip = WORK_DIR / f"doodle_clip_{scene_id}.mp4"

    video_path = ASSETS_DIR / scene["video_file"]
    looper = VideoLooper(video_path)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    vw = cv2.VideoWriter(str(out_clip), fourcc, fps, (1080, 1920))

    print(f"    -> Rendering {total_frames} frames ({dur:.2f}s) from {scene['video_file']}...")

    for f in range(total_frames):
        bg_frame = looper.get_frame(f)
        composed_img = render_doodle_hybrid_frame(bg_frame, scene, f, total_frames)

        # Convert back to BGR for OpenCV
        bgr = cv2.cvtColor(np.array(composed_img.convert("RGB")), cv2.COLOR_RGB2BGR)
        vw.write(bgr)

    vw.release()
    looper.release()
    return out_clip

# ==========================================
# MAIN PRODUCTION PIPELINE
# ==========================================

def main():
    print("=" * 80)
    print(" DOODLE HYBRID MASTERPIECE STUDIO - SONG NGỮ TRUNG - VIỆT ĐẲNG CẤP TRIỆU VIEW")
    print("=" * 80)

    # 1. Foley SFX
    print("\n[1/5] Khởi tạo hệ thống âm thanh Foley (Pop, Whoosh, Ding, Battery)...")
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

    # Calculate exact delays for SFX based on scene durations
    # Scene 1 start: 0s -> sfx_whoosh at 0.3s
    # Scene 2 start: durations[0] -> sfx_battery at durations[0] + 0.8s
    # Scene 3 start: durations[0] + durations[1] -> sfx_pop at durations[0] + durations[1] + 1.0s
    # Scene 4 start: sum(durations[:3]) -> sfx_ding at sum(durations[:3]) + 1.8s
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

    # 4. Render All Doodle Scenes
    print("\n[4/5] Render 4 cảnh Doodle Hybrid trên nền video thật...")
    clips = []
    for s, dur in zip(SCENES, durations):
        print(f"  • Render {s['title']} ({dur:.2f}s)...")
        c = render_scene_clip(s, dur)
        clips.append(c)

    # 5. Concatenate & Finalize Video
    print("\n[5/5] Ghép nối và hoàn thiện video 9:16 chuẩn TikTok / Douyin...")
    inputs = []
    filter_inputs = ""
    for idx, c in enumerate(clips):
        inputs.extend(["-i", str(c)])
        filter_inputs += f"[{idx}:v]fps=30,setpts=PTS-STARTPTS[v{idx}];"

    concat_filter = f"{filter_inputs}" + "".join([f"[v{i}]" for i in range(len(clips))]) + f"concat=n={len(clips)}:v=1:a=0[vconcat]"

    out_path = OUT_DIR / "video_doodle_hybrid_song_ngu_trieu_view.mp4"

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
    desktop_copy = Path("C:/Users/User/Desktop/video_doodle_hybrid_song_ngu_trieu_view.mp4")
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
        title="✨ DOODLE HYBRID: Chuyện Não Mở 100 Tab Lúc 3h Chiều (Chuẩn Triệu View TikTok / Douyin)",
        description=(
            "Phong cách Doodle Hybrid kết hợp 100% video quay thực tế cực chill (quán cafe, mưa rơi cửa kính, cốc cafe bốc khói) "
            "với hoạt họa người que vẽ tay mực trắng tương tác sống động! "
            "Phụ đề song ngữ Douyin điện ảnh (Pinyin + Hán tự YaHei + Tiếng Việt) + 2 thẻ từ vựng Sticky Note HSK trọng tâm."
        ),
        app_name="DoodleHybridStudio",
        tags=["DoodleHybrid", "SongNguTrungViet", "TikTokTriệuView", "NaoMo100Tab", "ChuaLanhDouyin"],
        blocking=True
    )
    if ok:
        print(f"✅ {res}")
    else:
        print(f"⚠️ Dispatch notice: {res}")

if __name__ == "__main__":
    main()
