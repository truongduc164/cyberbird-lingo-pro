"""
VibeRadar - Terminal CLI Runner
Scans GitHub, Hacker News, Hugging Face, Dev.to & Synthesizes Spontaneous Ideas.
"""
import sys
import os

# Fix Windows console UTF-8 encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    os.system("") # Enable ANSI escape sequences on Windows

from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from core.github_scanner import GitHubScanner
from core.hn_scanner import HackerNewsScanner
from core.hf_scanner import HuggingFaceScanner
from core.devto_scanner import DevToScanner
from core.vibe_engine import VibeEngine
from core.storage import Storage
from core.report_generator import ReportGenerator

console = Console(force_terminal=True, legacy_windows=False)

def run_scan():
    console.print("\n[bold magenta]==================================================================[/bold magenta]")
    console.print("[bold cyan]      * VIBERADAR — BỘ QUÉT XU HƯỚNG & PHÁT SINH Ý TƯỞNG *[/bold cyan]")
    console.print("[bold magenta]==================================================================[/bold magenta]\n")

    storage = Storage()
    gh = GitHubScanner()
    hn = HackerNewsScanner()
    hf = HuggingFaceScanner()
    devto = DevToScanner()
    engine = VibeEngine()
    reporter = ReportGenerator()

    all_items = []

    with console.status("[bold green]Dang quet xu huong cong nghe toan cau...", spinner="dots"):
        # 1. GitHub
        console.print("[dim]-> Quet GitHub Trending & Rising repos...[/dim]")
        gh_items = gh.fetch_trending()
        all_items.extend(gh_items)

        # 2. Hacker News
        console.print("[dim]-> Quet Hacker News (Show HN & Top Tech)...[/dim]")
        hn_items = hn.fetch_all()
        all_items.extend(hn_items)

        # 3. Hugging Face
        console.print("[dim]-> Quet Hugging Face Trending AI...[/dim]")
        hf_items = hf.fetch_all()
        all_items.extend(hf_items)

        # 4. Dev.to
        console.print("[dim]-> Quet Dev.to Tech Articles...[/dim]")
        dev_items = devto.fetch_top_articles()
        all_items.extend(dev_items)

        # Analysis & Vibe Idea Sparks
        keywords = engine.extract_keywords(all_items)
        sparks = engine.generate_sparks(all_items, count=6)

        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_items": len(all_items),
            "keywords": keywords,
            "sparks": sparks,
            "items": all_items
        }

        # Cache & Report
        storage.save_cache(data)
        reporter.generate_markdown(data)

    console.print(f"\n[bold green]✔ Da quet thanh cong {len(all_items)} xu huong moi nhat![/bold green]")
    console.print(f"[bold yellow]Hot Keywords:[/bold yellow] " + " ".join([f"[cyan]#{kw}[/cyan]" for kw in keywords[:10]]))

    # Render Table of Trending Items
    table = Table(title="TOP TRENDING PICKS HOM NAY", show_header=True, header_style="bold magenta")
    table.add_column("Nguon", style="dim", width=16)
    table.add_column("Ten Du An / Bai Viet", style="bold cyan", min_width=25)
    table.add_column("Ngon ngu/Loai", style="green", width=14)
    table.add_column("Tuong tac", style="yellow", justify="right", width=12)

    for item in all_items[:12]:
        table.add_row(
            item.get("source", ""),
            item.get("title", "")[:32],
            item.get("language", "")[:12],
            f"* {item.get('stars', '0')}"
        )
    console.print(table)

    # Render Vibe Sparks
    console.print("\n[bold yellow]==================================================================[/bold yellow]")
    console.print("[bold yellow]       * TIA SANG Y TUONG BAT CHOT NAY RA (VIBE SPARKS) *[/bold yellow]")
    console.print("[bold yellow]==================================================================[/bold yellow]\n")

    for i, s in enumerate(sparks, 1):
        panel_content = (
            f"[bold white]{s['desc']}[/bold white]\n\n"
            f"[dim]• Cam hung tu:[/dim] [cyan]{s['inspiration_source']}[/cyan]\n"
            f"[dim]• Do kho:[/dim] [green]{s['difficulty']}[/green]  |  "
            f"[dim]• Stack de xuat:[/dim] [yellow]{s['tech_stack']}[/yellow]  |  "
            f"[dim]• Vibe Score:[/dim] [bold red]{s['vibe_score']}/100[/bold red]"
        )
        console.print(Panel(panel_content, title=f"[bold cyan]Idea #{i}: {s['title']}[/bold cyan]", border_style="cyan"))

    console.print("\n[bold green]Bao cao chi tiet da duoc luu tai:[/bold green] [cyan]reports/vibe_digest_latest.md[/cyan]")
    console.print("[bold blue]Ban co the chay Dashboard truc quan bang lenh:[/bold blue] [bold white]python run_web.py[/bold white]\n")

if __name__ == "__main__":
    run_scan()
