"""
Configuration for VibeRadar
"""
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
STATIC_DIR = BASE_DIR / "web" / "static"

# Web Server Settings
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8765

# Scraping Limits
GITHUB_TRENDING_LIMIT = 15
GITHUB_RISING_LIMIT = 10
HACKERNEWS_LIMIT = 15
HUGGINGFACE_LIMIT = 10
DEVTO_LIMIT = 10

# Search & Trend Tags
WATCH_TOPICS = [
    "ai",
    "agent",
    "llm",
    "automation",
    "developer-tools",
    "productivity",
    "cli",
    "fastapi",
    "python",
    "bot",
    "crawler",
    "open-source"
]

# Cache duration (seconds) - 1 hour by default
CACHE_TTL = 3600

# User Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 VibeRadar/1.0"
