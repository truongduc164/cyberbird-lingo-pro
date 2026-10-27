#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stickman Storytime Animation Generator (Hoạt Hình Người Que Podcast Triệu View)
- Phỏng theo xu hướng viral trên TikTok: DeepSeek kịch bản + Hoạt hình người que Podcast
- Nhân vật người que tối giản, biểu cảm hài hước, cử động miệng & mắt chớp tự động
- Đổi cảnh B-roll nhịp nhàng: Studio Podcast -> Ôm đầu suy nghĩ -> Lướt đt 2h sáng -> Ra ngoài hít thở -> Thumbs up
- Giọng đọc dí dỏm (vi-VN-NamMinhNeural)
- Phụ đề TikTok kiểu hoạt hình (vàng/trắng nổi bật)
- Xuất 1080x1920 @ 30fps & Dispatch trực tiếp về Telegram Bot
"""

import os
import sys
import math
import asyncio
from pathlib import Path
import subprocess
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
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
WORK_DIR = WORKSPACE_ROOT / "temp_stickman_studio"
WORK_DIR.mkdir(exist_ok=True)
OUT_DIR = WORKSPACE_ROOT / "storage"
OUT_DIR.mkdir(exist_ok=True)

SCENES = [
    {
        "id": 1,
        "type": "podcast",
        "title": "Mở đầu • Câu hỏi nghịch lý",
        "voice_text": "Bạn có bao giờ tự hỏi: tại sao cả ngày hôm nay mình chẳng làm gì nặng nhọc, mà người vẫn mệt rã rời không?",
        "sub_line1": "Tại sao chẳng làm gì nặng nhọc...",
        "sub_line2": "Mà người vẫn mệt rã rời không?",
        "keyword": "NGHỊCH LÝ NÃO BỘ"
    },
    {
        "id": 2,
        "type": "overthinking",
        "title": "Chạy ngầm 100 tab",
        "voice_text": "Thủ phạm chính là: não bạn đang chạy ngầm cả trăm tab suy nghĩ cùng một lúc! Nào là lo tương lai, nhớ chuyện cũ, rồi lại băn khoăn trưa nay ăn gì.",
        "sub_line1": "Não bạn đang chạy ngầm 100 tab suy nghĩ!",
        "sub_line2": "Lo tương lai, nhớ chuyện cũ, trưa nay ăn gì...",
        "keyword": "QUÁ TẢI SUY NGHĨ"
    },
    {
        "id": 3,
        "type": "bed_phone",
        "title": "Lướt điện thoại 2h sáng",
        "voice_text": "Cơ thể thì nằm bất động trên giường, nhưng ngón tay thì lướt màn hình vô định suốt 3 tiếng đồng hồ.",
        "sub_line1": "Cơ thể nằm bất động trên giường...",
        "sub_line2": "Nhưng ngón tay lướt màn hình suốt 3 tiếng!",
        "keyword": "DOOM-SCROLLING 02:00 AM"
    },
    {
        "id": 4,
        "type": "outdoor",
        "title": "Giải pháp • Hít thở ngoài trời",
        "voice_text": "Muốn hết mệt à? Thử tắt màn hình, bước ra ngoài hít một hơi thật sâu và cho bộ não nghỉ ngơi 15 phút xem sao!",
        "sub_line1": "Hãy thử tắt màn hình, bước ra ngoài...",
        "sub_line2": "Hít thở thật sâu và nghỉ ngơi 15 phút!",
        "keyword": "GIẢI PHÓNG TÂM TRÍ"
    },
    {
        "id": 5,
        "type": "podcast_outro",
        "title": "Kết luận • Thumbs up & Follow",
        "voice_text": "Nếu thấy đúng với bạn, bấm tim và theo dõi kênh để cùng khám phá những điều thú vị tiếp theo nhé!",
        "sub_line1": "Nếu thấy đúng với bạn...",
        "sub_line2": "Bấm TIM và THEO DÕI kênh ngay nhé!",
        "keyword": "THEO DÕI KÊNH NHÉ!"
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

async def generate_voices():
    voice = "vi-VN-NamMinhNeural"
    durations = []
    for s in SCENES:
        out_f = WORK_DIR / f"voice_{s['id']}.mp3"
        communicate = edge_tts.Communicate(s["voice_text"], voice, rate="+6%", pitch="+1Hz")
        await communicate.save(str(out_f))
        dur = get_audio_duration(out_f)
        durations.append(dur)
        print(f"  • Voice {s['id']}: {dur:.2f}s | {s['title']}")
    return durations

# ==========================================
# PROCEDURAL STICKMAN SCENE DRAWING ENGINES
# ==========================================

def draw_podcast_studio(draw: ImageDraw.ImageDraw, f: int, is_outro: bool = False):
    """Draws Stickman sitting behind a podcast mic at a modern studio desk"""
    # Background wall: Wooden acoustic vertical slats
    wall_color = (235, 230, 222)
    draw.rectangle([0, 0, 1080, 1400], fill=wall_color)
    
    slat_color = (215, 205, 190)
    for x in range(0, 1080, 50):
        draw.line([(x, 0), (x, 1400)], fill=slat_color, width=4)
        
    # Acoustic studio badge on wall
    draw.rectangle([340, 180, 740, 270], fill=(40, 42, 54))
    draw.text((370, 205), "PODCAST VIBE • EP.01", fill=(255, 215, 0))

    # Desk (Foreground lower area)
    desk_color = (60, 50, 45)
    desk_top_y = 1180
    draw.rectangle([0, desk_top_y, 1080, 1920], fill=desk_color)
    draw.line([(0, desk_top_y), (1080, desk_top_y)], fill=(120, 100, 90), width=8)

    # Stickman Body
    head_cx = 540
    bob = int(math.sin(f * 0.3) * 6)
    head_cy = 760 + bob
    head_r = 135

    # Shoulders and Torso
    torso_top_y = head_cy + head_r
    torso_bot_y = desk_top_y + 40
    # Neck & Torso
    draw.line([(head_cx, torso_top_y), (head_cx, torso_bot_y)], fill=(20, 20, 20), width=14)
    # Shoulders
    shoulder_y = torso_top_y + 45
    draw.line([(head_cx - 160, shoulder_y + 20), (head_cx + 160, shoulder_y + 20)], fill=(20, 20, 20), width=12)

    # Arms resting on desk
    if is_outro and (f % 40 < 30):
        # Thumbs up gesture on right hand
        draw.line([(head_cx + 160, shoulder_y + 20), (head_cx + 260, desk_top_y - 60)], fill=(20, 20, 20), width=12)
        draw.line([(head_cx + 260, desk_top_y - 60), (head_cx + 280, desk_top_y - 140)], fill=(20, 20, 20), width=12)
        # Fist + Thumb up
        draw.ellipse([head_cx + 260, desk_top_y - 180, head_cx + 310, desk_top_y - 130], fill=(255, 255, 255), outline=(20, 20, 20), width=8)
        draw.line([(head_cx + 285, desk_top_y - 170), (head_cx + 285, desk_top_y - 215)], fill=(20, 20, 20), width=10) # thumb
        # Left arm on desk
        draw.line([(head_cx - 160, shoulder_y + 20), (head_cx - 240, desk_top_y - 10)], fill=(20, 20, 20), width=12)
        draw.line([(head_cx - 240, desk_top_y - 10), (head_cx - 100, desk_top_y + 10)], fill=(20, 20, 20), width=12)
    else:
        # Both arms relaxed on desk
        draw.line([(head_cx - 160, shoulder_y + 20), (head_cx - 240, desk_top_y - 10)], fill=(20, 20, 20), width=12)
        draw.line([(head_cx - 240, desk_top_y - 10), (head_cx - 80, desk_top_y + 10)], fill=(20, 20, 20), width=12)
        draw.line([(head_cx + 160, shoulder_y + 20), (head_cx + 240, desk_top_y - 10)], fill=(20, 20, 20), width=12)
        draw.line([(head_cx + 240, desk_top_y - 10), (head_cx + 80, desk_top_y + 10)], fill=(20, 20, 20), width=12)

    # Stickman Head (White fill with thick black stroke)
    draw.ellipse([head_cx - head_r, head_cy - head_r, head_cx + head_r, head_cy + head_r],
                 fill=(255, 255, 255), outline=(20, 20, 20), width=12)

    # Ears
    draw.arc([head_cx - head_r - 20, head_cy - 25, head_cx - head_r + 10, head_cy + 25], 90, 270, fill=(20, 20, 20), width=8)
    draw.arc([head_cx + head_r - 10, head_cy - 25, head_cx + head_r + 20, head_cy + 25], 270, 90, fill=(20, 20, 20), width=8)

    # Eyes: Blink every 50 frames for 4 frames
    is_blinking = (f % 55) in [0, 1, 2]
    eye_offset_x = 42
    eye_y = head_cy - 15

    if is_blinking:
        # Closed slit eyes - -
        draw.line([(head_cx - eye_offset_x - 20, eye_y), (head_cx - eye_offset_x + 20, eye_y)], fill=(20, 20, 20), width=8)
        draw.line([(head_cx + eye_offset_x - 20, eye_y), (head_cx + eye_offset_x + 20, eye_y)], fill=(20, 20, 20), width=8)
    elif is_outro:
        # Winking on right eye
        draw.ellipse([head_cx - eye_offset_x - 12, eye_y - 12, head_cx - eye_offset_x + 12, eye_y + 12], fill=(20, 20, 20))
        draw.arc([head_cx + eye_offset_x - 22, eye_y - 10, head_cx + eye_offset_x + 22, eye_y + 20], 180, 360, fill=(20, 20, 20), width=8)
    else:
        # Normal funny deadpan eyes (two solid dots)
        draw.ellipse([head_cx - eye_offset_x - 14, eye_y - 14, head_cx - eye_offset_x + 14, eye_y + 14], fill=(20, 20, 20))
        draw.ellipse([head_cx + eye_offset_x - 14, eye_y - 14, head_cx + eye_offset_x + 14, eye_y + 14], fill=(20, 20, 20))

    # Eyebrows
    draw.line([(head_cx - eye_offset_x - 22, eye_y - 35), (head_cx - eye_offset_x + 22, eye_y - 38)], fill=(20, 20, 20), width=7)
    draw.line([(head_cx + eye_offset_x - 22, eye_y - 38), (head_cx + eye_offset_x + 22, eye_y - 35)], fill=(20, 20, 20), width=7)

    # Mouth: Procedural talking mouth
    mouth_open = int(abs(math.sin(f * 0.75)) * 22)
    mouth_y = head_cy + 52
    if mouth_open > 6:
        # Open talking mouth
        draw.ellipse([head_cx - 28, mouth_y - mouth_open // 2, head_cx + 28, mouth_y + mouth_open // 2],
                     fill=(30, 30, 30), outline=(20, 20, 20), width=5)
    else:
        # Deadpan straight line mouth
        draw.line([(head_cx - 30, mouth_y), (head_cx + 30, mouth_y)], fill=(20, 20, 20), width=8)

    # ------------------------------------
    # Podcast Microphone (Shure SM7B Style)
    # ------------------------------------
    mic_x = 540
    mic_y = 1040
    # Boom arm & stand
    draw.line([(mic_x - 120, desk_top_y + 80), (mic_x, mic_y + 50)], fill=(30, 30, 30), width=18)
    draw.line([(mic_x, mic_y + 50), (mic_x, mic_y)], fill=(50, 50, 50), width=14)
    # Swivel mount
    draw.arc([mic_x - 45, mic_y - 35, mic_x + 45, mic_y + 35], 0, 360, fill=(80, 80, 80), width=8)
    # Mic capsule body
    draw.rounded_rectangle([mic_x - 38, mic_y - 95, mic_x + 38, mic_y + 15], radius=18, fill=(35, 35, 40), outline=(80, 85, 95), width=5)
    # Foam grille
    draw.rounded_rectangle([mic_x - 32, mic_y - 90, mic_x + 32, mic_y - 35], radius=12, fill=(20, 20, 22))
    # Sound wave rings from mic
    wave_r = int((f * 4) % 90)
    if wave_r > 15:
        alpha_color = (255, 180, 0)
        draw.arc([mic_x - 40 - wave_r, mic_y - 65 - wave_r, mic_x + 40 + wave_r, mic_y - 65 + wave_r], 200, 340, fill=alpha_color, width=4)

def draw_overthinking_scene(draw: ImageDraw.ImageDraw, f: int):
    """Draws Stickman holding his head in panic with 100 chaotic thought bubbles"""
    # Background: Stressful slightly dark vignette
    draw.rectangle([0, 0, 1080, 1920], fill=(240, 238, 235))
    
    # Desk and laptop
    desk_y = 1200
    draw.rectangle([0, desk_y, 1080, 1920], fill=(70, 75, 85))
    
    # Laptop screen
    draw.polygon([(460, desk_y - 120), (620, desk_y - 120), (660, desk_y), (420, desk_y)], fill=(40, 45, 55))
    draw.polygon([(475, desk_y - 110), (605, desk_y - 110), (645, desk_y - 10), (435, desk_y - 10)], fill=(0, 200, 255))
    
    # Stickman holding head
    head_cx = 540
    shake = int(math.sin(f * 1.2) * 5)
    head_cy = 820 + shake
    head_r = 130
    
    # Body
    draw.line([(head_cx, head_cy + head_r), (head_cx, desk_y + 30)], fill=(20, 20, 20), width=14)
    # Arms grabbing head in despair
    draw.line([(head_cx - 150, head_cy + head_r + 40), (head_cx - 190, head_cy)], fill=(20, 20, 20), width=12)
    draw.line([(head_cx - 190, head_cy), (head_cx - 120, head_cy - 40)], fill=(20, 20, 20), width=12)
    
    draw.line([(head_cx + 150, head_cy + head_r + 40), (head_cx + 190, head_cy)], fill=(20, 20, 20), width=12)
    draw.line([(head_cx + 190, head_cy), (head_cx + 120, head_cy - 40)], fill=(20, 20, 20), width=12)

    # Head
    draw.ellipse([head_cx - head_r, head_cy - head_r, head_cx + head_r, head_cy + head_r],
                 fill=(255, 255, 255), outline=(20, 20, 20), width=12)

    # Spiral dizzy eyes (stress overload)
    eye_offset = 42
    eye_y = head_cy - 10
    draw.line([(head_cx - eye_offset - 18, eye_y - 18), (head_cx - eye_offset + 18, eye_y + 18)], fill=(20, 20, 20), width=7)
    draw.line([(head_cx - eye_offset - 18, eye_y + 18), (head_cx - eye_offset + 18, eye_y - 18)], fill=(20, 20, 20), width=7)
    
    draw.line([(head_cx + eye_offset - 18, eye_y - 18), (head_cx + eye_offset + 18, eye_y + 18)], fill=(20, 20, 20), width=7)
    draw.line([(head_cx + eye_offset - 18, eye_y + 18), (head_cx + eye_offset + 18, eye_y - 18)], fill=(20, 20, 20), width=7)

    # Wavy stressed mouth
    draw.arc([head_cx - 40, head_cy + 45, head_cx + 40, head_cy + 85], 0, 180, fill=(20, 20, 20), width=8)

    # Sweat drops
    draw.ellipse([head_cx + 140, head_cy - 80, head_cx + 165, head_cy - 45], fill=(0, 180, 255), outline=(0, 120, 200), width=3)
    
    # -----------------------------
    # Chaotic Floating Tabs Bubbles
    # -----------------------------
    tabs = [
        (120, 320, "DEADLINE GẤP!!", (255, 80, 80)),
        (680, 260, "Tiền nhà tháng này?", (255, 170, 0)),
        (100, 520, "Trưa nay ăn gì ta?", (100, 180, 255)),
        (660, 480, "Quên rep tin nhắn!", (180, 120, 255)),
        (380, 160, "Tab 99+: Overthinking...", (255, 100, 150))
    ]
    for x, y, text, col in tabs:
        float_y = y + int(math.sin(f * 0.2 + x) * 12)
        # Tab box
        draw.rounded_rectangle([x, float_y, x + 310, float_y + 80], radius=16, fill=col, outline=(30, 30, 30), width=4)
        draw.text((x + 25, float_y + 25), text, fill=(255, 255, 255))

def draw_bed_phone_scene(draw: ImageDraw.ImageDraw, f: int):
    """Draws Stickman lying in bed in a dark room at 2 AM doom-scrolling on phone"""
    # Dark bedroom background
    draw.rectangle([0, 0, 1080, 1920], fill=(20, 25, 40))
    
    # Clock on wall: 02:00 AM
    draw.ellipse([800, 220, 980, 400], fill=(30, 35, 55), outline=(100, 110, 140), width=6)
    draw.text((830, 290), "02:00", fill=(255, 80, 80))
    draw.text((855, 340), "AM", fill=(180, 190, 210))

    # Bed
    draw.rounded_rectangle([100, 1050, 980, 1750], radius=30, fill=(45, 55, 80), outline=(70, 80, 110), width=8)
    # Pillow
    draw.rounded_rectangle([150, 1100, 450, 1280], radius=25, fill=(75, 85, 115), outline=(100, 115, 145), width=6)
    # Blanket
    draw.rounded_rectangle([320, 1220, 960, 1730], radius=20, fill=(30, 90, 130), outline=(50, 120, 170), width=6)

    # Stickman lying down
    head_cx = 320
    head_cy = 1180
    head_r = 110
    draw.ellipse([head_cx - head_r, head_cy - head_r, head_cx + head_r, head_cy + head_r],
                 fill=(255, 255, 255), outline=(20, 20, 20), width=10)

    # Torso under blanket
    draw.line([(head_cx + head_r, head_cy + 30), (780, head_cy + 150)], fill=(20, 20, 20), width=14)

    # Arms holding glowing phone
    phone_x = 560
    phone_y = 960
    draw.line([(head_cx + 80, head_cy + 80), (phone_x - 30, phone_y + 80)], fill=(20, 20, 20), width=12)
    draw.line([(phone_x - 30, phone_y + 80), (phone_x, phone_y + 20)], fill=(20, 20, 20), width=12)

    # Phone screen glow beam (Polygon)
    glow_poly = [
        (phone_x - 25, phone_y - 60),
        (phone_x + 65, phone_y - 60),
        (head_cx + 80, head_cy - 80),
        (head_cx - 40, head_cy + 40)
    ]
    # Subtle phone glow
    draw.polygon(glow_poly, fill=(30, 80, 120))

    # Glowing smartphone
    draw.rounded_rectangle([phone_x - 35, phone_y - 80, phone_x + 75, phone_y + 70], radius=14, fill=(20, 20, 25), outline=(150, 220, 255), width=5)
    # Screen light
    draw.rounded_rectangle([phone_x - 28, phone_y - 72, phone_x + 68, phone_y + 40], radius=8, fill=(0, 230, 255))
    # TikTok video icon on screen
    draw.polygon([(phone_x + 5, phone_y - 30), (phone_x + 35, phone_y - 15), (phone_x + 5, phone_y)], fill=(255, 255, 255))

    # Stickman wide open eyes staring at screen (zombie scrolling)
    eye_y = head_cy - 10
    draw.ellipse([head_cx + 10, eye_y - 18, head_cx + 46, eye_y + 18], fill=(255, 255, 255), outline=(20, 20, 20), width=5)
    draw.ellipse([head_cx + 25, eye_y - 8, head_cx + 41, eye_y + 8], fill=(0, 210, 255)) # cyan reflection
    
    # Tired mouth
    draw.line([(head_cx + 10, head_cy + 45), (head_cx + 50, head_cy + 42)], fill=(20, 20, 20), width=6)

def draw_outdoor_scene(draw: ImageDraw.ImageDraw, f: int):
    """Draws Stickman walking outside in sunshine, breathing fresh air"""
    # Sky and sun
    draw.rectangle([0, 0, 1080, 1200], fill=(200, 235, 255))
    # Sun
    draw.ellipse([820, 140, 980, 300], fill=(255, 215, 0), outline=(255, 170, 0), width=6)
    for ang in range(0, 360, 45):
        rad = math.radians(ang + f * 1.5)
        sx = 900 + int(math.cos(rad) * 110)
        sy = 220 + int(math.sin(rad) * 110)
        ex = 900 + int(math.cos(rad) * 140)
        ey = 220 + int(math.sin(rad) * 140)
        draw.line([(sx, sy), (ex, ey)], fill=(255, 190, 0), width=6)

    # Green grass ground
    ground_y = 1260
    draw.rectangle([0, ground_y, 1080, 1920], fill=(90, 185, 110))
    draw.line([(0, ground_y), (1080, ground_y)], fill=(60, 150, 80), width=10)

    # Walking Stickman
    walk_cycle = math.sin(f * 0.4)
    head_cx = 450 + int(f * 2) % 180
    head_cy = 780 + int(abs(walk_cycle) * 15)
    head_r = 125

    # Torso
    torso_bottom = head_cy + head_r + 220
    draw.line([(head_cx, head_cy + head_r), (head_cx, torso_bottom)], fill=(20, 20, 20), width=14)

    # Legs walking
    leg_l_angle = walk_cycle * 35
    leg_r_angle = -walk_cycle * 35
    lx = head_cx + int(math.sin(math.radians(leg_l_angle)) * 260)
    ly = torso_bottom + int(math.cos(math.radians(leg_l_angle)) * 260)
    rx = head_cx + int(math.sin(math.radians(leg_r_angle)) * 260)
    ry = torso_bottom + int(math.cos(math.radians(leg_r_angle)) * 260)
    draw.line([(head_cx, torso_bottom), (lx, min(ly, ground_y + 10))], fill=(20, 20, 20), width=12)
    draw.line([(head_cx, torso_bottom), (rx, min(ry, ground_y + 10))], fill=(20, 20, 20), width=12)

    # Arms swinging
    ax1 = head_cx - int(math.sin(math.radians(leg_l_angle)) * 180)
    ay1 = head_cy + head_r + 140
    ax2 = head_cx - int(math.sin(math.radians(leg_r_angle)) * 180)
    ay2 = head_cy + head_r + 140
    draw.line([(head_cx, head_cy + head_r + 40), (ax1, ay1)], fill=(20, 20, 20), width=10)
    draw.line([(head_cx, head_cy + head_r + 40), (ax2, ay2)], fill=(20, 20, 20), width=10)

    # Head smiling
    draw.ellipse([head_cx - head_r, head_cy - head_r, head_cx + head_r, head_cy + head_r],
                 fill=(255, 255, 255), outline=(20, 20, 20), width=12)

    # Eyes: Happy relaxed arches ^ ^
    eye_offset = 38
    eye_y = head_cy - 10
    draw.arc([head_cx - eye_offset - 20, eye_y - 20, head_cx - eye_offset + 20, eye_y + 15], 180, 360, fill=(20, 20, 20), width=8)
    draw.arc([head_cx + eye_offset - 20, eye_y - 20, head_cx + eye_offset + 20, eye_y + 15], 180, 360, fill=(20, 20, 20), width=8)

    # Big happy smile
    draw.arc([head_cx - 38, head_cy + 20, head_cx + 38, head_cy + 75], 0, 180, fill=(20, 20, 20), width=8)

    # Fresh air breeze lines ~ ~
    breeze_x = 180 + (f * 5) % 800
    draw.arc([breeze_x, 520, breeze_x + 140, 560], 180, 360, fill=(255, 255, 255), width=6)
    draw.arc([breeze_x + 100, 580, breeze_x + 260, 620], 180, 360, fill=(255, 255, 255), width=6)

# ==========================================
# RENDER FRAME DISPATCHER
# ==========================================

def render_scene_video(scene: dict, dur: float) -> Path:
    fps = 30
    total_frames = int(round(dur * fps))
    scene_id = scene["id"]
    stype = scene["type"]
    
    out_clip = WORK_DIR / f"stickman_clip_{scene_id}.mp4"
    if out_clip.exists() and out_clip.stat().st_size > 100000:
        return out_clip

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    vw = cv2.VideoWriter(str(out_clip), fourcc, fps, (1080, 1920))

    for f in range(total_frames):
        pil_img = Image.new("RGB", (1080, 1920), (255, 255, 255))
        draw = ImageDraw.Draw(pil_img)

        # Draw corresponding scene
        if stype == "podcast":
            draw_podcast_studio(draw, f, is_outro=False)
        elif stype == "overthinking":
            draw_overthinking_scene(draw, f)
        elif stype == "bed_phone":
            draw_bed_phone_scene(draw, f)
        elif stype == "outdoor":
            draw_outdoor_scene(draw, f)
        elif stype == "podcast_outro":
            draw_podcast_studio(draw, f, is_outro=True)

        # Top Category Keyword Badge
        kw = scene.get("keyword", "")
        if kw:
            badge_bg = (18, 18, 24)
            draw.rounded_rectangle([140, 90, 940, 160], radius=18, fill=badge_bg, outline=(255, 215, 0), width=3)
            draw.text((220, 108), f"💡 {kw}", fill=(255, 235, 120))

        # Convert to OpenCV BGR
        frame_cv = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        # Subtle dynamic camera zoom (1.00 -> 1.04)
        p = f / max(1, total_frames - 1)
        zoom = 1.0 + 0.04 * p
        if zoom > 1.005:
            new_w = int(1080 * zoom)
            new_h = int(1920 * zoom)
            resized = cv2.resize(frame_cv, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            ox = (new_w - 1080) // 2
            oy = (new_h - 1920) // 2
            frame_cv = resized[oy:oy+1920, ox:ox+1080]

        vw.write(frame_cv)

    vw.release()
    return out_clip

def build_ass_subtitles(scenes, durations, out_file: Path):
    """
    Bold, high-retention TikTok style subtitles in the safe zone (MarginV=200).
    Bright yellow/white punchy text with dark outline and rounded boxes.
    """
    header = """[Script Info]
Title: Stickman Viral TikTok Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: MainLine,Segoe UI,56,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,4,2,2,60,60,200,1
Style: SubLine,Segoe UI,44,&H0000E5FF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,3,1,2,60,60,290,1

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
        t0 = fmt_time(current_time)
        t1 = fmt_time(current_time + dur)
        l1 = s["sub_line1"]
        l2 = s["sub_line2"]

        events.append(f"Dialogue: 0,{t0},{t1},SubLine,,0,0,290,,{l1}")
        events.append(f"Dialogue: 0,{t0},{t1},MainLine,,0,0,200,,{l2}")

        current_time += dur

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events))

def main():
    print("=" * 70)
    print("🎨 KHỞI TẠO VIDEO HOẠT HÌNH NGƯỜI QUE (STICKMAN TALK SHOW)")
    print("   -> Lấy cảm hứng từ video TikTok triệu view: DeepSeek + CapCut")
    print("   -> Người que Podcast + B-roll biểu cảm cực bựa & hài hước")
    print("=" * 70)

    # 1. Voiceover
    print("\n[1/4] Tạo giọng kể chuyện dí dỏm bằng Edge-TTS...")
    durations = asyncio.run(generate_voices())
    
    # Merge audios
    voice_files = [WORK_DIR / f"voice_{s['id']}.mp3" for s in SCENES]
    audio_list = WORK_DIR / "audio_list.txt"
    with open(audio_list, "w", encoding="utf-8") as f:
        for vf in voice_files:
            f.write(f"file '{vf.resolve().as_posix()}'\n")

    final_audio = WORK_DIR / "final_audio.mp3"
    subprocess.run([
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", str(audio_list),
        "-c", "copy",
        str(final_audio)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    total_audio_dur = get_audio_duration(final_audio)
    print(f"✔ Đã ghép xong audio ({total_audio_dur:.2f}s)")

    # 2. Render each Stickman scene clip
    print("\n[2/4] Render hoạt hình người que cử động từng cảnh...")
    clips = []
    for s, dur in zip(SCENES, durations):
        print(f"  • Render Scene {s['id']}: {s['title']} ({dur:.2f}s)...")
        c = render_scene_video(s, dur)
        clips.append(c)

    # 3. Concatenate and burn Subtitles
    print("\n[3/4] Ghép nối và ép phụ đề TikTok nổi bật...")
    ass_path = WORK_DIR / "stickman_subtitles.ass"
    build_ass_subtitles(SCENES, durations, ass_path)
    escaped_ass = str(ass_path.resolve()).replace("\\", "/").replace(":", "\\:")

    inputs = []
    filter_inputs = ""
    for idx, c in enumerate(clips):
        inputs.extend(["-i", str(c)])
        filter_inputs += f"[{idx}:v]fps=30,setpts=PTS-STARTPTS[v{idx}];"

    concat_filter = f"{filter_inputs}" + "".join([f"[v{i}]" for i in range(len(clips))]) + f"concat=n={len(clips)}:v=1:a=0[vconcat]"
    full_filter = f"{concat_filter};[vconcat]subtitles='{escaped_ass}'[vfinal]"

    out_path = OUT_DIR / "video_hoat_hinh_nguoi_que_viral.mp4"

    cmd_final = [
        FFMPEG, "-y",
        *inputs,
        "-i", str(final_audio),
        "-filter_complex", full_filter,
        "-map", "[vfinal]",
        "-map", f"{len(clips)}:a",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(out_path)
    ]
    subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"\n🎉 Xuất video người que thành công: {out_path.name} ({size_mb:.1f} MB)")

    # Save copy to Desktop
    desktop_copy = Path("C:/Users/User/Desktop/video_hoat_hinh_nguoi_que_viral.mp4")
    try:
        import shutil
        shutil.copy2(str(out_path), str(desktop_copy))
        print(f"💾 Đã lưu bản sao trên Desktop: {desktop_copy.name}")
    except Exception as e:
        pass

    # 4. Dispatch to Telegram Video Hub
    print("\n[4/4] Gửi video về Telegram Video Hub...")
    ok, res = dispatch_video(
        video_path=str(out_path),
        title="Thử Nghiệm Hoạt Hình Người Que (Stickman Storytime Viral TikTok)",
        description="Lấy cảm hứng từ kịch bản DeepSeek + Hoạt hình người que CapCut: Nhân vật người que Podcast studio cử động miệng, chớp mắt, đổi cảnh B-roll cực hài hước và phụ đề TikTok.",
        app_name="Stickman-Studio",
        tags=["HoatHinhNguoiQue", "StickmanViral", "TikTokStorytime", "DeepSeekIdea", "9x16Shorts"],
        blocking=True
    )
    if ok:
        print(f"✅ {res}")
    else:
        print(f"⚠️ Dispatch notice: {res}")

if __name__ == "__main__":
    main()
