#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CENTRAL DAILY WATCHDOG — CYBERBIRD LINGO PRO v3.2 (DEAN OPTIMIZE)
=================================================================
AI Pedagogical Curator + 24/7 Cloud Pages Auto-OTA Synchronizer:
  1. CHỈ ĐỌC (100% Read-Only, tốn 0 KB trên VPS) từ Ổ Đĩa Mạng `Z:\\` (`\\\\100.77.193.96\\DeanHub`):
     - `Z:\\_system\\nhat_ky.db` (copy ra thư mục tạm trước khi đọc để Zero-Lock trên VPS)
     - `Z:\\03_Nhat_Ky_Hang_Ngay\\YYYY-MM-DD.md`
     - `Z:\\01_Files_Cuu_Ho\\`
     - Kết hợp `15. REA/ReaKey/server/data/reavault.db` (`entries` + 45 thuật ngữ `glossary`) & `inbox_diary/`.
  2. DÙNG AI BIÊN TẬP SƯ PHẠM (`ai_diary_curator.py` — DeepSeek LLM):
     - TUYỆT ĐỐI KHÔNG BÊ NGUYÊN XI tin nhắn thô, lỗi OCR ('不合拾', '熬分箱'), tên cá nhân hay nhắc việc riêng tư.
     - Tự động tổng kết thành chủ đề bài học (`topic_title`), bản đúc kết sư phạm (`summary`), mẹo ghi nhớ (`learning_tip`),
       từ vựng chọn lọc có từ nhiễu cùng trường nghĩa & hội thoại công xưởng trau chuốt tự nhiên!
  3. Sinh giọng đọc Neural `zh-CN-XiaoxiaoNeural` (`edge-tts`) + Pinyin chuẩn thanh điệu (`pypinyin`).
  4. Tự động đẩy bản cập nhật OTA (`cloud_pages_publisher.py`) lên Link Cố Định Vĩnh Viễn cho MỌI CLIENT:
     👉 https://truongduc164.github.io/cyberbird-lingo/ (không còn phụ thuộc trycloudflare đổi link mỗi ngày!)
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import edge_tts
from pypinyin import Style, pinyin

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))

from ai_diary_curator import curate_day_lesson_with_ai
from cloud_pages_publisher import PERMANENT_PAGES_URL, publish_ota_to_github_pages

DEAN_ROOT = PROJECT_DIR.parent
GAME_DIR = PROJECT_DIR / "cyberbird_lingo"
DAILY_AUDIO_DIR = GAME_DIR / "audio" / "daily"
INBOX_DIARY_DIR = PROJECT_DIR / "inbox_diary"
STATE_FILE = PROJECT_DIR / ".watchdog_state.json"

Z_DRIVE_CANDIDATES = [
    Path(r"Z:\\"),
    Path(r"\\100.77.193.96\DeanHub"),
]

REAVAULT_DB = DEAN_ROOT / "15. REA" / "ReaKey" / "server" / "data" / "reavault.db"
FOLDER_SHARE_DIR = DEAN_ROOT / "19. Folder Share" / "Share"
FOLDER_SHARE_UPLOADS = DEAN_ROOT / "19. Folder Share" / "uploads"

TIMELINE_JSON = GAME_DIR / "daily_timeline.json"
TIMELINE_JS = GAME_DIR / "daily_timeline_data.js"

VOICE_ZH = "zh-CN-XiaoxiaoNeural"
RE_HANZI = re.compile(r"[\u4e00-\u9fff]+")
RE_MENTION = re.compile(r"@[^\s\u2005]+[\s\u2005]*")
RE_URL = re.compile(r"https?://\S+")

BLOCKED_SUBSTRINGS = (
    "memory usage",
    "bilibili",
    "photo,",
    "not downloaded",
    "received edited",
    "88u",
    "58u",
    "娱乐平台",
    "上帝",
    "厌倦",
    "疯了",
    "仙女",
    "少女",
    "接待员",
    "未来的老婆",
    "双向联系",
    "t.me/",
    "joeeir",
    "rppof",
    "ctrl + alt",
    "taskbar",
    "telegravity",
    "telecoder",
    "[vi]",
    "[中]",
)

TRIVIAL_ZH_EXACT = {
    "你好", "您好", "好的", "好", "谢谢", "啊", "哦", "呵呵", "哈哈", "中国人", "十", "快乐", "欢迎", "欢迎，呵呵",
}

# Bộ bài mẫu dự phòng khi hoàn toàn mất mạng và chưa có cache AI
OFFLINE_FALLBACK_PATTERNS: list[dict[str, Any]] = [
    {
        "match": "吸塑模",
        "topic_title": "Kiểm soát khuôn hút nhựa & ngoại quan sản phẩm",
        "vocab": [
            {"vi": "Khuôn Hút Định Hình Nhựa", "en": "Vacuum Forming Mold", "zh": "吸塑模", "dist_zh": "注塑机", "dist_en": "Injection Machine"},
            {"vi": "Cong Vênh Mép", "en": "Warped Edge", "zh": "翘边", "dist_zh": "表面刮伤", "dist_en": "Surface Scratch"},
            {"vi": "Lựa Hàng Lỗi Riêng Ra", "en": "Sort Out Defects", "zh": "挑出来", "dist_zh": "分箱包装", "dist_en": "Split-Box Packing"},
            {"vi": "Hướng Dẫn Thao Tác (SOP)", "en": "Work Instruction (SOP)", "zh": "作业指导书", "dist_zh": "出货计划", "dist_en": "Shipment Plan"},
        ],
        "dialogue": {
            "speaker": "🔍 Kỹ Sư QC Xưởng",
            "q_zh": "这批货发现有翘边现象，请先把不良品挑出来！",
            "q_vi": "Lô hàng này phát hiện bị vênh mép, vui lòng nhặt riêng hàng lỗi ra trước!",
            "correct_zh": "收到，产线正在逐个排查并调整模具温度！",
            "correct_vi": "Đã nhận, chuyền đang rà soát từng sản phẩm và chỉnh lại nhiệt độ khuôn!",
            "wrong_zh": "周末我们一起去公园骑自行车吧。",
            "wrong_vi": "Cuối tuần chúng mình cùng ra công viên đạp xe nhé.",
        },
    }
]


def resolve_z_hub() -> Path | None:
    """Locate Z:\\ or \\\\100.77.193.96\\DeanHub, re-mounting Z: silently if needed."""
    for cand in Z_DRIVE_CANDIDATES:
        try:
            if cand.exists():
                return cand
        except Exception:
            pass
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["net", "use", "Z:", r"\\100.77.193.96\DeanHub", "dean007", "/user:WORKGROUP\\dean", "/persistent:yes"],
                capture_output=True,
                timeout=6,
            )
            if Path(r"Z:\\").exists():
                return Path(r"Z:\\")
        except Exception:
            pass
    return None


def to_pinyin(zh_text: str) -> str:
    parts = pinyin(zh_text, style=Style.TONE, errors="default")
    raw = " ".join(item[0] for item in parts if item and item[0].strip())
    return re.sub(r"\s+([，。！？、；：,.!?])", r"\1", raw).strip()


def audio_hash_filename(zh_text: str, prefix: str = "d") -> str:
    digest = hashlib.md5(zh_text.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}_{digest}.mp3"


async def synthesize_missing_audio(tasks: list[tuple[str, Path]]) -> int:
    DAILY_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    created = 0
    sem = asyncio.Semaphore(4)
    unique_map: dict[Path, str] = {}
    for text, out_path in tasks:
        unique_map[out_path] = text

    async def _worker(text: str, out_path: Path) -> None:
        nonlocal created
        if out_path.exists() and out_path.stat().st_size > 800:
            return
        async with sem:
            try:
                comm = edge_tts.Communicate(text, VOICE_ZH, rate="-5%")
                await comm.save(str(out_path))
                created += 1
            except Exception as exc:
                print(f"  [WARN] TTS lỗi '{text[:20]}': {exc}")

    await asyncio.gather(*[_worker(t, p) for p, t in unique_map.items()])
    return created


def is_noise_text(txt: str) -> bool:
    low = txt.lower().strip()
    if not low:
        return True
    if RE_URL.search(low):
        return True
    if any(b in low for b in BLOCKED_SUBSTRINGS):
        return True
    return False


def is_clean_pair(vi_text: str, zh_text: str) -> bool:
    vi_s = vi_text.strip()
    zh_s = zh_text.strip()
    if not vi_s or not zh_s:
        return False
    if len(zh_s) < 2 or len(zh_s) > 25 or len(vi_s) < 2 or len(vi_s) > 75:
        return False
    if "\n" in zh_s or "\n" in vi_s:
        return False
    if not RE_HANZI.search(zh_s):
        return False
    if vi_s == zh_s or len(RE_HANZI.findall(vi_s)) > 1:
        return False
    if is_noise_text(vi_s + " " + zh_s):
        return False
    if zh_s in TRIVIAL_ZH_EXACT:
        return False
    return True


def make_day_bucket() -> dict[str, Any]:
    return {
        "raw_blobs": [],
        "clean_pairs": [],
        "raw_zh_candidates": [],
    }


def extract_zh_lines_from_text(content: str, starred: bool, origin: str, bucket: dict[str, Any]) -> None:
    """Collect candidate Chinese phrases/sentences for AI Pedagogical Editor (never dumped raw to UI)."""
    for raw_line in content.splitlines():
        line = RE_MENTION.sub("", raw_line).strip()
        line = line.strip(" \t\r\n•*-—|")
        if not line or is_noise_text(line):
            continue
        if re.match(r"^\d{4}[/-]\d{1,2}[/-]\d{1,2}", line):
            continue
        if "|" in line and "⚡" not in line:
            parts = [p.strip() for p in line.split("|", 1)]
            if len(parts) == 2 and is_clean_pair(parts[0], parts[1]):
                bucket["clean_pairs"].append((parts[0], parts[1], origin))
                continue
            if len(parts) == 2 and is_clean_pair(parts[1], parts[0]):
                bucket["clean_pairs"].append((parts[1], parts[0], origin))
                continue

        hanzi_count = sum(len(m) for m in RE_HANZI.findall(line))
        if hanzi_count >= 2 and 2 <= len(line) <= 90:
            clean_zh = line.strip(" ，。、；：,.\\")
            if clean_zh not in TRIVIAL_ZH_EXACT:
                bucket["raw_zh_candidates"].append((clean_zh, starred, origin))


def collect_z_drive_hub(days_map: dict[str, dict[str, Any]]) -> Path | None:
    """Read daily diary & SQLite nhat_ky.db from Z:\\ (100% Read-Only, zero personal reminders copied)."""
    z_root = resolve_z_hub()
    if not z_root:
        print("  [WARN] Tạm thời chưa thấy ổ Z:\\ (\\\\100.77.193.96\\DeanHub) — dùng dữ liệu cục bộ.")
        return None

    z_db = z_root / "_system" / "nhat_ky.db"
    if z_db.exists():
        try:
            with tempfile.TemporaryDirectory() as tmp_str:
                tmp_dir = Path(tmp_str)
                for fn in ("nhat_ky.db", "nhat_ky.db-wal", "nhat_ky.db-shm"):
                    src = z_root / "_system" / fn
                    if src.exists():
                        shutil.copy2(src, tmp_dir / fn)

                con = sqlite3.connect(tmp_dir / "nhat_ky.db")
                con.row_factory = sqlite3.Row
                rows = con.execute(
                    "SELECT id, created_at, category, content, starred FROM entries ORDER BY id ASC"
                ).fetchall()
                for r in rows:
                    dt = str(r["created_at"] or "")[:10]
                    if not re.match(r"^\d{4}-\d{2}-\d{2}$", dt):
                        continue
                    cat = str(r["category"] or "")
                    content = str(r["content"] or "").strip()
                    starred = bool(r["starred"])
                    # Skip personal reminders without Chinese content
                    if cat == "reminder" and not RE_HANZI.search(content):
                        continue
                    if content and cat in ("clipboard_text", "note", "rescue_file", "reminder"):
                        bucket = days_map.setdefault(dt, make_day_bucket())
                        bucket["raw_blobs"].append(content)
                        extract_zh_lines_from_text(content, starred, "Ổ Z:", bucket)
                con.close()
        except Exception as exc:
            print(f"  [WARN] Lỗi đọc bản sao Z:\\_system\\nhat_ky.db: {exc}")

    md_dir = z_root / "03_Nhat_Ky_Hang_Ngay"
    if md_dir.exists():
        for md_file in sorted(md_dir.glob("*.md"))[-14:]:
            m = re.match(r"^(\d{4}-\d{2}-\d{2})", md_file.stem)
            if not m:
                continue
            dt = m.group(1)
            bucket = days_map.setdefault(dt, make_day_bucket())
            try:
                md_txt = md_file.read_text(encoding="utf-8", errors="replace")
                bucket["raw_blobs"].append(md_txt)
                extract_zh_lines_from_text(md_txt, False, "Nhật ký MD", bucket)
            except Exception:
                pass

    rescue_root = z_root / "01_Files_Cuu_Ho"
    if rescue_root.exists():
        for f in rescue_root.rglob("*"):
            if not f.is_file() or f.name.startswith("HUONG_DAN"):
                continue
            if f.suffix.lower() in (".txt", ".md", ".csv"):
                dt = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")
                bucket = days_map.setdefault(dt, make_day_bucket())
                try:
                    txt = f.read_text(encoding="utf-8", errors="replace")
                    bucket["raw_blobs"].append(txt)
                    extract_zh_lines_from_text(txt, True, f.stem, bucket)
                except Exception:
                    pass

    return z_root


def collect_reavault_and_local(days_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    glossary_items: list[dict[str, Any]] = []

    if REAVAULT_DB.exists():
        try:
            con = sqlite3.connect(f"file:{REAVAULT_DB}?mode=ro", uri=True)
            con.row_factory = sqlite3.Row

            rows = con.execute("SELECT id, vi, zh, en, updated_at FROM glossary ORDER BY id ASC").fetchall()
            for r in rows:
                vi_raw = str(r["vi"] or "").strip()
                zh_raw = str(r["zh"] or "").strip()
                en_raw = str(r["en"] or "").strip()
                dt = str(r["updated_at"] or datetime.now().strftime("%Y-%m-%d"))[:10]
                if vi_raw and zh_raw:
                    glossary_items.append({
                        "date": dt,
                        "vi": vi_raw[:1].upper() + vi_raw[1:],
                        "en": en_raw[:1].upper() + en_raw[1:] if en_raw else "Technical Term",
                        "zh": zh_raw,
                    })

            rows_e = con.execute(
                "SELECT ts, app, source_text, source_lang, target_text, target_lang FROM entries ORDER BY id ASC"
            ).fetchall()
            for r in rows_e:
                dt = str(r["ts"] or "")[:10]
                if not re.match(r"^\d{4}-\d{2}-\d{2}$", dt):
                    continue
                bucket = days_map.setdefault(dt, make_day_bucket())
                app_name = str(r["app"] or "").strip()
                src = str(r["source_text"] or "").strip()
                tgt = str(r["target_text"] or "").strip()
                slang = str(r["source_lang"] or "").lower()
                tlang = str(r["target_lang"] or "").lower()
                bucket["raw_blobs"].append(f"{src} {tgt}")

                vi_txt, zh_txt = "", ""
                if slang.startswith("vi") and tlang.startswith("zh"):
                    vi_txt, zh_txt = src, tgt
                elif slang.startswith("zh") and tlang.startswith("vi"):
                    zh_txt, vi_txt = src, tgt

                if vi_txt and zh_txt and is_clean_pair(vi_txt, zh_txt):
                    bucket["clean_pairs"].append((vi_txt, zh_txt, app_name or "ReaKey"))

            con.close()
        except Exception as exc:
            print(f"  [WARN] Lỗi đọc reavault.db: {exc}")

    INBOX_DIARY_DIR.mkdir(parents=True, exist_ok=True)
    for sdir in (FOLDER_SHARE_DIR, FOLDER_SHARE_UPLOADS, INBOX_DIARY_DIR):
        if not sdir.exists():
            continue
        for f in sdir.iterdir():
            if not f.is_file() or f.name in ("HUONG_DAN_NHAT_KY.txt", "test-write.txt"):
                continue
            dt = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")
            bucket = days_map.setdefault(dt, make_day_bucket())
            if f.suffix.lower() in (".txt", ".md", ".csv"):
                try:
                    txt = f.read_text(encoding="utf-8", errors="replace")
                    bucket["raw_blobs"].append(txt)
                    extract_zh_lines_from_text(txt, False, f.stem, bucket)
                except Exception:
                    pass

    return glossary_items


def build_timeline_payload(force_ai: bool = False) -> tuple[dict[str, Any], list[tuple[str, Path]], Path | None]:
    days_map: dict[str, dict[str, Any]] = {}
    z_root = collect_z_drive_hub(days_map)
    glossary_items = collect_reavault_and_local(days_map)

    today_str = datetime.now().strftime("%Y-%m-%d")
    if not days_map:
        days_map[today_str] = make_day_bucket()

    glossary_by_date: dict[str, list[dict[str, Any]]] = {}
    for g in glossary_items:
        glossary_by_date.setdefault(g["date"], []).append(g)
        days_map.setdefault(g["date"], make_day_bucket())

    tts_tasks: list[tuple[str, Path]] = []
    timeline_days: list[dict[str, Any]] = []

    for dt in sorted(days_map.keys(), reverse=True):
        bucket = days_map[dt]
        vocab_list: list[dict[str, Any]] = []
        dialogue_list: list[dict[str, Any]] = []
        seen_zh: set[str] = set()

        # 1. AI Pedagogical Editor synthesizes & polishes the day's raw diary!
        ai_lesson = curate_day_lesson_with_ai(
            date_str=dt,
            raw_blobs=bucket["raw_blobs"],
            clean_pairs=bucket["clean_pairs"],
            raw_zh_candidates=bucket["raw_zh_candidates"],
            force_refresh=force_ai,
        )

        topic_title = "Thực chiến Tiếng Trung Công Xưởng"
        summary_str = ""
        learning_tip = ""

        if ai_lesson:
            topic_title = ai_lesson.get("topic_title") or topic_title
            summary_str = ai_lesson.get("summary") or ""
            learning_tip = ai_lesson.get("learning_tip") or ""

            for v in ai_lesson.get("vocab", []):
                zh = v["zh"]
                if zh in seen_zh:
                    continue
                seen_zh.add(zh)
                fname = audio_hash_filename(zh, "dv")
                tts_tasks.append((zh, DAILY_AUDIO_DIR / fname))
                vocab_list.append({
                    "cat": "daily",
                    "date": dt,
                    "vi": v["vi"],
                    "en": v["en"],
                    "zh": zh,
                    "pinyin": to_pinyin(zh),
                    "dist_en": v["dist_en"],
                    "dist_zh": v["dist_zh"],
                    "dist_pinyin": to_pinyin(v["dist_zh"]),
                    "audio": f"audio/daily/{fname}",
                    "source": "✨ AI Biên Tập Sư Phạm",
                })

            for idx_d, dlg in enumerate(ai_lesson.get("dialogues", [])):
                q_fname = audio_hash_filename(dlg["q_zh"], "dq")
                a_fname = audio_hash_filename(dlg["correct_zh"], "da")
                tts_tasks.append((dlg["q_zh"], DAILY_AUDIO_DIR / q_fname))
                tts_tasks.append((dlg["correct_zh"], DAILY_AUDIO_DIR / a_fname))
                dialogue_list.append({
                    "id": f"daily_{dt}_ai_{idx_d + 1}",
                    "cat": "daily",
                    "date": dt,
                    "speaker": dlg["speaker"],
                    "q_zh": dlg["q_zh"],
                    "q_pinyin": to_pinyin(dlg["q_zh"]),
                    "q_vi": dlg["q_vi"],
                    "q_audio": f"audio/daily/{q_fname}",
                    "correct_zh": dlg["correct_zh"],
                    "correct_pinyin": to_pinyin(dlg["correct_zh"]),
                    "correct_vi": dlg["correct_vi"],
                    "wrong_zh": dlg["wrong_zh"],
                    "wrong_pinyin": to_pinyin(dlg["wrong_zh"]),
                    "wrong_vi": dlg["wrong_vi"],
                    "a_audio": f"audio/daily/{a_fname}",
                })
        else:
            # Clean curated fallback if offline and uncached (never dumps raw OCR!)
            joined_blob = "\n".join(bucket["raw_blobs"])
            for idx_p, pat in enumerate(OFFLINE_FALLBACK_PATTERNS):
                if pat["match"] in joined_blob:
                    topic_title = pat["topic_title"]
                    for v in pat["vocab"]:
                        zh = v["zh"]
                        if zh in seen_zh:
                            continue
                        seen_zh.add(zh)
                        fname = audio_hash_filename(zh, "dv")
                        tts_tasks.append((zh, DAILY_AUDIO_DIR / fname))
                        vocab_list.append({
                            "cat": "daily",
                            "date": dt,
                            "vi": v["vi"],
                            "en": v["en"],
                            "zh": zh,
                            "pinyin": to_pinyin(zh),
                            "dist_en": v["dist_en"],
                            "dist_zh": v["dist_zh"],
                            "dist_pinyin": to_pinyin(v["dist_zh"]),
                            "audio": f"audio/daily/{fname}",
                            "source": "Bài học chuẩn hóa",
                        })
                    dlg = pat["dialogue"]
                    q_fname = audio_hash_filename(dlg["q_zh"], "dq")
                    a_fname = audio_hash_filename(dlg["correct_zh"], "da")
                    tts_tasks.append((dlg["q_zh"], DAILY_AUDIO_DIR / q_fname))
                    tts_tasks.append((dlg["correct_zh"], DAILY_AUDIO_DIR / a_fname))
                    dialogue_list.append({
                        "id": f"daily_{dt}_fb_{idx_p + 1}",
                        "cat": "daily",
                        "date": dt,
                        "speaker": dlg["speaker"],
                        "q_zh": dlg["q_zh"],
                        "q_pinyin": to_pinyin(dlg["q_zh"]),
                        "q_vi": dlg["q_vi"],
                        "q_audio": f"audio/daily/{q_fname}",
                        "correct_zh": dlg["correct_zh"],
                        "correct_pinyin": to_pinyin(dlg["correct_zh"]),
                        "correct_vi": dlg["correct_vi"],
                        "wrong_zh": dlg["wrong_zh"],
                        "wrong_pinyin": to_pinyin(dlg["wrong_zh"]),
                        "wrong_vi": dlg["wrong_vi"],
                        "a_audio": f"audio/daily/{a_fname}",
                    })

        # 2. Merge clean technical Automation Glossary dictionary terms if present for that date
        day_gloss = glossary_by_date.get(dt, [])
        if day_gloss:
            for idx_g, g in enumerate(day_gloss):
                zh = g["zh"]
                if zh in seen_zh:
                    continue
                seen_zh.add(zh)
                other = day_gloss[(idx_g + 7) % len(day_gloss)] if len(day_gloss) > 1 else None
                dist_en = other["en"] if other else "Switchboard"
                dist_zh = other["zh"] if other else "配电柜"
                fname = audio_hash_filename(zh, "dg")
                tts_tasks.append((zh, DAILY_AUDIO_DIR / fname))
                vocab_list.append({
                    "cat": "daily",
                    "subcat": "automation_glossary",
                    "date": dt,
                    "vi": g["vi"],
                    "en": g["en"],
                    "zh": zh,
                    "pinyin": to_pinyin(zh),
                    "dist_en": dist_en,
                    "dist_zh": dist_zh,
                    "dist_pinyin": to_pinyin(dist_zh),
                    "audio": f"audio/daily/{fname}",
                    "source": "⚡ Từ điển Tủ điện & TĐH",
                })

        if not vocab_list and not dialogue_list:
            continue

        dt_obj = datetime.strptime(dt, "%Y-%m-%d")
        short_label = f"Hôm nay ({dt_obj.strftime('%d/%m')})" if dt == today_str else dt_obj.strftime("Ngày %d/%m/%Y")
        if not summary_str:
            summary_str = f"Bài học thực chiến ({len(vocab_list)} từ vựng & {len(dialogue_list)} tình huống giao tiếp chuẩn hóa)."

        timeline_days.append({
            "date": dt,
            "label": short_label,
            "topic_title": topic_title,
            "summary": summary_str,
            "learning_tip": learning_tip,
            "ai_curated": bool(ai_lesson),
            "vocab_count": len(vocab_list),
            "dialogue_count": len(dialogue_list),
            "vocab": vocab_list,
            "dialogues": dialogue_list,
        })

    payload = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "permanent_url": PERMANENT_PAGES_URL,
        "curation_engine": "DeepSeek Pedagogical AI v3.2",
        "total_days": len(timeline_days),
        "total_vocab": sum(d["vocab_count"] for d in timeline_days),
        "total_dialogues": sum(d["dialogue_count"] for d in timeline_days),
        "days": timeline_days,
    }
    return payload, tts_tasks, z_root


def compute_sources_fingerprint() -> str:
    parts: list[str] = ["v3.2-ai-curator"]
    z_root = resolve_z_hub()
    if z_root:
        for fn in ("nhat_ky.db", "nhat_ky.db-wal"):
            p = z_root / "_system" / fn
            if p.exists():
                st = p.stat()
                parts.append(f"zdb_{fn}:{st.st_mtime_ns}:{st.st_size}")
        md_dir = z_root / "03_Nhat_Ky_Hang_Ngay"
        if md_dir.exists():
            for f in sorted(md_dir.glob("*.md"))[-5:]:
                st = f.stat()
                parts.append(f"zmd_{f.name}:{st.st_mtime_ns}:{st.st_size}")

    if REAVAULT_DB.exists():
        st = REAVAULT_DB.stat()
        parts.append(f"reavault:{st.st_mtime_ns}:{st.st_size}")
    for d in (FOLDER_SHARE_DIR, FOLDER_SHARE_UPLOADS, INBOX_DIARY_DIR):
        if d.exists():
            for f in sorted(d.iterdir()):
                if f.is_file():
                    fst = f.stat()
                    parts.append(f"{f.name}:{fst.st_mtime_ns}:{fst.st_size}")
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def run_sync(force: bool = False, force_ai: bool = False, publish_cloud: bool = True) -> bool:
    fp = compute_sources_fingerprint()
    if not force and not force_ai and STATE_FILE.exists() and TIMELINE_JS.exists():
        try:
            prev = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            if prev.get("fingerprint") == fp:
                return False
        except Exception:
            pass

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Watchdog v3.2 đang đọc nhật ký & gọi AI biên tập bài học...")
    payload, tts_tasks, z_root = build_timeline_payload(force_ai=force_ai)
    new_mp3 = asyncio.run(synthesize_missing_audio(tts_tasks))

    json_text = json.dumps(payload, ensure_ascii=False, indent=2)
    TIMELINE_JSON.write_text(json_text, encoding="utf-8")
    TIMELINE_JS.write_text(
        "// Auto-generated by central_daily_watchdog.py v3.2 (AI Pedagogical Curator) — DO NOT EDIT MANUALLY\n"
        f"window.CYBERBIRD_DAILY_TIMELINE = {json_text};\n",
        encoding="utf-8",
    )

    cloud_ok = False
    if publish_cloud:
        try:
            cloud_ok, _ = publish_ota_to_github_pages(
                f"AI lesson {payload['days'][0]['date'] if payload['days'] else 'sync'} ({payload['total_vocab']}w/{payload['total_dialogues']}d)"
            )
        except Exception as exc:
            print(f"  [WARN] Lỗi đẩy OTA GitHub Pages: {exc}")

    STATE_FILE.write_text(
        json.dumps(
            {
                "fingerprint": fp,
                "updated_at": payload["updated_at"],
                "permanent_url": PERMANENT_PAGES_URL,
                "cloud_published": cloud_ok,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        f"  ✅ Đã hoàn tất bài học AI ({payload['total_days']} ngày | "
        f"{payload['total_vocab']} từ vựng | {payload['total_dialogues']} hội thoại | "
        f"+{new_mp3} MP3 mới | Cloud OTA: {'OK' if cloud_ok else 'Local'})!"
    )
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Central Daily Batch Digest v3.2.1 (End-of-Workday AI Curator + Cloud OTA)")
    parser.add_argument("--scheduled", action="store_true", help="Chạy chốt sổ định kỳ 1 lần (chỉ gọi AI & push nếu có dữ liệu mới) rồi tự thoát ngay")
    parser.add_argument("--once", action="store_true", help="Chạy kiểm tra & cập nhật ngay 1 lần rồi tự thoát")
    parser.add_argument("--force-ai", action="store_true", help="Bắt buộc gọi lại AI biên tập lại từ đầu")
    parser.add_argument("--no-cloud", action="store_true", help="Chỉ cập nhật cục bộ, tạm chưa push GitHub Pages")
    args = parser.parse_args()

    # Scheduled mode: smart fingerprint check -> if nothing new on Z:\ or ReaKey, exits in 0.05s!
    if args.scheduled:
        changed = run_sync(force=False, force_ai=args.force_ai, publish_cloud=not args.no_cloud)
        if not changed:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Không có nhật ký mới kể từ lần chốt sổ trước — tự thoát nhẹ nhàng.")
    else:
        run_sync(force=True, force_ai=args.force_ai, publish_cloud=not args.no_cloud)


if __name__ == "__main__":
    main()
