#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilingual Story Studio - Video Generator
Automated 9:16 Short Video Maker for Chinese-Vietnamese Storytelling
Powered by HyperFrames + GSAP + Edge/Google TTS
"""

import os
import sys
import re
import json
import shutil
import argparse
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path

# Fix Windows console utf-8 encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure Gyan FFmpeg is in PATH
FFMPEG_PATH_KNOWN = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin"
if os.path.exists(FFMPEG_PATH_KNOWN) and FFMPEG_PATH_KNOWN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = FFMPEG_PATH_KNOWN + os.pathsep + os.environ.get("PATH", "")

FFMPEG_BIN = shutil.which("ffmpeg") or os.path.join(FFMPEG_PATH_KNOWN, "ffmpeg.exe")

try:
    from pypinyin import pinyin, Style
except ImportError:
    pinyin = None


def hanzi_to_ruby(text: str) -> str:
    """Converts Chinese Hanzi into HTML <ruby> characters with pinyin tones."""
    if not pinyin:
        return text
    
    # Process character by character while keeping punctuation
    result = []
    for char in text:
        if "\u4e00" <= char <= "\u9fff":
            py_list = pinyin(char, style=Style.TONE)
            py = py_list[0][0] if py_list and py_list[0] else ""
            result.append(f"<ruby>{char}<rt>{py}</rt></ruby>")
        else:
            result.append(char)
    return "".join(result)


def get_audio_duration(audio_path: str) -> float:
    """Extracts exact audio duration in seconds using FFmpeg."""
    try:
        proc = subprocess.run(
            [FFMPEG_BIN, "-i", str(audio_path)],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            errors="replace"
        )
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", proc.stderr)
        if m:
            h, mn, s = float(m.group(1)), float(m.group(2)), float(m.group(3))
            return h * 3600 + mn * 60 + s
    except Exception as e:
        print(f"[!] Warning: Could not get audio duration: {e}")
    return 4.0


def download_tts(text: str, output_path: Path) -> bool:
    """Downloads natural Chinese speech via Edge TTS (Yunxi voice) with Google TTS fallback."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    clean_text = re.sub(r"[^\w\s\u4e00-\u9fff，。！？、“”：]", "", text)
    
    # Try Edge TTS (warm, cinematic native Chinese voice)
    try:
        import asyncio
        import edge_tts
        async def _synth():
            c = edge_tts.Communicate(clean_text, "zh-CN-YunxiNeural", rate="-5%")
            await c.save(str(output_path))
        asyncio.run(_synth())
        if output_path.exists() and output_path.stat().st_size > 500:
            return True
    except Exception as e:
        print(f"[!] Edge-TTS fallback: {e}")

    # Fallback to Google TTS
    url = "https://translate.google.com/translate_tts?ie=UTF-8&tl=zh-CN&client=tw-ob&q=" + urllib.parse.quote(clean_text)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            output_path.write_bytes(resp.read())
        return True
    except Exception as e:
        print(f"[!] TTS Error for '{clean_text}': {e}")
        return False


def parse_story_file(file_path: Path):
    """Parses story file from JSON or TXT format."""
    text = file_path.read_text(encoding="utf-8")
    
    if file_path.suffix.lower() == ".json":
        return json.loads(text)
    
    # Parse TXT format
    title = "Song Ngữ Trung - Việt"
    level = "HSK STORY"
    scenes = []
    current_scene = None

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        if line.startswith("TITLE:"):
            title = line[6:].strip()
        elif line.startswith("LEVEL:"):
            level = line[6:].strip()
        elif line.startswith("[SCENE]") or line.startswith("SCENE:"):
            if current_scene:
                scenes.append(current_scene)
            current_scene = {"cn": "", "vi": "", "vocab": []}
        elif line.startswith("CN:") and current_scene is not None:
            current_scene["cn"] = line[3:].strip()
        elif line.startswith("VI:") and current_scene is not None:
            current_scene["vi"] = line[3:].strip()
        elif line.startswith("VOCAB:") and current_scene is not None:
            vocab_part = line[6:].strip()
            # Parse pairs like "乌龟 (wūguī): Con rùa | 兔子 (tùzi): Con thỏ"
            for pair in vocab_part.split("|"):
                if ":" in pair:
                    w, m = pair.split(":", 1)
                    current_scene["vocab"].append({"word": w.strip(), "meaning": m.strip()})
    
    if current_scene:
        scenes.append(current_scene)
        
    return {"title": title, "level": level, "scenes": scenes}


def build_html_composition(story_data: dict, audio_durations: list, total_duration: float, output_html: Path):
    """Generates the HyperFrames index.html composition."""
    title = story_data.get("title", "Song Ngữ Trung - Việt")
    level = story_data.get("level", "HSK 2-3 STORY")
    scenes = story_data.get("scenes", [])
    
    # Build Audio elements
    audio_tags = []
    for sc in scenes:
        idx = sc["id"]
        start = sc["start"]
        dur = sc["dur"]
        audio_tags.append(f'    <audio id="voice_{idx}" src="{sc["audio_rel"]}" data-start="{start:.2f}" data-duration="{dur:.2f}"></audio>')
    
    audio_tags.append(f'    <audio id="bgm" src="audio/bgm.mp3" data-start="0.00" data-duration="{total_duration:.2f}" data-volume="0.14"></audio>')
    audio_html = "\n".join(audio_tags)

    # Build Scene elements
    scene_elements = []
    for sc in scenes:
        idx = sc["id"]
        start = sc["start"]
        dur = sc["dur"]
        ruby = sc["ruby"]
        vi = sc["vi"]
        
        vocab_chips = []
        for v in sc.get("vocab", []):
            vocab_chips.append(f'''            <div class="vocab-chip">
              <span class="vocab-word">{v.get('word', '')}</span>
              <span class="vocab-meaning">{v.get('meaning', '')}</span>
            </div>''')
        
        vocab_html = ""
        if vocab_chips:
            vocab_html = f'''          <div class="vocab-container">
{chr(10).join(vocab_chips)}
          </div>'''

        scene_html = f'''      <!-- Scene {idx} ({start:.2f}s - {(start+dur):.2f}s) -->
      <div id="scene-{idx}" class="scene-wrap clip" data-start="{start:.2f}" data-duration="{dur:.2f}" data-track-index="1">
        <div class="scene-inner" id="inner-{idx}">
          <div class="content-card">
            <div class="hanzi-box">
              {ruby}
            </div>
            <div class="vi-box">
              <div class="vi-text">“{vi}”</div>
            </div>
          </div>
{vocab_html}
        </div>
      </div>'''
        scene_elements.append(scene_html)

    scenes_html = "\n\n".join(scene_elements)

    # Build GSAP Timeline
    gsap_lines = []
    for sc in scenes:
        idx = sc["id"]
        start = sc["start"]
        dur = sc["dur"]
        in_t = round(start + 0.1, 2)
        out_t = round(start + dur - 0.45, 2)
        gsap_lines.append(f'    tl.fromTo("#inner-{idx}", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power2.out" }}, {in_t});')
        gsap_lines.append(f'    tl.to("#inner-{idx}", {{ opacity: 0, y: -20, duration: 0.4, ease: "power2.in" }}, {out_t});')

    gsap_lines.append(f'    tl.fromTo("#prog-bar", {{ width: "0%" }}, {{ width: "100%", duration: {total_duration:.2f}, ease: "none" }}, 0);')
    gsap_script = "\n".join(gsap_lines)

    template = f'''<!doctype html>
<html lang="zh" data-resolution="portrait">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=1080, height=1920" />
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Ma+Shan+Zheng&family=Noto+Serif+SC:wght@600;700;900&family=Plus+Jakarta+Sans:ital,wght@0,500;0,700;1,400&display=swap" rel="stylesheet">
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
      background: #080a10;
      font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
    }}

    #root {{
      width: 100%;
      height: 100%;
      position: relative;
      background: radial-gradient(circle at 50% 30%, #151b2c 0%, #080b12 70%, #030408 100%);
      color: #ffffff;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 80px 60px 70px 60px;
      overflow: hidden;
    }}

    .bg-decor {{
      position: absolute;
      inset: 0;
      pointer-events: none;
      opacity: 0.25;
      background: 
        radial-gradient(circle at 20% 15%, rgba(246, 211, 101, 0.15) 0%, transparent 40%),
        radial-gradient(circle at 80% 85%, rgba(79, 172, 254, 0.12) 0%, transparent 50%);
    }}

    .bg-circle {{
      position: absolute;
      width: 700px;
      height: 700px;
      border-radius: 50%;
      border: 1px dashed rgba(246, 211, 101, 0.18);
      top: 480px;
      left: 190px;
      pointer-events: none;
    }}

    .header-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 10;
    }}

    .series-tag {{
      display: inline-flex;
      align-items: center;
      gap: 12px;
      background: rgba(246, 211, 101, 0.12);
      border: 1px solid rgba(246, 211, 101, 0.35);
      padding: 12px 28px;
      border-radius: 40px;
      font-size: 26px;
      font-weight: 700;
      color: #f6d365;
      letter-spacing: 1px;
    }}

    .level-badge {{
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      padding: 8px 22px;
      border-radius: 20px;
      font-size: 22px;
      color: #94a3b8;
      font-weight: 600;
    }}

    .story-stage {{
      position: relative;
      width: 100%;
      height: 1280px;
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 10;
    }}

    .scene-wrap {{
      position: absolute;
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}

    .scene-inner {{
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 36px;
    }}

    .content-card {{
      width: 100%;
      background: rgba(14, 20, 35, 0.85);
      backdrop-filter: blur(20px);
      border: 2px solid rgba(246, 211, 101, 0.3);
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6), inset 0 0 30px rgba(246, 211, 101, 0.05);
      border-radius: 36px;
      padding: 60px 48px;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
    }}

    .hanzi-box {{
      font-family: 'Noto Serif SC', 'Ma Shan Zheng', serif;
      line-height: 2.1;
      text-align: center;
      margin-bottom: 28px;
    }}

    ruby {{
      font-size: 58px;
      font-weight: 700;
      color: #ffffff;
      ruby-position: over;
      margin: 0 4px;
      text-shadow: 0 4px 16px rgba(0, 0, 0, 0.8);
    }}

    rt {{
      font-size: 26px;
      font-weight: 600;
      color: #f6d365;
      font-family: 'Plus Jakarta Sans', sans-serif;
      letter-spacing: 0.5px;
      margin-bottom: 6px;
      text-shadow: 0 2px 8px rgba(0, 0, 0, 0.9);
    }}

    .vi-box {{
      background: rgba(255, 255, 255, 0.05);
      border-left: 4px solid #f6d365;
      padding: 24px 32px;
      border-radius: 16px;
      width: 100%;
      text-align: left;
    }}

    .vi-text {{
      font-size: 34px;
      line-height: 1.5;
      color: #e2e8f0;
      font-style: italic;
      font-weight: 500;
    }}

    .vocab-container {{
      width: 100%;
      display: flex;
      gap: 18px;
    }}

    .vocab-chip {{
      flex: 1;
      background: rgba(24, 32, 54, 0.9);
      border: 1px solid rgba(79, 172, 254, 0.35);
      border-radius: 20px;
      padding: 20px 24px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
    }}

    .vocab-word {{
      font-size: 28px;
      font-weight: 700;
      color: #4facfe;
      font-family: 'Noto Serif SC', serif;
    }}

    .vocab-meaning {{
      font-size: 22px;
      color: #94a3b8;
    }}

    .footer-bar {{
      display: flex;
      flex-direction: column;
      gap: 16px;
      z-index: 10;
    }}

    .progress-track {{
      width: 100%;
      height: 8px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 4px;
      overflow: hidden;
    }}

    .progress-fill {{
      width: 0%;
      height: 100%;
      background: linear-gradient(90deg, #f6d365, #fda085);
      border-radius: 4px;
    }}

    .cta-text {{
      text-align: center;
      font-size: 20px;
      color: #64748b;
      letter-spacing: 2px;
      text-transform: uppercase;
    }}
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{total_duration:.2f}" data-width="1080" data-height="1920">
    <div class="bg-decor"></div>
    <div class="bg-circle"></div>

    <!-- Audio Tracks -->
{audio_html}

    <!-- Top Header -->
    <div id="header-bar" class="header-bar clip" data-start="0" data-duration="{total_duration:.2f}" data-track-index="0">
      <div class="series-tag">
        <span>🏮</span> {title}
      </div>
      <div class="level-badge">{level}</div>
    </div>

    <!-- Center Story Area -->
    <div class="story-stage">
{scenes_html}
    </div>

    <!-- Bottom Footer & Progress -->
    <div id="footer-bar" class="footer-bar clip" data-start="0" data-duration="{total_duration:.2f}" data-track-index="2">
      <div class="progress-track">
        <div id="prog-bar" class="progress-fill"></div>
      </div>
      <div class="cta-text">CHIA SẺ ĐỂ CÙNG NHAU HỌC TIẾNG TRUNG MỖI NGÀY</div>
    </div>
  </div>

  <script>
    const tl = gsap.timeline({{ paused: true }});
{gsap_script}

    window.__timelines = window.__timelines || {{}};
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
'''
    output_html.write_text(template, encoding="utf-8")
    print(f"[✓] Generated composition: {output_html}")


def run_pipeline(input_path: Path, output_mp4: Path, copy_to_desktop: bool = True):
    print("=" * 60)
    print("  Bilingual Story Studio - Video Generator")
    print("=" * 60)
    
    if not input_path.exists():
        print(f"[x] Error: Input file '{input_path}' not found!")
        sys.exit(1)

    print(f"[1/4] Parsing story from: {input_path.name}")
    story = parse_story_file(input_path)
    scenes = story.get("scenes", [])
    print(f"      Title: {story.get('title')}")
    print(f"      Scenes: {len(scenes)}")

    audio_dir = Path("audio")
    audio_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[2/4] Generating Chinese Audio & Calculating Timings...")
    current_time = 0.0
    for idx, sc in enumerate(scenes, 1):
        sc["id"] = idx
        cn_text = sc["cn"]
        audio_file = audio_dir / f"voice_{idx}.mp3"
        print(f"      - Scene {idx}: \"{cn_text[:20]}...\"")
        
        # Download TTS
        download_tts(cn_text, audio_file)
        dur = get_audio_duration(audio_file)
        
        # Scene duration with 0.8s breathing room
        scene_dur = round(dur + 0.8, 2)
        sc["audio_rel"] = f"audio/voice_{idx}.mp3"
        sc["start"] = round(current_time, 2)
        sc["dur"] = scene_dur
        
        # Generate ruby markup
        sc["ruby"] = hanzi_to_ruby(cn_text)
        
        current_time += scene_dur

    total_duration = round(current_time, 2)
    print(f"      Total Video Duration: {total_duration:.2f}s")

    print(f"\n[3/4] Building Dynamic HTML5 Composition...")
    index_html = Path("index.html")
    build_html_composition(story, scenes, total_duration, index_html)

    print(f"\n[4/4] Rendering 1080x1920 30FPS MP4 via HyperFrames Headless Chrome...")
    # DIR is '.', output path is output_mp4
    full_cmd = f'npx hyperframes render . -o "{output_mp4}"'
    print(f"      Executing: {full_cmd}")
    ret = subprocess.run(full_cmd, shell=True)
    
    if ret.returncode != 0:
        print("[x] Error: HyperFrames render failed!")
        sys.exit(ret.returncode)

    print(f"\n[✓] Render Complete: {output_mp4.resolve()}")

    if copy_to_desktop:
        desktop_dir = Path(os.environ.get("USERPROFILE", "C:/Users/User")) / "Desktop"
        if desktop_dir.exists():
            dest = desktop_dir / output_mp4.name
            shutil.copy2(output_mp4, dest)
            print(f"[✓] Copied to Desktop: {dest}")

    # Auto-dispatch to Telegram Video Hub (asynchronous)
    try:
        hub_dir = Path(__file__).resolve().parent.parent / "telegram_video_hub"
        if str(hub_dir.parent) not in sys.path:
            sys.path.insert(0, str(hub_dir.parent))
        from telegram_video_hub import dispatch_video
        video_title = story.get("title", "Song Ngữ Trung - Việt")
        dispatch_video(
            video_path=str(output_mp4.resolve()),
            title=video_title,
            description=f"Video học tiếng Trung qua nhật ký: {video_title}",
            app_name="BilingualStoryStudio",
            tags=["HocTiengTrung", "NhatKyMoiNgay", "Shadowing", "Douyin"]
        )
    except Exception as e:
        print(f"[!] Telegram Hub notice: {e}")

    print("\n" + "=" * 60)
    print("SUCCESS! Video is ready for TikTok / Reels / Shorts.")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Automated Bilingual Story Video Generator")
    parser.add_argument("-i", "--input", default="sample_story.txt", help="Input story file (.txt or .json)")
    parser.add_argument("-o", "--output", default="story_video.mp4", help="Output MP4 file name")
    parser.add_argument("--no-desktop", action="store_true", help="Do not copy output to Desktop")

    args = parser.parse_args()
    input_path = Path(args.input)
    output_mp4 = Path(args.output)
    run_pipeline(input_path, output_mp4, copy_to_desktop=not args.no_desktop)


if __name__ == "__main__":
    main()
