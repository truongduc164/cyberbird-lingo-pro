#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANTIGRAVITY QUOTA WATCHDOG HELPER — CYBERBIRD LINGO PRO v3.3 (DEAN OPTIMIZE)
============================================================================
Công cụ cầu nối giúp chính Agent Antigravity (dùng 100% Quota Antigravity, $0 API ngoài!)
thực hiện vai trò Biên Tập Viên Sư Phạm hằng ngày lúc 17:30:

1. `python antigravity_watchdog_helper.py --check`
   -> Đọc Ổ Z:\\ (100% Read-Only) & ReaKey, đối chiếu `.ai_curated_days_cache.json`.
   -> Nếu không có dữ liệu tiếng Trung mới: in `STATUS: UP_TO_DATE` (Agent dừng ngay, tốn ~0 quota!).
   -> Nếu có ngày mới / dữ liệu tăng ca mới: in `STATUS: NEEDS_CURATION` kèm dữ liệu thô đã lọc sạch
      để chính Agent Antigravity biên tập thành bài học sư phạm!

2. `python antigravity_watchdog_helper.py --save-day YYYY-MM-DD --input-hash <HASH> --lesson-file <PATH>`
   -> Lưu bài học do Agent Antigravity vừa biên tập vào `.ai_curated_days_cache.json`,
      sau đó tự chạy `central_daily_watchdog.py --once` để tạo MP3 Xiaoxiao miễn phí (`edge-tts`)
      và đẩy OTA lên https://truongduc164.github.io/cyberbird-lingo/ !
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))

from ai_diary_curator import (
    compute_day_input_hash,
    load_ai_cache,
    prepare_sanitized_day_digest_input,
    save_ai_cache,
)
from central_daily_watchdog import collect_reavault_and_local, collect_z_drive_hub, run_sync


def cmd_check() -> None:
    days_map = {}
    collect_z_drive_hub(days_map)
    collect_reavault_and_local(days_map)
    cache = load_ai_cache()

    pending = []
    for dt in sorted(days_map.keys(), reverse=True)[:7]:
        b = days_map[dt]
        digest_in = prepare_sanitized_day_digest_input(
            b["raw_blobs"], b["clean_pairs"], b["raw_zh_candidates"]
        )
        if not digest_in.strip():
            continue
        in_hash = compute_day_input_hash(dt, digest_in)
        cached = cache.get(dt)
        if not isinstance(cached, dict) or cached.get("input_hash") != in_hash:
            pending.append({
                "date": dt,
                "input_hash": in_hash,
                "raw_digest": digest_in,
            })

    if not pending:
        print("STATUS: UP_TO_DATE")
        return

    print(f"STATUS: NEEDS_CURATION ({len(pending)} day(s))")
    print(json.dumps(pending, ensure_ascii=False, indent=2))


def cmd_save(date_str: str, input_hash: str, lesson_file: Path, publish: bool) -> None:
    lesson_raw = json.loads(lesson_file.read_text(encoding="utf-8"))
    lesson_raw["ai_curated"] = True
    cache = load_ai_cache()
    cache[date_str] = {
        "input_hash": input_hash,
        "updated_by_model": "antigravity-agent-quota",
        "lesson": lesson_raw,
    }
    save_ai_cache(cache)
    print(f"✅ Saved Antigravity-curated lesson for {date_str} into .ai_curated_days_cache.json")
    if publish:
        run_sync(force=True, publish_cloud=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--save-day", type=str, default="")
    parser.add_argument("--input-hash", type=str, default="")
    parser.add_argument("--lesson-file", type=str, default="")
    parser.add_argument("--no-publish", action="store_true")
    args = parser.parse_args()

    if args.check:
        cmd_check()
    elif args.save_day and args.lesson_file:
        cmd_save(args.save_day, args.input_hash, Path(args.lesson_file), publish=not args.no_publish)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
