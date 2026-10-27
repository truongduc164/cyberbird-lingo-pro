"""
CLI Runner for Video Automation
Usage:
  python make_video.py --topic "3 Bí Mật Về AI Agent"
  python make_video.py --file "path/to/story.txt"
"""
import sys
import os
import argparse
from pathlib import Path

# Add directory A to path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Fix Windows console UTF-8 encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    os.system("")

from rich.console import Console
from rich.panel import Panel
from video_engine.pipeline import run_video_pipeline

console = Console()

def main():
    parser = argparse.ArgumentParser(description="Antigravity Video Automation Studio")
    parser.add_argument("--topic", type=str, default="3 Bí Mật Về Trí Tuệ Nhân Tạo Năm 2026", help="Chu de video muon tao")
    parser.add_argument("--file", type=str, default="", help="Duong dan toi file .txt chua truyen hoac kich ban")
    parser.add_argument("--lang", type=str, default="vi", help="Ngon ngu: vi, en, zh-CN")
    parser.add_argument("--ratio", type=str, default="9:16", help="Ty le khung hinh: 9:16 (Shorts/TikTok) hoac 16:9 (YouTube)")
    parser.add_argument("--output", type=str, default="", help="Ten file video xuat ra")
    parser.add_argument("--no-open", action="store_true", help="Khong tu dong mo video sau khi render")

    args = parser.parse_args()

    console.print("\n[bold magenta]══════════════════════════════════════════════════════════════════[/bold magenta]")
    console.print("[bold cyan]   🎬 ANTIGRAVITY VIDEO AUTOMATION STUDIO (REA ENGINE) 🎬[/bold cyan]")
    console.print("[bold magenta]══════════════════════════════════════════════════════════════════[/bold magenta]\n")

    is_raw_text = False
    content = args.topic

    if args.file and os.path.exists(args.file):
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
        is_raw_text = True
        console.print(f"[bold green]📖 Da doc noi dung tu file:[/bold green] [cyan]{args.file}[/cyan]")
    else:
        console.print(f"[bold green]💡 Chu de video:[/bold green] [cyan]{content}[/cyan]")

    console.print(f"[dim]• Ngon ngu: {args.lang} | Ty le: {args.ratio}[/dim]\n")

    # Run pipeline
    result = run_video_pipeline(
        input_content=content,
        is_raw_text=is_raw_text,
        lang=args.lang,
        ratio=args.ratio,
        output_name=args.output
    )

    out_file = result["output_path"]

    panel_text = (
        f"[bold white]✔ Video da duoc san xuat thanh cong![/bold white]\n\n"
        f"[cyan]📁 File:[/cyan] [bold yellow]{out_file}[/bold yellow]\n"
        f"[dim]• So phan canh (Scenes):[/dim] {result['scenes_count']}\n"
        f"[dim]• Thoi luong tong:[/dim] {result['duration']} giay\n"
        f"[dim]• Dung luong:[/dim] {result['file_size_mb']} MB\n"
        f"[dim]• Thoi gian render:[/dim] {result['elapsed_seconds']} giay"
    )
    console.print(Panel(panel_text, title="[bold green]THÀNH PHẨM XUẤT XƯỞNG[/bold green]", border_style="green"))

    if not args.no_open and sys.platform == "win32" and os.path.exists(out_file):
        console.print("[dim]Dang mo video tren trinh phat media...[/dim]")
        try:
            os.startfile(out_file)
        except Exception:
            pass

if __name__ == "__main__":
    main()
