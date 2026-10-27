"""
FFmpeg Video Compositor
Stitches scenes, aligns voiceover audio, adds optional BGM and outputs final MP4.
"""
import os
import subprocess
from pathlib import Path
from typing import List, Optional
import imageio_ffmpeg

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

class VideoCompositor:
    def __init__(self, fps: int = 24):
        self.fps = fps

    def compile_scene_video(self, frames_dir: Path, audio_path: Path, output_scene_mp4: Path) -> bool:
        """
        Assemble image sequence and audio track into a single scene MP4.
        """
        cmd = [
            FFMPEG_EXE, "-y",
            "-framerate", str(self.fps),
            "-i", str(frames_dir / "frame_%04d.jpg"),
            "-i", str(audio_path),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-shortest",
            str(output_scene_mp4)
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, errors="replace")
        if res.returncode != 0:
            print(f"Error compiling scene {output_scene_mp4}: {res.stderr}")
            return False
        return True

    def concat_scenes(self, scene_mp4s: List[Path], output_mp4: Path) -> bool:
        """
        Concatenate multiple scene videos using FFmpeg concat demuxer.
        """
        if not scene_mp4s:
            return False

        list_file = output_mp4.parent / "concat_list.txt"
        with open(list_file, "w", encoding="utf-8") as f:
            for s in scene_mp4s:
                # Format for FFmpeg concat: file 'path/to/scene.mp4'
                safe_path = str(s.resolve()).replace("\\", "/")
                f.write(f"file '{safe_path}'\n")

        cmd = [
            FFMPEG_EXE, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
            "-c", "copy",
            str(output_mp4)
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, errors="replace")
        
        # Cleanup list file
        if list_file.exists():
            list_file.unlink(missing_ok=True)

        if res.returncode != 0:
            print(f"Error concatenating scenes: {res.stderr}")
            return False
        return True

    def mix_bgm(self, input_video: Path, bgm_path: Path, output_video: Path, bgm_volume: float = 0.12) -> bool:
        """
        Overlay background music onto video at low volume (e.g. 12-15%).
        """
        if not bgm_path.exists():
            # If no BGM, simply copy or rename
            return False

        cmd = [
            FFMPEG_EXE, "-y",
            "-i", str(input_video),
            "-stream_loop", "-1",
            "-i", str(bgm_path),
            "-filter_complex", f"[1:a]volume={bgm_volume}[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            str(output_video)
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, errors="replace")
        return res.returncode == 0
