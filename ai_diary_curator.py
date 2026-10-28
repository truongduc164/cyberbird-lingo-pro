#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANTIGRAVITY-QUOTA DIARY CURATOR CACHE — CYBERBIRD LINGO PRO v3.3 (DEAN OPTIMIZE)
================================================================================
Chế độ $0 API Trả Phí — Dùng 100% Quota của chính Agent Antigravity!
- Tuyệt đối KHÔNG tự động gọi bất kỳ API trả phí bên ngoài nào (DeepSeek/OpenAI...).
- Đọc bài học sư phạm đã được chính Agent Antigravity biên tập và lưu trong `.ai_curated_days_cache.json`.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parent
AI_CACHE_FILE = PROJECT_DIR / ".ai_curated_days_cache.json"

PROMPT_VERSION = "v3.2-pedagogical-pro-2"

RE_SENSITIVE_OR_NOISE = re.compile(
    r"(https?://\S+|sk-[A-Za-z0-9_-]{12,}|\b\d{6,}:[A-Za-z0-9_-]{20,}\b|"
    r"memory usage|ctrl\s*\+\s*alt|telegravity|telecoder)",
    re.I,
)


def load_ai_cache() -> dict[str, Any]:
    if AI_CACHE_FILE.exists():
        try:
            return json.loads(AI_CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_ai_cache(cache: dict[str, Any]) -> None:
    AI_CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def prepare_sanitized_day_digest_input(
    raw_blobs: list[str],
    clean_pairs: list[tuple[str, str, str]],
    raw_zh_candidates: list[tuple[str, bool, str]],
) -> str:
    """Deduplicate and pre-clean raw diary notes so Antigravity Agent can curate them cleanly."""
    seen_lines: set[str] = set()
    collected: list[str] = []

    for vi, zh, _ in clean_pairs:
        entry = f"[Cặp từ tra cứu] {zh} = {vi}"
        if entry not in seen_lines:
            seen_lines.add(entry)
            collected.append(entry)

    for zh_cand, starred, _ in raw_zh_candidates:
        prefix = "[Ghim quan trọng] " if starred else "[Câu/Từ thực tế] "
        entry = f"{prefix}{zh_cand}"
        if entry not in seen_lines:
            seen_lines.add(entry)
            collected.append(entry)

    for blob in raw_blobs:
        for raw_line in blob.splitlines():
            line = raw_line.strip()
            if not line or len(line) < 3 or len(line) > 220:
                continue
            if RE_SENSITIVE_OR_NOISE.search(line):
                continue
            if not re.search(r"[\u4e00-\u9fff]", line):
                continue
            norm = re.sub(r"\s+", " ", line)
            if norm not in seen_lines:
                seen_lines.add(norm)
                collected.append(f"[Ngữ cảnh nhật ký] {norm}")
            if sum(len(x) for x in collected) > 4200:
                break
        if sum(len(x) for x in collected) > 4200:
            break

    return "\n".join(collected)[:4500]


def compute_day_input_hash(date_str: str, digest_input: str) -> str:
    return hashlib.sha256(f"{PROMPT_VERSION}|{date_str}|{digest_input}".encode("utf-8")).hexdigest()


def curate_day_lesson_with_ai(
    date_str: str,
    raw_blobs: list[str],
    clean_pairs: list[tuple[str, str, str]],
    raw_zh_candidates: list[tuple[str, bool, str]],
    force_refresh: bool = False,
) -> dict[str, Any] | None:
    """
    Zero-Paid-API reader: returns the lesson curated by Antigravity Agent in `.ai_curated_days_cache.json`.
    Never calls any external paid LLM API!
    """
    cache = load_ai_cache()
    if date_str in cache and isinstance(cache[date_str], dict):
        lesson = cache[date_str].get("lesson")
        if isinstance(lesson, dict) and (lesson.get("vocab") or lesson.get("dialogues")):
            return lesson
    return None
