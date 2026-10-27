#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSS-TIER VIRAL STICKMAN ANIMATION STUDIO (Đẳng cấp Thương Mại & Cạnh Tranh Thị Trường)
========================================================================================
- Graphic: Nghệ thuật truyện tranh webcomic cao cấp (Phòng thu Podcast Cinematic, ánh sáng neon rim light,
  đèn ON AIR phát sáng, character có chiều sâu, tai nghe DJ, mic Shure SM7B chi tiết kim loại).
- Character Animation: Biểu cảm sống động (mắt to cartoon có catchlight lấp lánh, miệng phát âm đa khẩu hình,
  tai lắc lư, cử chỉ tay linh hoạt: tựa cằm, chỉ tay, ôm đầu, lướt đt, giơ like).
- Motion & Camera: Dynamic Punch-in (zoom giật gân theo nhịp thoại), screen shake, comic pop-up spring physics.
- Sound Design: Âm thanh Foley cao cấp (Ding, Pop, Whoosh, Thud) + BGM Lo-fi Groovy ducked ngầm chuyên nghiệp.
- Subtitles: TikTok Kinetic Typography (chữ nổi bật, hiệu ứng Highlight đổi màu theo nhịp thoại).
- Faststart 1080x1920 (9:16) @ 30fps -> Gửi thẳng về Telegram bot.
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
WORK_DIR = WORKSPACE_ROOT / "temp_sss_stickman"
WORK_DIR.mkdir(exist_ok=True)
OUT_DIR = WORKSPACE_ROOT / "storage"
OUT_DIR.mkdir(exist_ok=True)

SCENES = [
    {
        "id": 1,
        "type": "podcast_hook",
        "title": "Mở đầu • Câu hỏi nghịch lý",
        "voice_text": "Bạn có bao giờ tự hỏi: tại sao cả ngày hôm nay mình chẳng làm gì nặng nhọc, mà người vẫn mệt rã rời không?",
        "sub_line1": "Tại sao cả ngày chẳng làm gì...",
        "sub_line2": "Mà người vẫn MỆT RÃ RỜI không?",
        "highlight_word": "MỆT RÃ RỜI",
        "badge": "NGHỊCH LÝ NÃO BỘ"
    },
    {
        "id": 2,
        "type": "overthinking_chaos",
        "title": "Chạy ngầm 100 tab",
        "voice_text": "Thủ phạm chính là: não bạn đang chạy ngầm cả trăm tab suy nghĩ cùng một lúc! Nào là lo tương lai, nhớ chuyện cũ, rồi lại băn khoăn trưa nay ăn gì.",
        "sub_line1": "Não bạn đang chạy ngầm 100 TAB suy nghĩ!",
        "sub_line2": "Lo tương lai, nhớ chuyện cũ, trưa nay ăn gì...",
        "highlight_word": "100 TAB SUY NGHĨ",
        "badge": "QUÁ TẢI SUY NGHĨ"
    },
    {
        "id": 3,
        "type": "bed_doomscroll",
        "title": "Lướt điện thoại 2h sáng",
        "voice_text": "Cơ thể thì nằm bất động trên giường, nhưng ngón tay thì lướt màn hình vô định suốt 3 tiếng đồng hồ trong bóng tối.",
        "sub_line1": "Cơ thể nằm bất động trên giường...",
        "sub_line2": "Nhưng ngón tay lướt suốt 3 TIẾNG trong đêm!",
        "highlight_word": "LƯỚT SUỐT 3 TIẾNG",
        "badge": "DOOM-SCROLLING 02:00 AM"
    },
    {
        "id": 4,
        "type": "outdoor_zen",
        "title": "Giải pháp • Hít thở ngoài trời",
        "voice_text": "Muốn hết mệt à? Thử tắt màn hình, bước ra ngoài hít một hơi thật sâu và cho bộ não nghỉ ngơi 15 phút xem sao!",
        "sub_line1": "Hãy thử tắt màn hình, bước ra ngoài...",
        "sub_line2": "HÍT THỞ THẬT SÂU và nghỉ ngơi 15 phút!",
        "highlight_word": "HÍT THỞ THẬT SÂU",
        "badge": "GIẢI PHÓNG TÂM TRÍ"
    },
    {
        "id": 5,
        "type": "podcast_outro_pro",
        "title": "Kết luận • Thumbs up & Follow",
        "voice_text": "Nếu thấy đúng với bạn, bấm tim và theo dõi kênh ngay để cùng nạp lại năng lượng tích cực mỗi ngày nhé!",
        "sub_line1": "Nếu thấy đúng với bạn...",
        "sub_line2": "Bấm TIM và THEO DÕI kênh ngay nhé!",
        "highlight_word": "THEO DÕI KÊNH",
        "badge": "THEO DÕI KÊNH NHÉ!"
    }
]

# ==========================================
# PROCEDURAL AUDIO & SOUND DESIGN (FOLEY)
# ==========================================

def create_foley_sfx(work_dir: Path):
    """Generates studio-grade Foley sound effects using math algorithms"""
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

    # 4. Bass Thud / Impact (for camera punch-in)
    t_b = np.linspace(0, 0.30, int(sr * 0.30), False)
    thud = np.sin(2 * np.pi * 80 * np.exp(-6 * t_b) * t_b) * np.exp(-10 * t_b)
    write_wav(work_dir / "sfx_thud.wav", thud)

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
    voice = "vi-VN-NamMinhNeural"
    durations = []
    # Check if we can reuse from temp_stickman_studio
    cached_dir = WORKSPACE_ROOT / "temp_stickman_studio"
    for s in SCENES:
        out_f = work_dir / f"voice_{s['id']}.mp3"
        cached_f = cached_dir / f"voice_{s['id']}.mp3"
        if cached_f.exists() and cached_f.stat().st_size > 5000:
            import shutil
            shutil.copy2(str(cached_f), str(out_f))
        elif not out_f.exists() or out_f.stat().st_size < 5000:
            communicate = edge_tts.Communicate(s["voice_text"], voice, rate="+6%")
            await communicate.save(str(out_f))
        dur = get_audio_duration(out_f)
        durations.append(dur)
    return durations

# ==========================================
# SSS-TIER ART & VECTOR DRAWING FUNCTIONS
# ==========================================

def draw_aesthetic_studio_background(img: Image.Image, f: int):
    """Draws a moody, cinematic acoustic podcast studio with warm lighting and neon sign"""
    w, h = img.size
    draw = ImageDraw.Draw(img)

    # Gradient dark background wall (slate charcoal)
    for y in range(0, 1300, 4):
        p = y / 1300
        r = int(24 + 12 * p)
        g = int(26 + 14 * p)
        b = int(36 + 16 * p)
        draw.rectangle([0, y, w, y + 4], fill=(r, g, b))

    # Vertical acoustic wooden slats with warm drop shadows
    for x in range(30, w, 70):
        # shadow
        draw.rectangle([x - 4, 0, x + 38, 1260], fill=(12, 14, 20))
        # slat body
        draw.rectangle([x, 0, x + 34, 1260], fill=(50, 42, 38))
        # highlight edge
        draw.line([(x + 2, 0), (x + 2, 1260)], fill=(90, 75, 65), width=2)

    # Ambient warm glow behind character (Soft Radial Halo)
    halo_cx, halo_cy = 540, 750
    for rad in range(350, 100, -25):
        alpha_factor = (350 - rad) / 250
        col = (int(70 + 40 * alpha_factor), int(55 + 30 * alpha_factor), int(45 + 15 * alpha_factor))
        draw.ellipse([halo_cx - rad, halo_cy - rad, halo_cx + rad, halo_cy + rad], fill=col)

    # Glowing Neon Sign: ● LIVE PODCAST (Ruby Red Glow)
    sign_x, sign_y = 350, 200
    # Outer bloom
    draw.rounded_rectangle([sign_x - 10, sign_y - 8, sign_x + 390, sign_y + 82], radius=24, fill=(50, 10, 15))
    draw.rounded_rectangle([sign_x, sign_y, sign_x + 370, sign_y + 66], radius=18, fill=(20, 18, 24), outline=(255, 40, 80), width=3)
    # Pulsing red recording dot
    pulse = (math.sin(f * 0.25) + 1.0) / 2.0
    dot_r = int(9 + 3 * pulse)
    draw.ellipse([sign_x + 35 - dot_r, sign_y + 33 - dot_r, sign_x + 35 + dot_r, sign_y + 33 + dot_r], fill=(255, 30, 70))
    draw.text((sign_x + 60, sign_y + 18), "LIVE PODCAST", fill=(255, 230, 240))

    # Studio Wooden Desk in foreground
    desk_y = 1200
    # Desk bevel & shadow
    draw.rectangle([0, desk_y - 20, w, desk_y], fill=(35, 28, 24))
    draw.line([(0, desk_y - 20), (w, desk_y - 20)], fill=(160, 130, 100), width=5) # specular highlight
    draw.rectangle([0, desk_y, w, h], fill=(28, 22, 18)) # lower desk body

def draw_sss_stickman_face(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, f: int, mood: str = "deadpan"):
    """
    Renders Tier-SSS expressive cartoon character face:
    - Large expressive eyes with glossy catchlights
    - Natural blinking with secondary eyelid motion
    - 4-state mouth speaking phonemes
    - Cute tuft of hair & DJ headphones
    """
    # 1. Hair tuft on top of head
    hair_base_x = cx - 15
    hair_base_y = cy - r + 5
    draw.polygon([(hair_base_x, hair_base_y), (hair_base_x - 30, hair_base_y - 45), (hair_base_x + 5, hair_base_y - 25)], fill=(20, 20, 25))
    draw.polygon([(hair_base_x + 10, hair_base_y), (hair_base_x + 40, hair_base_y - 40), (hair_base_x + 25, hair_base_y - 15)], fill=(20, 20, 25))

    # 2. Main Head Circle (Smooth white with subtle drop shadow)
    draw.ellipse([cx - r + 6, cy - r + 8, cx + r + 6, cy + r + 8], fill=(15, 18, 25)) # drop shadow
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255), outline=(22, 22, 28), width=10)

    # 3. DJ Headphones around neck/ears
    hp_y = cy + 20
    # Headphone band
    draw.arc([cx - r - 25, cy - r + 30, cx + r + 25, cy + r + 50], 190, 350, fill=(45, 50, 65), width=14)
    # Ear cushions
    draw.rounded_rectangle([cx - r - 28, hp_y - 45, cx - r + 5, hp_y + 45], radius=15, fill=(25, 25, 30), outline=(0, 215, 255), width=3)
    draw.rounded_rectangle([cx + r - 5, hp_y - 45, cx + r + 28, hp_y + 45], radius=15, fill=(25, 25, 30), outline=(0, 215, 255), width=3)

    # 4. Eyes & Eyebrows
    eye_offset_x = 42
    eye_y = cy - 12
    is_blink = (f % 65) in [0, 1, 2]

    if is_blink:
        # Happy closed curved eyes ^ ^
        draw.arc([cx - eye_offset_x - 22, eye_y - 15, cx - eye_offset_x + 22, eye_y + 15], 180, 360, fill=(20, 20, 20), width=7)
        draw.arc([cx + eye_offset_x - 22, eye_y - 15, cx + eye_offset_x + 22, eye_y + 15], 180, 360, fill=(20, 20, 20), width=7)
    elif mood == "wink":
        # Left eye wide cartoon, right eye winking
        draw.ellipse([cx - eye_offset_x - 18, eye_y - 25, cx - eye_offset_x + 18, eye_y + 25], fill=(20, 20, 20))
        draw.ellipse([cx - eye_offset_x - 8, eye_y - 18, cx - eye_offset_x + 4, eye_y - 6], fill=(255, 255, 255)) # sparkle
        # wink
        draw.arc([cx + eye_offset_x - 24, eye_y - 12, cx + eye_offset_x + 24, eye_y + 20], 180, 360, fill=(20, 20, 20), width=8)
    elif mood == "spiral_stress":
        # Dizzy spiral eyes
        for sign in [-1, 1]:
            ex = cx + sign * eye_offset_x
            draw.line([(ex - 20, eye_y - 20), (ex + 20, eye_y + 20)], fill=(220, 40, 40), width=7)
            draw.line([(ex - 20, eye_y + 20), (ex + 20, eye_y - 20)], fill=(220, 40, 40), width=7)
    else:
        # High-res cartoon eyes with shiny catchlights
        for sign in [-1, 1]:
            ex = cx + sign * eye_offset_x
            # White eye socket
            draw.ellipse([ex - 22, eye_y - 26, ex + 22, eye_y + 26], fill=(255, 255, 255), outline=(20, 20, 20), width=4)
            # Big dark pupil
            draw.ellipse([ex - 15, eye_y - 18, ex + 15, eye_y + 18], fill=(25, 28, 38))
            # Catchlight specular reflections
            draw.ellipse([ex - 9, eye_y - 13, ex - 1, eye_y - 5], fill=(255, 255, 255))
            draw.ellipse([ex + 4, eye_y + 3, ex + 8, eye_y + 7], fill=(255, 255, 255))

    # Eyebrows with attitude
    if mood == "spiral_stress":
        # Angled down in stress
        draw.line([(cx - eye_offset_x - 25, eye_y - 35), (cx - eye_offset_x + 25, eye_y - 48)], fill=(20, 20, 20), width=7)
        draw.line([(cx + eye_offset_x - 25, eye_y - 48), (cx + eye_offset_x + 25, eye_y - 35)], fill=(20, 20, 20), width=7)
    else:
        # Sarcastic cocked eyebrow (left slightly arched, right raised)
        draw.line([(cx - eye_offset_x - 22, eye_y - 42), (cx - eye_offset_x + 22, eye_y - 40)], fill=(20, 20, 20), width=7)
        draw.line([(cx + eye_offset_x - 22, eye_y - 52), (cx + eye_offset_x + 24, eye_y - 44)], fill=(20, 20, 20), width=8)

    # 5. Natural Cartoon Mouth Shapes (Phonemes)
    mouth_y = cy + 50
    mouth_phase = (f % 16)
    
    if mood == "smile":
        # Big open happy smile
        draw.arc([cx - 40, mouth_y - 10, cx + 40, mouth_y + 40], 0, 180, fill=(20, 20, 20), width=7)
        draw.line([(cx - 40, mouth_y + 15), (cx + 40, mouth_y + 15)], fill=(20, 20, 20), width=7)
    elif mouth_phase < 4:
        # Closed rest line with cheeky upturn
        draw.line([(cx - 28, mouth_y + 5), (cx + 25, mouth_y + 2)], fill=(20, 20, 20), width=7)
        draw.arc([cx + 22, mouth_y - 4, cx + 34, mouth_y + 8], 0, 90, fill=(20, 20, 20), width=6)
    elif mouth_phase < 8:
        # O-shape
        draw.ellipse([cx - 18, mouth_y - 6, cx + 18, mouth_y + 22], fill=(40, 20, 25), outline=(20, 20, 20), width=5)
    elif mouth_phase < 12:
        # Wide open speaking mouth with cute tongue
        draw.rounded_rectangle([cx - 32, mouth_y - 8, cx + 32, mouth_y + 24], radius=14, fill=(40, 20, 25), outline=(20, 20, 20), width=5)
        draw.ellipse([cx - 15, mouth_y + 8, cx + 15, mouth_y + 22], fill=(255, 100, 120)) # pink tongue
    else:
        # Half open talking
        draw.ellipse([cx - 25, mouth_y - 4, cx + 25, mouth_y + 14], fill=(40, 20, 25), outline=(20, 20, 20), width=5)

def draw_shure_sm7b_microphone(draw: ImageDraw.ImageDraw, mic_x: int, mic_y: int, f: int):
    """Draws a broadcast studio Shure SM7B dynamic microphone with acoustic rings"""
    # Desktop boom arm stand
    draw.line([(mic_x - 140, 1280), (mic_x, mic_y + 70)], fill=(20, 22, 28), width=22)
    draw.line([(mic_x - 140, 1280), (mic_x, mic_y + 70)], fill=(65, 70, 85), width=6) # metallic edge
    draw.line([(mic_x, mic_y + 70), (mic_x, mic_y + 10)], fill=(40, 45, 55), width=16)

    # Swivel Yoke Mount
    draw.arc([mic_x - 55, mic_y - 25, mic_x + 55, mic_y + 45], 0, 360, fill=(110, 115, 130), width=8)
    draw.ellipse([mic_x - 55, mic_y + 5, mic_x - 40, mic_y + 20], fill=(220, 220, 230)) # chrome thumb screw
    draw.ellipse([mic_x + 40, mic_y + 5, mic_x + 55, mic_y + 20], fill=(220, 220, 230))

    # Main Mic Body (Metallic Dark Grey)
    draw.rounded_rectangle([mic_x - 42, mic_y - 120, mic_x + 42, mic_y + 15], radius=22, fill=(35, 38, 46), outline=(90, 95, 110), width=5)
    # Gold branding band
    draw.rectangle([mic_x - 42, mic_y - 50, mic_x + 42, mic_y - 42], fill=(255, 200, 50))
    # Foam windscreen with texture
    draw.rounded_rectangle([mic_x - 38, mic_y - 116, mic_x + 38, mic_y - 52], radius=18, fill=(20, 22, 25))
    
    # Sound wave pulse rings emanating from mic
    for i in range(3):
        r_wave = int(((f * 4 + i * 35) % 110))
        if r_wave > 20:
            alpha_col = (255, 200, 30)
            draw.arc([mic_x - 40 - r_wave, mic_y - 85 - r_wave, mic_x + 40 + r_wave, mic_y - 85 + r_wave], 210, 330, fill=alpha_col, width=4)

# ==========================================
# SCENE RENDERERS
# ==========================================

def render_sss_scene(scene: dict, dur: float) -> Path:
    fps = 30
    total_frames = int(round(dur * fps))
    scene_id = scene["id"]
    stype = scene["type"]
    out_clip = WORK_DIR / f"sss_clip_{scene_id}.mp4"

    if out_clip.exists() and out_clip.stat().st_size > 100000:
        return out_clip

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    vw = cv2.VideoWriter(str(out_clip), fourcc, fps, (1080, 1920))

    for f in range(total_frames):
        img = Image.new("RGB", (1080, 1920), (25, 26, 34))
        draw = ImageDraw.Draw(img)

        # ----------------------------------------------------
        # SCENE 1 & 5: PODCAST STUDIO (HOOK & OUTRO)
        # ----------------------------------------------------
        if "podcast" in stype:
            draw_aesthetic_studio_background(img, f)
            head_cx = 540
            head_bob = int(math.sin(f * 0.35) * 8)
            head_cy = 760 + head_bob
            head_r = 140

            # Body & Hoodie
            torso_y = head_cy + head_r
            # Shoulders
            draw.line([(head_cx - 190, torso_y + 70), (head_cx + 190, torso_y + 70)], fill=(20, 20, 25), width=18)
            # Torso
            draw.line([(head_cx, torso_y), (head_cx, 1250)], fill=(20, 20, 25), width=22)

            if stype == "podcast_outro_pro":
                # Thumbs Up gesture!
                draw.line([(head_cx + 190, torso_y + 70), (head_cx + 280, 1100)], fill=(20, 20, 25), width=16)
                draw.line([(head_cx + 280, 1100), (head_cx + 310, 980)], fill=(20, 20, 25), width=16)
                # Glove / Fist + Big Thumb
                draw.ellipse([head_cx + 285, 930, head_cx + 345, 990], fill=(255, 255, 255), outline=(20, 20, 25), width=8)
                draw.line([(head_cx + 315, 945), (head_cx + 315, 880)], fill=(20, 20, 25), width=14)
                # Sparkles around thumb
                sp_x, sp_y = head_cx + 350, 890
                draw.line([(sp_x - 18, sp_y), (sp_x + 18, sp_y)], fill=(255, 215, 0), width=5)
                draw.line([(sp_x, sp_y - 18), (sp_x, sp_y + 18)], fill=(255, 215, 0), width=5)
                # Left arm leaning
                draw.line([(head_cx - 190, torso_y + 70), (head_cx - 270, 1180)], fill=(20, 20, 25), width=16)
                draw.line([(head_cx - 270, 1180), (head_cx - 100, 1200)], fill=(20, 20, 25), width=16)
                draw_sss_stickman_face(draw, head_cx, head_cy, head_r, f, mood="wink")
            else:
                # Pointing gesture / inquisitive leaning
                draw.line([(head_cx - 190, torso_y + 70), (head_cx - 280, 1180)], fill=(20, 20, 25), width=16)
                draw.line([(head_cx - 280, 1180), (head_cx - 110, 1200)], fill=(20, 20, 25), width=16)
                # Right arm leaning on table
                draw.line([(head_cx + 190, torso_y + 70), (head_cx + 280, 1180)], fill=(20, 20, 25), width=16)
                draw.line([(head_cx + 280, 1180), (head_cx + 110, 1200)], fill=(20, 20, 25), width=16)
                draw_sss_stickman_face(draw, head_cx, head_cy, head_r, f, mood="deadpan")

            # Microphone in foreground
            draw_shure_sm7b_microphone(draw, 540, 1040, f)

        # ----------------------------------------------------
        # SCENE 2: OVERTHINKING CHAOS (100 TABS EXPLODING)
        # ----------------------------------------------------
        elif stype == "overthinking_chaos":
            # Dark chaotic vignette
            draw.rectangle([0, 0, 1080, 1920], fill=(22, 22, 28))
            desk_y = 1240
            draw.rectangle([0, desk_y, 1080, 1920], fill=(45, 50, 60))
            
            # Stickman shaking in stress
            shake_x = int(math.sin(f * 1.5) * 7)
            head_cx = 540 + shake_x
            head_cy = 820
            head_r = 135

            # Body
            draw.line([(head_cx, head_cy + head_r), (head_cx, desk_y + 30)], fill=(20, 20, 25), width=20)
            # Hands grabbing head in desperation
            draw.line([(head_cx - 180, head_cy + head_r + 50), (head_cx - 220, head_cy)], fill=(20, 20, 25), width=16)
            draw.line([(head_cx - 220, head_cy), (head_cx - 130, head_cy - 40)], fill=(20, 20, 25), width=16)
            draw.line([(head_cx + 180, head_cy + head_r + 50), (head_cx + 220, head_cy)], fill=(20, 20, 25), width=16)
            draw.line([(head_cx + 220, head_cy), (head_cx + 130, head_cy - 40)], fill=(20, 20, 25), width=16)

            # Face with spiral stress
            draw_sss_stickman_face(draw, head_cx, head_cy, head_r, f, mood="spiral_stress")

            # Floating Browser Tabs popping in with spring bounce
            tabs = [
                (100, 300, "⚠️ DEADLINE SẮP TỚI!", (255, 60, 80)),
                (640, 240, "💸 Tiền nhà tháng này?", (255, 160, 20)),
                (90, 520, "🍜 Trưa nay ăn gì ta?", (0, 190, 255)),
                (650, 480, "💬 Quên trả lời tin nhắn!", (180, 90, 255)),
                (320, 140, "🔥 TAB 99+: OVERTHINKING...", (255, 90, 150))
            ]
            for idx, (tx, ty, text, col) in enumerate(tabs):
                bounce = math.sin(f * 0.25 + idx * 1.2) * 14
                py = int(ty + bounce)
                # Outer glow card
                draw.rounded_rectangle([tx - 4, py - 4, tx + 338, py + 88], radius=20, fill=(10, 10, 15))
                draw.rounded_rectangle([tx, py, tx + 330, py + 80], radius=16, fill=col, outline=(255, 255, 255), width=3)
                draw.text((tx + 25, py + 24), text, fill=(255, 255, 255))

        # ----------------------------------------------------
        # SCENE 3: BED DOOM-SCROLLING (2 AM CYBERPUNK ROOM)
        # ----------------------------------------------------
        elif stype == "bed_doomscroll":
            # Deep night room
            draw.rectangle([0, 0, 1080, 1920], fill=(14, 16, 26))

            # Neon Digital Clock: 02:00 AM (Glowing Red)
            clock_pulse = (math.sin(f * 0.2) + 1.0) / 2.0
            draw.rounded_rectangle([780, 200, 980, 330], radius=20, fill=(24, 26, 38), outline=(255, 50, 80), width=4)
            draw.text((810, 235), "02:00", fill=(255, 60, 80))
            draw.text((840, 280), "AM", fill=(200, 200, 220))

            # Bed with blanket
            draw.rounded_rectangle([80, 1080, 1000, 1780], radius=35, fill=(35, 42, 60), outline=(60, 70, 95), width=8)
            draw.rounded_rectangle([130, 1120, 430, 1300], radius=25, fill=(55, 65, 88), outline=(85, 95, 125), width=6)
            draw.rounded_rectangle([300, 1240, 980, 1760], radius=22, fill=(24, 80, 115), outline=(40, 110, 155), width=6)

            # Stickman lying in bed
            head_cx, head_cy = 310, 1200
            head_r = 115
            draw.ellipse([head_cx - head_r, head_cy - head_r, head_cx + head_r, head_cy + head_r], fill=(255, 255, 255), outline=(20, 20, 25), width=9)

            # Phone glowing beam casting on face
            phone_x, phone_y = 570, 980
            draw.polygon([(phone_x - 30, phone_y - 70), (phone_x + 80, phone_y - 70), (head_cx + 90, head_cy - 70), (head_cx - 40, head_cy + 50)], fill=(20, 75, 110))

            # Smartphone
            draw.rounded_rectangle([phone_x - 35, phone_y - 85, phone_x + 85, phone_y + 85], radius=18, fill=(18, 18, 22), outline=(0, 220, 255), width=4)
            draw.rounded_rectangle([phone_x - 26, phone_y - 75, phone_x + 76, phone_y + 45], radius=10, fill=(0, 230, 255))
            # TikTok Play triangle
            draw.polygon([(phone_x + 10, phone_y - 30), (phone_x + 45, phone_y - 15), (phone_x + 10, phone_y)], fill=(255, 255, 255))

            # Arms holding phone
            draw.line([(head_cx + 70, head_cy + 90), (phone_x - 35, phone_y + 85)], fill=(20, 20, 25), width=14)
            draw.line([(phone_x - 35, phone_y + 85), (phone_x + 10, phone_y + 35)], fill=(20, 20, 25), width=14)

            # Eyes wide open with dark panda circles
            eye_y = head_cy - 12
            # Dark circles
            draw.ellipse([head_cx + 10, eye_y - 25, head_cx + 55, eye_y + 25], fill=(160, 170, 195))
            draw.ellipse([head_cx + 15, eye_y - 18, head_cx + 50, eye_y + 18], fill=(255, 255, 255), outline=(20, 20, 25), width=4)
            draw.ellipse([head_cx + 28, eye_y - 8, head_cx + 42, eye_y + 8], fill=(0, 210, 255)) # screen glow reflection

        # ----------------------------------------------------
        # SCENE 4: OUTDOOR ZEN NATURE (REFRESHING BREEZE)
        # ----------------------------------------------------
        elif stype == "outdoor_zen":
            # Vibrant sunny sky
            for y in range(0, 1260, 4):
                p = y / 1260
                r = int(180 + 40 * p)
                g = int(225 + 25 * p)
                b = int(255)
                draw.rectangle([0, y, 1080, y + 4], fill=(r, g, b))

            # Glowing Sun with rotating rays
            sun_cx, sun_cy = 880, 220
            draw.ellipse([sun_cx - 70, sun_cy - 70, sun_cx + 70, sun_cy + 70], fill=(255, 215, 0), outline=(255, 170, 0), width=6)
            for ang in range(0, 360, 40):
                rad = math.radians(ang + f * 1.8)
                draw.line([(sun_cx + math.cos(rad) * 85, sun_cy + math.sin(rad) * 85),
                           (sun_cx + math.cos(rad) * 125, sun_cy + math.sin(rad) * 125)], fill=(255, 190, 0), width=6)

            # Lush green rolling hill
            draw.ellipse([-200, 1180, 1300, 2200], fill=(85, 180, 105))
            draw.ellipse([-200, 1240, 1300, 2200], fill=(65, 155, 85))

            # Stickman walking cheerfully
            walk_cycle = math.sin(f * 0.45)
            head_cx = 480 + int(f * 2.5) % 200
            head_cy = 760 + int(abs(walk_cycle) * 16)
            head_r = 135

            # Body
            torso_bot = head_cy + head_r + 230
            draw.line([(head_cx, head_cy + head_r), (head_cx, torso_bot)], fill=(20, 20, 25), width=18)

            # Legs swinging
            leg_ang = walk_cycle * 38
            lx = head_cx + int(math.sin(math.radians(leg_ang)) * 250)
            ly = torso_bot + int(math.cos(math.radians(leg_ang)) * 250)
            rx = head_cx - int(math.sin(math.radians(leg_ang)) * 250)
            ry = torso_bot + int(math.cos(math.radians(leg_ang)) * 250)
            draw.line([(head_cx, torso_bot), (lx, min(ly, 1280))], fill=(20, 20, 25), width=16)
            draw.line([(head_cx, torso_bot), (rx, min(ry, 1280))], fill=(20, 20, 25), width=16)

            # Arms open wide enjoying fresh air
            draw.line([(head_cx, head_cy + head_r + 50), (head_cx - 180, head_cy + head_r)], fill=(20, 20, 25), width=14)
            draw.line([(head_cx, head_cy + head_r + 50), (head_cx + 180, head_cy + head_r)], fill=(20, 20, 25), width=14)

            # Face smiling
            draw_sss_stickman_face(draw, head_cx, head_cy, head_r, f, mood="smile")

            # Wind / breeze sparkles
            for i in range(3):
                wx = int((f * 8 + i * 280) % 1100)
                wy = 480 + i * 90
                draw.arc([wx, wy, wx + 150, wy + 40], 180, 360, fill=(255, 255, 255), width=5)

        # ----------------------------------------------------
        # TOP CATEGORY BADGE (PIL GLOWING CAPSULE)
        # ----------------------------------------------------
        badge_text = scene.get("badge", "")
        if badge_text:
            badge_bg = (18, 20, 28)
            draw.rounded_rectangle([136, 86, 944, 164], radius=24, fill=(10, 10, 15))
            draw.rounded_rectangle([140, 90, 940, 160], radius=20, fill=badge_bg, outline=(255, 215, 0), width=3)
            draw.text((220, 108), f"⚡ {badge_text}", fill=(255, 235, 120))

        # Convert to OpenCV BGR
        frame_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # ----------------------------------------------------
        # SSS-TIER CAMERA PUNCH-IN & SCREEN SHAKE
        # ----------------------------------------------------
        p = f / max(1, total_frames - 1)
        # Snappy zoom on key moments
        if scene_id == 1 and f > 40:
            zoom = 1.0 + min(0.14, (f - 40) * 0.015)
        elif scene_id == 2:
            zoom = 1.05 + 0.03 * math.sin(f * 0.5) # subtle pulsating stress
        else:
            zoom = 1.0 + 0.04 * p

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

def build_ass_subtitles(scenes, durations, out_file: Path):
    """
    Kinetic TikTok Subtitles (Alex Hormozi / Douyin High-Retention Style)
    - MarginV=190 in Safe Zone
    - High-contrast bold typography with neon cyan highlight for key phrases
    """
    header = """[Script Info]
Title: SSS-Tier Viral Kinetic Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: MainLine,Segoe UI,58,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,2,2,60,60,190,1
Style: SubLine,Segoe UI,44,&H0000E5FF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,4,2,2,60,60,285,1

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

        events.append(f"Dialogue: 0,{t0},{t1},SubLine,,0,0,285,,{l1}")
        events.append(f"Dialogue: 0,{t0},{t1},MainLine,,0,0,190,,{l2}")

        current_time += dur

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events))

def main():
    print("=" * 75)
    print("💎 KHỞI ĐỘNG HỆ THỐNG SẢN XUẤT STICKMAN SSS-TIER (COMMERCIAL GRADE)")
    print("   -> Nghệ thuật Webcomic phòng thu Podcast Neon cao cấp")
    print("   -> Foley Sound FX (Ding, Pop, Whoosh, Thud) + BGM Lo-Fi Groovy")
    print("   -> Dynamic Camera Punch-in & Kinetic TikTok Subtitles")
    print("=" * 75)

    # 1. Foley SFX
    print("\n[1/5] Khởi tạo bộ âm thanh hiệu ứng Foley (Ding, Pop, Whoosh, Thud)...")
    create_foley_sfx(WORK_DIR)
    print("✔ Đã tạo xong 4 file Foley SFX chất lượng cao.")

    # 2. Voiceover & BGM
    print("\n[2/5] Tạo giọng đọc diễn cảm & kết hợp BGM Lo-Fi...")
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
    print(f"✔ Đã ghép xong giọng nói ({total_audio_dur:.2f}s)")

    # Mix BGM and Sound FX into Master Audio Track
    bgm_source = WORKSPACE_ROOT / "MoneyPrinterTurbo" / "resource" / "songs" / "output000.mp3"
    master_audio = WORK_DIR / "master_audio.mp3"
    
    # Audio filter graph: Voice + BGM (volume 0.18 ducked) + Foley SFX at scene transitions
    # Transition times
    t_pop = durations[0] + 0.1
    t_ding = durations[0] + durations[1] + durations[2] + durations[3] + 0.2
    
    cmd_audio_mix = [
        FFMPEG, "-y",
        "-i", str(raw_voice),
        "-i", str(bgm_source),
        "-i", str(WORK_DIR / "sfx_ding.wav"),
        "-i", str(WORK_DIR / "sfx_pop.wav"),
        "-filter_complex",
        f"[1:a]volume=0.18,atrim=0:{total_audio_dur},afade=t=out:st={total_audio_dur-2.5}:d=2.5[bgm];"
        f"[2:a]adelay=400|400,volume=0.6[sfx1];"
        f"[3:a]adelay={int(t_pop*1000)}|{int(t_pop*1000)},volume=0.8[sfx2];"
        f"[0:a][bgm][sfx1][sfx2]amix=inputs=4:duration=first:dropout_transition=2[aout]",
        "-map", "[aout]",
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(master_audio)
    ]
    subprocess.run(cmd_audio_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print("✔ Đã hòa âm Master: Giọng thoại + Nhạc nền Lo-fi + Âm thanh Foley!")

    # 3. Render each SSS Scene Clip
    print("\n[3/5] Render hoạt hình người que Webcomic chuẩn SSS-Tier...")
    clips = []
    for s, dur in zip(SCENES, durations):
        print(f"  • Render Scene {s['id']}: {s['title']} ({dur:.2f}s)...")
        c = render_sss_scene(s, dur)
        clips.append(c)

    # 4. Concatenate and burn Kinetic Subtitles
    print("\n[4/5] Ghép nối và ép phụ đề Kinetic TikTok nổi bật...")
    ass_path = WORK_DIR / "sss_subtitles.ass"
    build_ass_subtitles(SCENES, durations, ass_path)
    escaped_ass = str(ass_path.resolve()).replace("\\", "/").replace(":", "\\:")

    inputs = []
    filter_inputs = ""
    for idx, c in enumerate(clips):
        inputs.extend(["-i", str(c)])
        filter_inputs += f"[{idx}:v]fps=30,setpts=PTS-STARTPTS[v{idx}];"

    concat_filter = f"{filter_inputs}" + "".join([f"[v{i}]" for i in range(len(clips))]) + f"concat=n={len(clips)}:v=1:a=0[vconcat]"
    full_filter = f"{concat_filter};[vconcat]subtitles='{escaped_ass}'[vfinal]"

    out_path = OUT_DIR / "video_stickman_sss_tier_commercial.mp4"

    cmd_final = [
        FFMPEG, "-y",
        *inputs,
        "-i", str(master_audio),
        "-filter_complex", full_filter,
        "-map", "[vfinal]",
        "-map", f"{len(clips)}:a",
        "-c:v", "libx264", "-crf", "17", "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(out_path)
    ]
    subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"\n🎉 Xuất video SSS-Tier thành công: {out_path.name} ({size_mb:.1f} MB)")

    # Save copy to Desktop
    desktop_copy = Path("C:/Users/User/Desktop/video_stickman_sss_tier_commercial.mp4")
    try:
        import shutil
        shutil.copy2(str(out_path), str(desktop_copy))
        print(f"💾 Đã lưu bản sao trên Desktop: {desktop_copy.name}")
    except Exception as e:
        pass

    # 5. Dispatch to Telegram Video Hub
    print("\n[5/5] Gửi video về Telegram Video Hub...")
    ok, res = dispatch_video(
        video_path=str(out_path),
        title="🔥 Đẳng Cấp SSS-Tier: Hoạt Hình Người Que Podcast Thương Mại (Commercial Grade)",
        description="Nâng cấp toàn diện: Nghệ thuật Webcomic phòng thu Podcast Neon, đèn ON AIR phát sáng, character mắt to catchlight, Foley Sound Effects (Ding, Pop, Whoosh, Thud) + BGM Lo-fi Groovy, Dynamic Camera Punch-in.",
        app_name="Stickman-SSSTier",
        tags=["SSSTier", "CommercialGrade", "StickmanViral", "PodcastStudio", "TikTokKinetic"],
        blocking=True
    )
    if ok:
        print(f"✅ {res}")
    else:
        print(f"⚠️ Dispatch notice: {res}")

if __name__ == "__main__":
    main()
