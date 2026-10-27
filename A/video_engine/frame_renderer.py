"""
Frame & Typography Motion Renderer
Generates dynamic visual frames for video scenes (Ken Burns motion, elegant text cards).
"""
import math
import os
from pathlib import Path
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont

# Theme Color Gradients: (Top Color, Bottom Color, Accent Color)
THEMES = {
    "cyber_blue": ((10, 15, 30), (0, 70, 120), (0, 242, 254)),
    "neon_purple": ((18, 10, 32), (80, 20, 120), (180, 100, 255)),
    "sunset_orange": ((25, 12, 15), (120, 40, 20), (255, 150, 50)),
    "emerald_green": ((8, 22, 18), (15, 80, 55), (0, 230, 130)),
    "deep_ruby": ((20, 8, 12), (100, 15, 35), (255, 60, 100))
}

class FrameRenderer:
    def __init__(self, width: int = 1080, height: int = 1920, fps: int = 24):
        self.width = width
        self.height = height
        self.fps = fps
        self.font_path = "C:/Windows/Fonts/arial.ttf"
        if not os.path.exists(self.font_path):
            self.font_path = "C:/Windows/Fonts/tahoma.ttf"

    def _create_gradient(self, top_color: Tuple[int, int, int], bot_color: Tuple[int, int, int]) -> Image.Image:
        """Create a smooth vertical gradient image"""
        img = Image.new("RGB", (self.width, self.height))
        draw = ImageDraw.Draw(img)
        for y in range(self.height):
            ratio = y / float(self.height)
            r = int(top_color[0] * (1 - ratio) + bot_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bot_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bot_color[2] * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        return img

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = font.getbbox(test_line)
            w = bbox[2] - bbox[0]
            if w <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
        return lines

    def render_scene_base(self, title: str, text: str, theme_name: str = "cyber_blue") -> Image.Image:
        """
        Render a static base frame for a scene with beautiful card and typography.
        """
        top_c, bot_c, accent_c = THEMES.get(theme_name, THEMES["cyber_blue"])
        base_img = self._create_gradient(top_c, bot_c)
        draw = ImageDraw.Draw(base_img, "RGBA")

        # Fonts
        title_font = ImageFont.truetype(self.font_path, 36)
        text_font = ImageFont.truetype(self.font_path, 54)

        # 1. Category Badge Top Pill
        badge_text = f"✨ {title.upper()}"
        bbox = title_font.getbbox(badge_text)
        badge_w = bbox[2] - bbox[0] + 40
        badge_h = bbox[3] - bbox[1] + 24
        badge_x = (self.width - badge_w) // 2
        badge_y = int(self.height * 0.22)

        # Badge background
        draw.rounded_rectangle(
            [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
            radius=20,
            fill=(accent_c[0], accent_c[1], accent_c[2], 40),
            outline=(accent_c[0], accent_c[1], accent_c[2], 180),
            width=2
        )
        draw.text((badge_x + 20, badge_y + 10), badge_text, font=title_font, fill=accent_c)

        # 2. Centered Frosted Text Card
        card_margin = 60
        card_width = self.width - (card_margin * 2)
        lines = self._wrap_text(text, text_font, card_width - 80)
        
        line_height = 76
        text_block_h = len(lines) * line_height
        card_h = text_block_h + 100
        card_y = (self.height - card_h) // 2

        # Draw card container
        draw.rounded_rectangle(
            [card_margin, card_y, card_margin + card_width, card_y + card_h],
            radius=24,
            fill=(10, 14, 24, 180),
            outline=(255, 255, 255, 30),
            width=2
        )

        # Render lines of text with shadow
        curr_y = card_y + 50
        for line in lines:
            line_bbox = text_font.getbbox(line)
            line_w = line_bbox[2] - line_bbox[0]
            line_x = (self.width - line_w) // 2

            # Shadow
            draw.text((line_x + 2, curr_y + 3), line, font=text_font, fill=(0, 0, 0, 160))
            # Main Text
            draw.text((line_x, curr_y), line, font=text_font, fill=(255, 255, 255, 255))
            curr_y += line_height

        return base_img

    def generate_scene_frames(self, title: str, text: str, duration: float, theme: str, motion: str, output_dir: Path) -> List[str]:
        """
        Generate sequence of frame images with smooth Ken Burns zoom effect.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        total_frames = max(1, int(duration * self.fps))

        # Render base image slightly oversized for smooth cropping
        base_img = self.render_scene_base(title, text, theme)
        base_w, base_h = base_img.size

        frame_paths = []
        for i in range(total_frames):
            progress = i / float(total_frames) if total_frames > 1 else 0

            # Scale factor for Ken Burns (1.00 to 1.05)
            if motion == "zoom_in":
                scale = 1.0 + (0.05 * progress)
            else: # zoom_out
                scale = 1.05 - (0.05 * progress)

            new_w = int(base_w * scale)
            new_h = int(base_h * scale)

            # Resize and crop back to original dimensions
            scaled = base_img.resize((new_w, new_h), Image.Resampling.BILINEAR)
            crop_x = (new_w - self.width) // 2
            crop_y = (new_h - self.height) // 2
            cropped = scaled.crop((crop_x, crop_y, crop_x + self.width, crop_y + self.height))

            # Bottom progress bar
            draw = ImageDraw.Draw(cropped)
            bar_y = self.height - 12
            bar_w = int(self.width * progress)
            _, _, accent_c = THEMES.get(theme, THEMES["cyber_blue"])
            draw.rectangle([0, bar_y, bar_w, self.height], fill=accent_c)

            frame_file = output_dir / f"frame_{i:04d}.jpg"
            cropped.save(frame_file, "JPEG", quality=88)
            frame_paths.append(str(frame_file))

        return frame_paths
