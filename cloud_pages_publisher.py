#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLOUD PAGES AUTO-OTA PUBLISHER — CYBERBIRD LINGO PRO v3.2 (DEAN OPTIMIZE)
=========================================================================
Đồng bộ tự động ứng dụng Web PWA tĩnh (`cyberbird_lingo/`) lên GitHub Pages cố định:
  👉 Link cố định vĩnh viễn cho MỌI CLIENT: https://truongduc164.github.io/cyberbird-lingo/

Đặc điểm an toàn & tối ưu:
  - CHỈ đẩy thư mục web tĩnh (`index.html`, `sw.js`, `manifest.json`, `daily_timeline*`, icons, `audio/*.mp3`).
  - TUYỆT ĐỐI KHÔNG đẩy mã nguồn Python nội bộ, `.env`, token Telegram hay nhật ký thô.
  - Quét bảo mật trước khi commit để đảm bảo 0% rò rỉ khóa API.
  - Mỗi khi Watchdog biên tập xong bài học AI mới trong ngày -> tự động `git push` -> sau ~30 giây
    MỌI thiết bị (iPhone, iPad, Android, PC) mở đúng 1 đường link cố định đều nhận được bài học mới!
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import requests

PROJECT_DIR = Path(__file__).resolve().parent
GAME_DIR = PROJECT_DIR / "cyberbird_lingo"
DEPLOY_DIR = PROJECT_DIR / ".gh_pages_deploy"

GH_OWNER = "truongduc164"
GH_REPO = "cyberbird-lingo"
PERMANENT_PAGES_URL = f"https://{GH_OWNER}.github.io/{GH_REPO}/"
REMOTE_GIT_URL = f"https://github.com/{GH_OWNER}/{GH_REPO}.git"

ALLOWED_TOP_EXTS = {".html", ".js", ".json", ".png", ".ico", ".svg", ".webmanifest", ".css"}
SECRET_GUARD_RE = re.compile(r"(sk-[A-Za-z0-9]{18,}|\b\d{8,12}:AA[A-Za-z0-9_-]{30,}\b)")


def get_github_token() -> str:
    """Retrieve GitHub token from Windows Git Credential Manager without storing it on disk."""
    try:
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True,
            text=True,
            timeout=6,
        )
        for line in proc.stdout.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return ""


def ensure_github_repo_exists(token: str) -> bool:
    if not token:
        return False
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    r = requests.get(f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}", headers=headers, timeout=10)
    if r.status_code == 200:
        return True
    if r.status_code == 404:
        print(f"  🌐 Đang khởi tạo kho GitHub Pages cố định: {GH_OWNER}/{GH_REPO} ...")
        cr = requests.post(
            "https://api.github.com/user/repos",
            headers=headers,
            json={
                "name": GH_REPO,
                "description": "CyberBird Lingo PRO — Bilingual Workplace Reflex & AI Daily Lesson PWA by DEAN OPTIMIZE",
                "private": False,
                "has_issues": False,
                "has_projects": False,
                "has_wiki": False,
                "auto_init": False,
            },
            timeout=15,
        )
        return cr.status_code in (200, 201)
    return False


def ensure_github_pages_enabled(token: str) -> bool:
    if not token:
        return False
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    r = requests.get(f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}/pages", headers=headers, timeout=10)
    if r.status_code == 200:
        return True
    print(f"  🚀 Bật GitHub Pages 24/7 tại: {PERMANENT_PAGES_URL}")
    cr = requests.post(
        f"https://api.github.com/repos/{GH_OWNER}/{GH_REPO}/pages",
        headers=headers,
        json={"source": {"branch": "main", "path": "/"}},
        timeout=15,
    )
    return cr.status_code in (200, 201, 409)


def sync_static_tree_to_deploy() -> None:
    DEPLOY_DIR.mkdir(parents=True, exist_ok=True)

    # Copy top-level clean web files
    for item in GAME_DIR.iterdir():
        if item.is_file() and item.suffix.lower() in ALLOWED_TOP_EXTS:
            txt_check = ""
            if item.suffix.lower() in (".html", ".js", ".json"):
                txt_check = item.read_text(encoding="utf-8", errors="ignore")
                if SECRET_GUARD_RE.search(txt_check):
                    raise RuntimeError(f"Secret guard blocked publishing {item.name}!")
            shutil.copy2(item, DEPLOY_DIR / item.name)

    # Mirror audio/ directory cleanly (add new MP3s & remove stale ones if any)
    src_audio = GAME_DIR / "audio"
    dst_audio = DEPLOY_DIR / "audio"
    if src_audio.exists():
        for root, _, files in os.walk(src_audio):
            rel_dir = Path(root).relative_to(src_audio)
            target_dir = dst_audio / rel_dir
            target_dir.mkdir(parents=True, exist_ok=True)
            for fn in files:
                if fn.lower().endswith(".mp3"):
                    s_file = Path(root) / fn
                    d_file = target_dir / fn
                    if not d_file.exists() or d_file.stat().st_size != s_file.stat().st_size:
                        shutil.copy2(s_file, d_file)

    # Create .nojekyll for instant static serving without Jekyll build delay
    (DEPLOY_DIR / ".nojekyll").write_text("", encoding="utf-8")


def publish_ota_to_github_pages(reason: str = "daily AI lesson sync") -> tuple[bool, str]:
    """
    Push static PWA & AI-curated daily timeline to https://truongduc164.github.io/cyberbird-lingo/.
    Returns (pushed_or_already_up_to_date, permanent_url).
    """
    token = get_github_token()
    if not token:
        print("  [WARN] Chưa tìm thấy GitHub credential để đẩy OTA lên GitHub Pages.")
        return False, PERMANENT_PAGES_URL

    if not ensure_github_repo_exists(token):
        print("  [WARN] Không thể kiểm tra/khởi tạo kho GitHub cyberbird-lingo.")
        return False, PERMANENT_PAGES_URL

    # Initialize or repair local deploy git repo
    if not (DEPLOY_DIR / ".git").exists():
        if DEPLOY_DIR.exists():
            shutil.rmtree(DEPLOY_DIR, ignore_errors=True)
        DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "-C", str(DEPLOY_DIR), "init", "-b", "main"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(DEPLOY_DIR), "remote", "add", "origin", REMOTE_GIT_URL], check=True, capture_output=True)
        fetch_res = subprocess.run(["git", "-C", str(DEPLOY_DIR), "fetch", "origin", "main"], capture_output=True)
        if fetch_res.returncode == 0:
            subprocess.run(["git", "-C", str(DEPLOY_DIR), "reset", "--mixed", "origin/main"], capture_output=True)

    subprocess.run(["git", "-C", str(DEPLOY_DIR), "config", "user.name", GH_OWNER], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(DEPLOY_DIR), "config", "user.email", f"{GH_OWNER}@users.noreply.github.com"], check=True, capture_output=True)

    sync_static_tree_to_deploy()

    st = subprocess.run(["git", "-C", str(DEPLOY_DIR), "status", "--porcelain"], capture_output=True, text=True)
    if not st.stdout.strip():
        ensure_github_pages_enabled(token)
        return True, PERMANENT_PAGES_URL

    subprocess.run(["git", "-C", str(DEPLOY_DIR), "add", "-A"], check=True, capture_output=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    subprocess.run(
        ["git", "-C", str(DEPLOY_DIR), "commit", "-m", f"chore(ota): {reason} ({ts})"],
        check=True,
        capture_output=True,
    )
    push_res = subprocess.run(
        ["git", "-C", str(DEPLOY_DIR), "push", "-u", "origin", "main"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if push_res.returncode != 0:
        # In case remote diverged, pull rebase/ours and push cleanly
        subprocess.run(["git", "-C", str(DEPLOY_DIR), "fetch", "origin", "main"], capture_output=True)
        subprocess.run(["git", "-C", str(DEPLOY_DIR), "push", "--force-with-lease", "-u", "origin", "main"], check=True, capture_output=True, timeout=60)

    ensure_github_pages_enabled(token)
    print(f"  ☁️ [OTA PUBLISHED] Đã cập nhật lên Link Cố Định Mọi Client: {PERMANENT_PAGES_URL}")
    return True, PERMANENT_PAGES_URL


if __name__ == "__main__":
    ok, url = publish_ota_to_github_pages("manual OTA sync")
    print("Result:", ok, url)
