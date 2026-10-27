#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Douyin Viral Bilingual Video Generator
Generates cinematic Chinese-Vietnamese life quotes/reup style videos.
Full-screen moving video footage, emotional BGM, zero classroom vibe!
"""

import os
import sys
import re
import json
import shutil
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path

# Fix console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

FFMPEG_PATH_KNOWN = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin"
if os.path.exists(FFMPEG_PATH_KNOWN) and FFMPEG_PATH_KNOWN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = FFMPEG_PATH_KNOWN + os.pathsep + os.environ.get("PATH", "")

FFMPEG_BIN = shutil.which("ffmpeg") or os.path.join(FFMPEG_PATH_KNOWN, "ffmpeg.exe")

AUDIO_DIR = Path("audio_douyin")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# 4 Viral Douyin Quotes on Life & Growth
QUOTES = [
    {
        "id": 1,
        "cn": "穷在闹市无人问，富在深山有远亲。",
        "vi": "Nghèo giữa chợ đông không ai ngó, giàu nơi núi thẳm có bạn thăm.",
        "bg_video": "video_bg/bg_night_city.mp4"
    },
    {
        "id": 2,
        "cn": "不是现实太残酷，而是你没有让人尊敬的实力。",
        "vi": "Không phải hiện thực quá tàn nhẫn, mà là bạn chưa đủ thực lực để người ta tôn trọng.",
        "bg_video": "video_bg/bg_night_city.mp4"
    },
    {
        "id": 3,
        "cn": "成年人的世界，没有退路，只有坚强。",
        "vi": "Thế giới của người trưởng thành, không có đường lui, chỉ có kiên cường.",
        "bg_video": "video_bg/bg_mountain.mp4"
    },
    {
        "id": 4,
        "cn": "默默努力吧，当你有价值的时候，整个世界都会对你和颜悦色。",
        "vi": "Hãy âm thầm nỗ lực, khi bạn có giá trị, cả thế giới sẽ dịu dàng với bạn.",
        "bg_video": "video_bg/bg_mountain.mp4"
    }
]

def get_duration(audio_path):
    proc = subprocess.run([FFMPEG_BIN, "-i", str(audio_path)], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors="replace")
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", proc.stderr)
    if m:
        h, mn, s = float(m.group(1)), float(m.group(2)), float(m.group(3))
        return h * 3600 + mn * 60 + s
    return 4.5

def download_tts_enhanced(text: str, output_path: Path):
    """Downloads TTS and applies deep documentary pitch filter."""
    raw_path = output_path.with_suffix(".raw.mp3")
    clean_text = re.sub(r"[^\w\s\u4e00-\u9fff，。！？、“”：]", "", text)
    url = "https://translate.google.com/translate_tts?ie=UTF-8&tl=zh-CN&client=tw-ob&q=" + urllib.parse.quote(clean_text)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw_path.write_bytes(resp.read())
    
    # Apply warm resonance filter: slightly slower tempo for dramatic emotional delivery
    cmd = [
        FFMPEG_BIN, "-y", "-i", str(raw_path),
        "-filter:a", "atempo=0.92,equalizer=f=120:width_type=o:w=1:g=2.5",
        "-c:a", "libmp3lame", "-q:a", "2",
        str(output_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if raw_path.exists():
        raw_path.unlink()

print("Generating emotional Douyin voiceover...")
current_start = 0.0
scenes_data = []

for q in QUOTES:
    audio_file = AUDIO_DIR / f"quote_{q['id']}.mp3"
    download_tts_enhanced(q["cn"], audio_file)
    dur = get_duration(audio_file)
    scene_dur = round(dur + 1.0, 2)  # 1s dramatic pause
    
    scenes_data.append({
        **q,
        "audio_file": str(audio_file).replace("\\", "/"),
        "audio_duration": dur,
        "start": round(current_start, 2),
        "dur": scene_dur
    })
    print(f"  Quote {q['id']}: start={current_start:.2f}s, dur={scene_dur:.2f}s | {q['cn'][:12]}...")
    current_start += scene_dur

total_duration = round(current_start, 2)
print(f"Total video length: {total_duration}s")

# Build Douyin Cinematic HTML Composition
# 2 background video clips: City night (first half) -> Mountain drone (second half)
split_time = scenes_data[1]["start"] + scenes_data[1]["dur"]

html_content = f'''<!doctype html>
<html lang="zh" data-resolution="portrait">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=1080, height=1920" />
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Ma+Shan+Zheng&family=Noto+Serif+SC:wght@600;700;900&family=Plus+Jakarta+Sans:ital,wght@0,500;0,700;1,400;1,600&display=swap" rel="stylesheet">
  <style>
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}
    html, body {{
      width: 1080px;
      height: 1920px;
      overflow: hidden;
      background: #000000;
      font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
    }}

    #root {{
      width: 100%;
      height: 100%;
      position: relative;
      overflow: hidden;
    }}

    /* Video Background Footage Layers */
    .bg-video {{
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      z-index: 1;
    }}

    /* Cinematic Film Vignette & Shadow Overlay */
    .vignette {{
      position: absolute;
      inset: 0;
      z-index: 2;
      background: radial-gradient(circle at 50% 45%, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0.75) 85%, rgba(0,0,0,0.95) 100%);
      pointer-events: none;
    }}

    .bottom-gradient {{
      position: absolute;
      bottom: 0;
      left: 0;
      width: 100%;
      height: 900px;
      z-index: 2;
      background: linear-gradient(to top, rgba(0,0,0,0.92) 0%, rgba(0,0,0,0.6) 60%, transparent 100%);
      pointer-events: none;
    }}

    /* Top Douyin Aesthetic Tag */
    .douyin-tag {{
      position: absolute;
      top: 100px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 10;
      display: inline-flex;
      align-items: center;
      gap: 12px;
      padding: 12px 32px;
      border-radius: 40px;
      background: rgba(0, 0, 0, 0.45);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.18);
      color: #f6d365;
      font-size: 24px;
      font-weight: 700;
      letter-spacing: 3px;
      text-transform: uppercase;
    }}

    /* Central Quote Stage */
    .stage {{
      position: absolute;
      bottom: 340px;
      left: 60px;
      right: 60px;
      z-index: 10;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
    }}

    .quote-box {{
      position: absolute;
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      gap: 24px;
    }}

    /* Douyin Reup Chinese Subtitle (Bold, Glowing, Cinematic) */
    .cn-text {{
      font-family: 'Noto Serif SC', 'Ma Shan Zheng', serif;
      font-size: 54px;
      font-weight: 900;
      line-height: 1.5;
      color: #ffffff;
      letter-spacing: 2px;
      text-shadow: 0 4px 25px rgba(0, 0, 0, 0.95), 0 0 40px rgba(0,0,0,0.8);
      max-width: 960px;
    }}

    .cn-text span.gold {{
      color: #f6d365;
      text-shadow: 0 0 25px rgba(246, 211, 101, 0.6);
    }}

    /* Vietnamese Translation (Clean, Aesthetic, Emotional) */
    .vi-text {{
      font-size: 34px;
      font-weight: 500;
      line-height: 1.55;
      color: #e2e8f0;
      font-style: italic;
      letter-spacing: 0.5px;
      text-shadow: 0 3px 15px rgba(0, 0, 0, 0.95);
      max-width: 900px;
    }}

    /* Subtle Gold Accent Line */
    .accent-bar {{
      width: 60px;
      height: 4px;
      background: linear-gradient(90deg, #f6d365, #fda085);
      border-radius: 2px;
      box-shadow: 0 0 15px rgba(246, 211, 101, 0.8);
    }}

    /* Minimal Bottom Player Bar */
    .footer-track {{
      position: absolute;
      bottom: 80px;
      left: 80px;
      right: 80px;
      z-index: 10;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 16px;
    }}

    .progress-bar {{
      width: 100%;
      height: 6px;
      background: rgba(255, 255, 255, 0.2);
      border-radius: 3px;
      overflow: hidden;
    }}

    .progress-fill {{
      width: 0%;
      height: 100%;
      background: #f6d365;
    }}

    .sub-brand {{
      font-size: 20px;
      color: rgba(255, 255, 255, 0.5);
      letter-spacing: 4px;
      font-weight: 500;
    }}
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{total_duration:.2f}" data-width="1080" data-height="1920">
    
    <!-- Moving Video Background (Part 1: Night City) -->
    <video id="vid1" class="bg-video clip" src="video_bg/bg_night_city.mp4" data-start="0.00" data-duration="{split_time:.2f}" muted autoplay loop></video>
    
    <!-- Moving Video Background (Part 2: Majestic Mountain) -->
    <video id="vid2" class="bg-video clip" src="video_bg/bg_mountain.mp4" data-start="{split_time:.2f}" data-duration="{(total_duration - split_time):.2f}" muted autoplay loop></video>

    <!-- Cinematic Overlays -->
    <div class="vignette"></div>
    <div class="bottom-gradient"></div>

    <!-- Voiceover Audio Tracks -->
    <audio id="v1" src="{scenes_data[0]['audio_file']}" data-start="{scenes_data[0]['start']:.2f}" data-duration="{scenes_data[0]['dur']:.2f}"></audio>
    <audio id="v2" src="{scenes_data[1]['audio_file']}" data-start="{scenes_data[1]['start']:.2f}" data-duration="{scenes_data[1]['dur']:.2f}"></audio>
    <audio id="v3" src="{scenes_data[2]['audio_file']}" data-start="{scenes_data[2]['start']:.2f}" data-duration="{scenes_data[2]['dur']:.2f}"></audio>
    <audio id="v4" src="{scenes_data[3]['audio_file']}" data-start="{scenes_data[3]['start']:.2f}" data-duration="{scenes_data[3]['dur']:.2f}"></audio>
    <audio id="bgm" src="audio/douyin_bgm.mp3" data-start="0.00" data-duration="{total_duration:.2f}" data-volume="0.18"></audio>

    <!-- Top Tag -->
    <div class="douyin-tag">
      <span>🏮</span> 人生感悟 • ĐẠO LÝ ĐỜI NGƯỜI
    </div>

    <!-- Central Stage -->
    <div class="stage">
      <div id="quote-1" class="quote-box clip" data-start="{scenes_data[0]['start']:.2f}" data-duration="{scenes_data[0]['dur']:.2f}">
        <div class="cn-text">“<span class="gold">穷在闹市</span>无人问，<br><span class="gold">富在深山</span>有远亲。”</div>
        <div class="accent-bar"></div>
        <div class="vi-text">“Nghèo giữa chợ đông không ai ngó,<br>giàu nơi núi thẳm có bạn thăm.”</div>
      </div>

      <div id="quote-2" class="quote-box clip" data-start="{scenes_data[1]['start']:.2f}" data-duration="{scenes_data[1]['dur']:.2f}">
        <div class="cn-text">“不是现实太残酷，<br>而是你没有让人尊敬的<span class="gold">实力</span>。”</div>
        <div class="accent-bar"></div>
        <div class="vi-text">“Không phải hiện thực quá tàn nhẫn,<br>mà là bạn chưa đủ thực lực để người ta tôn trọng.”</div>
      </div>

      <div id="quote-3" class="quote-box clip" data-start="{scenes_data[2]['start']:.2f}" data-duration="{scenes_data[2]['dur']:.2f}">
        <div class="cn-text">“成年人的世界，<br><span class="gold">没有退路</span>，只有坚强。”</div>
        <div class="accent-bar"></div>
        <div class="vi-text">“Thế giới của người trưởng thành,<br>không có đường lui, chỉ có kiên cường.”</div>
      </div>

      <div id="quote-4" class="quote-box clip" data-start="{scenes_data[3]['start']:.2f}" data-duration="{scenes_data[3]['dur']:.2f}">
        <div class="cn-text">“默默努力吧，当你有价值的时候，<br><span class="gold">整个世界都会对你和颜悦色</span>。”</div>
        <div class="accent-bar"></div>
        <div class="vi-text">“Hãy âm thầm nỗ lực, khi bạn có giá trị,<br>cả thế giới này sẽ dịu dàng với bạn.”</div>
      </div>
    </div>

    <!-- Bottom Footer -->
    <div class="footer-track">
      <div class="progress-bar">
        <div id="prog-fill" class="progress-fill"></div>
      </div>
      <div class="sub-brand">DOUYIN REUP • SONG NGỮ TRUNG VIỆT</div>
    </div>
  </div>

  <script>
    const tl = gsap.timeline({{ paused: true }});

    // Scene 1 Animation
    tl.fromTo("#quote-1", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.8, ease: "power2.out" }}, 0.2);
    tl.to("#quote-1", {{ opacity: 0, y: -30, duration: 0.5, ease: "power2.in" }}, {scenes_data[0]['dur'] - 0.5:.2f});

    // Scene 2 Animation
    tl.fromTo("#quote-2", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.8, ease: "power2.out" }}, {scenes_data[1]['start'] + 0.2:.2f});
    tl.to("#quote-2", {{ opacity: 0, y: -30, duration: 0.5, ease: "power2.in" }}, {scenes_data[1]['start'] + scenes_data[1]['dur'] - 0.5:.2f});

    // Scene 3 Animation
    tl.fromTo("#quote-3", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.8, ease: "power2.out" }}, {scenes_data[2]['start'] + 0.2:.2f});
    tl.to("#quote-3", {{ opacity: 0, y: -30, duration: 0.5, ease: "power2.in" }}, {scenes_data[2]['start'] + scenes_data[2]['dur'] - 0.5:.2f});

    // Scene 4 Animation
    tl.fromTo("#quote-4", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.8, ease: "power2.out" }}, {scenes_data[3]['start'] + 0.2:.2f});
    tl.to("#quote-4", {{ opacity: 0, y: -30, duration: 0.5, ease: "power2.in" }}, {scenes_data[3]['start'] + scenes_data[3]['dur'] - 0.5:.2f});

    // Continuous Progress Fill
    tl.fromTo("#prog-fill", {{ width: "0%" }}, {{ width: "100%", duration: {total_duration:.2f}, ease: "none" }}, 0);

    window.__timelines = window.__timelines || {{}};
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
'''

output_html = Path("douyin_reup_composition.html")
output_html.write_text(html_content, encoding="utf-8")
print(f"[✓] Generated composition: {output_html}")
