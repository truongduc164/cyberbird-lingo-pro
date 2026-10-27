import html
from typing import List, Optional

def escape(text: str) -> str:
    """Escapes HTML special characters for Telegram HTML parse mode."""
    if not text:
        return ""
    return html.escape(str(text))

def format_duration(seconds: float) -> str:
    """Converts seconds into MM:SS format."""
    total_sec = int(round(seconds))
    mins = total_sec // 60
    secs = total_sec % 60
    return f"{mins:02d}:{secs:02d}"

def format_caption(
    app_name: str,
    title: str,
    description: Optional[str] = None,
    duration: Optional[float] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    file_size_mb: Optional[float] = None,
    tags: Optional[List[str]] = None
) -> str:
    """
    Creates a clean, professional HTML formatted caption for Telegram video messages.
    Enforces Telegram's 1024 character limit.
    """
    header = f"🎬 <b>[{escape(app_name)}]</b>\n━━━━━━━━━━━━━━━━━━━━"
    
    title_line = f"📌 <b>{escape(title)}</b>" if title else ""
    
    desc_line = ""
    if description and description.strip():
        desc_line = f"📝 <i>{escape(description.strip())}</i>\n"

    # Technical Specs Block
    specs = []
    if duration:
        specs.append(f"• ⏱️ {format_duration(duration)}")
    if width and height:
        specs.append(f"• 📐 {width}x{height}")
    if file_size_mb:
        specs.append(f"• 📦 {file_size_mb:.1f} MB")
    specs.append("• 🚀 FastStream")

    specs_block = "📊 <b>Thông số:</b> " + " | ".join(specs)

    # Tags block
    tag_str = ""
    if tags:
        clean_tags = []
        for t in tags:
            t = t.strip()
            if not t.startswith("#"):
                t = f"#{t}"
            clean_tags.append(t)
        tag_str = " ".join(clean_tags)

    parts = [header]
    if title_line:
        parts.append(title_line)
    if desc_line:
        parts.append(desc_line)
    parts.append(specs_block)
    if tag_str:
        parts.append(f"🏷️ <code>{escape(tag_str)}</code>")

    full_caption = "\n\n".join(parts)

    # Ensure under 1024 chars (Telegram media caption limit)
    if len(full_caption) > 1020:
        excess = len(full_caption) - 1017
        if desc_line and len(desc_line) > excess + 10:
            truncated_desc = desc_line[:-(excess + 5)] + "..."
            desc_line = f"📝 <i>{escape(truncated_desc)}</i>\n"
            parts[2] = desc_line
            full_caption = "\n\n".join(parts)
        else:
            full_caption = full_caption[:1017] + "..."

    return full_caption
