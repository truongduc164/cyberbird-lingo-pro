"""
Audio TTS Engine (Google TTS + Duration Extractor)
100% Free, Zero API Key Required.
"""
import os
import re
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Tuple
import imageio_ffmpeg

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

class AudioTTSEngine:
    def __init__(self, lang: str = "vi"):
        self.lang = lang
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

    def generate_speech(self, text: str, output_path: str) -> float:
        """
        Synthesize text to MP3 file and return its duration in seconds.
        """
        clean_text = text.strip()
        if not clean_text:
            clean_text = "..."

        encoded_text = urllib.parse.quote(clean_text)
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl={self.lang}&client=tw-ob&q={encoded_text}"
        
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req, timeout=12) as response:
            audio_bytes = response.read()

        with open(output_path, "wb") as f:
            f.write(audio_bytes)

        duration = self.get_duration(output_path)
        # Minimum safe duration: 1.5s
        return max(1.5, duration)

    def get_duration(self, audio_path: str) -> float:
        """
        Extract audio duration using ffmpeg.
        """
        try:
            cmd = [FFMPEG_EXE, "-i", str(audio_path)]
            proc = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors="replace")
            # Look for Duration: 00:00:05.12
            match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", proc.stderr)
            if match:
                hours = float(match.group(1))
                minutes = float(match.group(2))
                seconds = float(match.group(3))
                return hours * 3600 + minutes * 60 + seconds
        except Exception as e:
            print(f"Error parsing duration: {e}")
        
        # Fallback approximation based on byte size for MP3 ~32kbps
        file_size = os.path.getsize(audio_path)
        return max(1.5, file_size / 4000.0)
