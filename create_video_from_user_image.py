#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate TikTok/Reels 9:16 Video from User's Chinese Learning Infographic
"""

import os
import sys
import json
import asyncio
from pathlib import Path
import subprocess
from PIL import Image, ImageFilter, ImageOps
import edge_tts

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

WORKSPACE_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from telegram_video_hub import dispatch_video

FFMPEG = "ffmpeg"
IMAGE_PATH = Path(r"D:\0.PROGRAMME\4. DEAN OPTIMIZE\12.Vibe idea (tạm)\.telegravity_uploads\tg_1792726291_telegram_photo.jpg")

SCENES = [
    {
        "id": 1,
        "title": "Mở đầu • Toàn cảnh",
        "cn": "学习中文，快乐每一天！今天我们一起来看图学单词吧。",
        "vi": "Học tiếng Trung, vui mỗi ngày! Hôm nay chúng ta cùng nhìn tranh học từ vựng nhé.",
        "crop": "full"
    },
    {
        "id": 2,
        "title": "Đầu, Mặt & Điện thoại",
        "cn": "躺在地上看手机 (shǒujī)，头上 (tóu) 有乌黑的头发，圆圆的脸 (liǎn) 和明亮的眼睛 (yǎnjing)。",
        "vi": "Nằm lướt điện thoại (shǒujī), có đầu (tóu), khuôn mặt (liǎn) và đôi mắt (yǎnjing).",
        "crop": (30, 200, 520, 500)
    },
    {
        "id": 3,
        "title": "Tay, Cánh tay & Thẻ căn cước",
        "cn": "双手 (shǒu) 拿着手机，张开手臂 (shǒubì)，胸前还挂着工作证件 (zhèngjiàn)。",
        "vi": "Hai bàn tay (shǒu) cầm điện thoại, cánh tay (shǒubì) và thẻ căn cước (zhèngjiàn).",
        "crop": (150, 360, 580, 440)
    },
    {
        "id": 4,
        "title": "Vòng eo, Quần, Đôi chân & Bàn chân",
        "cn": "系好腰带 (yāodài)，穿着舒适的裤子 (kùzi)，伸展双腿 (tuǐ) 和双脚 (jiǎo)。",
        "vi": "Thắt lưng (yāodài), mặc chiếc quần (kùzi), đôi chân (tuǐ) và bàn chân (jiǎo).",
        "crop": (320, 430, 448, 590)
    },
    {
        "id": 5,
        "title": "Mẹo nhỏ • Nghỉ ngơi",
        "cn": "最后的小提示：手机虽然好玩，也要注意多休息哦！",
        "vi": "Mẹo nhỏ cuối cùng: Điện thoại tuy vui, nhưng cũng phải chú ý nghỉ ngơi nhé!",
        "crop": (360, 710, 400, 310)
    }
]

def make_9x16_canvas(orig_img: Image.Image, crop_rect=None) -> Image.Image:
    """
    Fits cropped region or whole image onto a beautiful 1080x1920 (9:16) vertical canvas.
    Uses soft blurred background of the image itself for an aesthetic studio look!
    """
    canvas_w, canvas_h = 1080, 1920
    
    if crop_rect == "full" or crop_rect is None:
        sub_img = orig_img
    else:
        x, y, w, h = crop_rect
        sub_img = orig_img.crop((x, y, x + w, y + h))

    # Create blurred background from the original image
    bg = orig_img.resize((canvas_w, canvas_h), Image.Resampling.BILINEAR)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=35))
    
    # Overlay a semi-transparent dark layer for contrast
    dim = Image.new("RGBA", (canvas_w, canvas_h), (20, 20, 25, 110))
    bg.paste(dim, (0, 0), dim)

    # Scale the focal image to fit nicely within 90% width of the canvas
    target_w = int(canvas_w * 0.94)
    scale = target_w / sub_img.width
    target_h = int(sub_img.height * scale)
    
    # If height exceeds 65% of screen, scale by height instead
    max_h = int(canvas_h * 0.65)
    if target_h > max_h:
        scale = max_h / sub_img.height
        target_w = int(sub_img.width * scale)
        target_h = max_h

    fitted_img = sub_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Add rounded corners and white border to the focal image card
    bordered = ImageOps.expand(fitted_img, border=6, fill="white")
    
    # Paste onto center (slightly higher than center to leave room for subtitles)
    paste_x = (canvas_w - bordered.width) // 2
    paste_y = (canvas_h - bordered.height) // 2 - 120
    bg.paste(bordered, (paste_x, paste_y))

    return bg

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
Style: Bilingual,Microsoft YaHei,52,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,4.0,2.0,2,40,40,320,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    for sc in scenes:
        start_ts = format_ass_timestamp(sc["start"])
        end_ts = format_ass_timestamp(sc["start"] + sc["dur"])
        cn = sc["cn"]
        vi = sc["vi"]
        text_line = f"{{\\b1\\c&H00FFFFFF\\fs52}}{cn}\\N{{\\b1\\c&H003CEBFF\\fs40}}{vi}"
        ass_content += f"Dialogue: 0,{start_ts},{end_ts},Bilingual,,0,0,0,,{text_line}\n"

    output_ass.write_text(ass_content, encoding="utf-8")

def main():
    print("=" * 60)
    print("🎨 TẠO VIDEO TỪ BỨC ẢNH HỌC TIẾNG TRUNG (Chuẩn 9:16 Điện Thoại)")
    print("=" * 60)

    work_dir = Path("temp_image_video")
    work_dir.mkdir(parents=True, exist_ok=True)
    out_path = Path("storage/video_hoc_tieng_trung_tu_anh.mp4").resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    orig_img = Image.open(IMAGE_PATH).convert("RGBA")
    print(f"Loaded image: {IMAGE_PATH.name} ({orig_img.size[0]}x{orig_img.size[1]})")

    print("\n[1/4] Tạo giọng đọc Tiếng Trung Xiaoxiao (Cute & Trong trẻo)...")
    current_time = 0.0
    audio_files = []

    for sc in SCENES:
        idx = sc["id"]
        audio_p = work_dir / f"voice_{idx}.mp3"
        dur = asyncio.run(generate_speech(sc["cn"], audio_p, voice="zh-CN-XiaoxiaoNeural"))
        scene_dur = round(dur + 0.7, 2)
        sc["start"] = round(current_time, 2)
        sc["dur"] = scene_dur
        sc["audio"] = str(audio_p)
        audio_files.append(audio_p)
        print(f"  • Cảnh {idx} [{sc['title']}]: {scene_dur:.1f}s | {sc['cn'][:16]}...")
        current_time += scene_dur

    total_duration = round(current_time, 2)
    print(f"  -> Tổng thời lượng video: {total_duration:.2f}s")

    print("\n[2/4] Ghép âm thanh & Nhạc nền Lo-fi Cute...")
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
            f"[0:a]volume=1.0[voice];[1:a]volume=0.15[bgm];[voice][bgm]amix=inputs=2:duration=first[aout]",
            "-map", "[aout]",
            "-t", f"{total_duration:.2f}",
            str(final_audio)
        ]
        subprocess.run(cmd_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    else:
        final_audio = merged_voice

    print("\n[3/4] Cắt khung hình & Tạo chuyển động 30 FPS cho từng phân cảnh...")
    clip_files = []
    for sc in SCENES:
        idx = sc["id"]
        # Generate 9:16 canvas for this scene
        scene_canvas = make_9x16_canvas(orig_img, sc["crop"])
        canvas_path = work_dir / f"canvas_{idx}.jpg"
        scene_canvas.convert("RGB").save(canvas_path, quality=95)

        # Render 30fps clip with subtle Ken Burns zoom
        clip_out = work_dir / f"clip_{idx}.mp4"
        cmd_clip = [
            FFMPEG, "-y",
            "-loop", "1", "-i", str(canvas_path),
            "-t", f"{sc['dur']:.2f}",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setpts=N/(30*TB),setsar=1",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-an",
            str(clip_out)
        ]
        subprocess.run(cmd_clip, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        clip_files.append(clip_out)
        print(f"  ✓ Rendered clip {idx}: {sc['dur']:.1f}s (1080x1920 @ 30.00fps)")

    # Concatenate clips using filter_complex
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
        "-c:v", "libx264", "-crf", "20", "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(out_path)
    ]
    subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    print(f"\n🎉 Video hoàn thành: {out_path.name} ({out_path.stat().st_size / (1024*1024):.1f} MB)")

    # Save copy to Desktop
    desktop_copy = Path("C:/Users/User/Desktop/video_hoc_tieng_trung_tu_anh.mp4")
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
        title="Học Tiếng Trung Qua Ảnh: Các Bộ Phận Cơ Thể & Đồ Vật (日常单词)",
        description="Video được tạo từ bức ảnh infographic học tiếng Trung: giọng đọc Xiaoxiao, phụ đề song ngữ, tỷ lệ chuẩn 9:16.",
        app_name="ImageToVideo-Chinese",
        tags=["HocTiengTrungQuaAnh", "TuVungCoThe", "XiaoxiaoVoice", "SongNgu9x16"],
        blocking=True
    )
    if ok:
        print(f"✅ {res}")
    else:
        print(f"⚠️ Dispatch notice: {res}")

if __name__ == "__main__":
    main()
