#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CENTRAL DAILY WATCHDOG — CYBERBIRD LINGO PRO v3.0 (DEAN OPTIMIZE)
=================================================================
Silent Background Watchdog & Daily Diary Timeline Synchronizer ("Very Silent"):
  1. Quét tự động nhật ký dịch thuật & giao tiếp WeChat/Zalo/Chrome hằng ngày từ:
     - ReaKey SQLite Vault (`15. REA/ReaKey/server/data/reavault.db` -> bảng `entries` & `glossary`)
     - Ổ đĩa chia sẻ Tailscale (`19. Folder Share/Share` & `uploads`)
     - Hộp thư nhật ký/nhắc nhở/cảnh báo (`23. CyberBird-Lingo-Game/inbox_diary/`)
  2. Lọc nhiễu thông minh, khử trùng lặp, tự sinh phiên âm Pinyin chuẩn dấu thanh (`pypinyin`),
     tự ghép đáp án nhiễu hợp lý và tổng hợp giọng đọc Neural `zh-CN-XiaoxiaoNeural` (`edge-tts`)
     lưu offline tại `cyberbird_lingo/audio/daily/`.
  3. Tóm tắt Nhật ký Ngày (Daily Diary Digest) và xuất thẳng vào:
     - `cyberbird_lingo/daily_timeline.json` (cho Live PWA tự nạp không cần reload)
     - `cyberbird_lingo/daily_timeline_data.js` (cho Offline APK / file:// 100% không lỗi CORS)

Chế độ chạy:
  - Đồng bộ ngay 1 lần:   python central_daily_watchdog.py --once
  - Chạy ngầm liên tục:   pythonw central_daily_watchdog.py --daemon --interval 300
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import sqlite3
import sys
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
DEAN_ROOT = PROJECT_DIR.parent
GAME_DIR = PROJECT_DIR / "cyberbird_lingo"
DAILY_AUDIO_DIR = GAME_DIR / "audio" / "daily"
INBOX_DIARY_DIR = PROJECT_DIR / "inbox_diary"
STATE_FILE = PROJECT_DIR / ".watchdog_state.json"

REAVAULT_DB = DEAN_ROOT / "15. REA" / "ReaKey" / "server" / "data" / "reavault.db"
FOLDER_SHARE_DIR = DEAN_ROOT / "19. Folder Share" / "Share"
FOLDER_SHARE_UPLOADS = DEAN_ROOT / "19. Folder Share" / "uploads"
MONITOR_PC_DIR = DEAN_ROOT / "04. Monitor PC"

TIMELINE_JSON = GAME_DIR / "daily_timeline.json"
TIMELINE_JS = GAME_DIR / "daily_timeline_data.js"

VOICE_ZH = "zh-CN-XiaoxiaoNeural"

# Clean Chinese character regex
RE_HANZI = re.compile(r"[\u4e00-\u9fff]+")

# Filter out noisy test phrases / system strings / rude test prompts
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
    "ctrl + alt",
    "taskbar",
    "telegravity",
    "telecoder",
    "[vi]",
    "[中]",
    "ứa gan",
    "rủ cả phê",
    "banj ",
    "ban ơi",
    "luýt",
    " lut",
    "zhuding",
    "tưởng mình là ai",
    "nghĩ mình là ai",
    "biết tôi là ai",
    "có vấn đề",
    "lại là bạn",
    "bạn lại vậy",
    "đang làm gì đó",
    "bạn là gì",
    "bạn là ai",
    "kỳ lạ",
    "gửi nhầm",
    "haha",
    "hehe",
    "cơm bữa",
    "mọi ngày",
)

# High-value curated extractions from real factory/WeChat patterns when detected in raw logs
CURATED_REAL_FACTORY_PATTERNS: list[dict[str, Any]] = [
    {
        "match": "作业指导书",
        "vocab": [
            {"vi": "Hướng Dẫn Thao Tác (SOP)", "en": "Work Instruction (SOP)", "zh": "作业指导书"},
            {"vi": "Lắp Vỏ Nhựa ABS", "en": "Assemble ABS Shell", "zh": "装ABS壳"},
            {"vi": "Hàng Mẫu Kinh Doanh", "en": "Sales Sample", "zh": "销样"},
            {"vi": "In & Phát Xuống Xưởng", "en": "Print & Distribute", "zh": "打印下发"},
        ],
        "dialogue": {
            "speaker": "📋 Quản Lý Kỹ Thuật (WeChat)",
            "q_zh": "BTN-8-11装ABS壳和装彩盒的作业指导书更新了，请帮打印下发！",
            "q_vi": "SOP lắp vỏ ABS & đóng hộp màu mã BTN-8-11 đã cập nhật, nhờ in phát xuống xưởng!",
            "correct_zh": "收到，我马上打印并发给产线组长。",
            "correct_vi": "Đã nhận, tôi in ngay và phát cho tổ trưởng chuyền.",
            "wrong_zh": "我今天中午想吃牛肉面。",
            "wrong_vi": "Trưa nay tôi muốn ăn mì bò.",
        },
        "tag": "Cập nhật SOP vỏ ABS & hộp màu BTN-8-11",
    },
    {
        "match": "漏彩盒",
        "vocab": [
            {"vi": "Gia Công Kiểm Lại", "en": "Rework & Inspect", "zh": "返工检查"},
            {"vi": "Sót Tem Hộp Màu", "en": "Missing Color-Box Sticker", "zh": "漏彩盒贴纸"},
            {"vi": "Kiểm Tra Toàn Bộ 100%", "en": "100% Full Inspection", "zh": "全检"},
            {"vi": "FQC Kiểm Xác Suất", "en": "FQC Spot Check", "zh": "FQC抽查"},
        ],
        "dialogue": {
            "speaker": "🔍 Phó Tổng Tiêu (WeChat QC)",
            "q_zh": "7071出日本单安排全检一次，检查漏彩盒贴纸的问题！",
            "q_vi": "Đơn 7071 xuất Nhật sắp xếp kiểm 100% một lượt, kiểm tra lỗi sót tem hộp màu!",
            "correct_zh": "明白，马上安排产线返工全检，FQC再抽查！",
            "correct_vi": "Rõ, sắp xếp chuyền kiểm lại 100% ngay, FQC rút kiểm lại!",
            "wrong_zh": "这双运动鞋穿起来很舒服。",
            "wrong_vi": "Đôi giày thể thao này đi rất êm chân.",
        },
        "tag": "FQC toàn kiểm đơn Nhật 7071 (lỗi sót tem hộp màu)",
    },
    {
        "match": "小批量试产",
        "vocab": [
            {"vi": "Sản Xuất Thử Lô Nhỏ", "en": "Small-Batch Pilot Run", "zh": "小批量试产"},
            {"vi": "Theo Dõi Bất Thường", "en": "Track Abnormalities", "zh": "追踪异常"},
            {"vi": "In - Hút - Cắt Định Hình", "en": "Print, Vacuum Form & Trim", "zh": "印吸切成型"},
            {"vi": "Kế Hoạch Khắc Phục (CAP)", "en": "Corrective Action Plan", "zh": "改善对策"},
        ],
        "dialogue": {
            "speaker": "🏭 Kỹ Sư Dự Án SMI-16",
            "q_zh": "SMI-16各环节小批量试产的时间和异常记录好了吗？",
            "q_vi": "Thời gian và bất thường chạy thử lô nhỏ mã SMI-16 các khâu đã ghi nhận xong chưa?",
            "correct_zh": "记录好了，印吸切成型的数据都在报告里。",
            "correct_vi": "Ghi xong rồi, dữ liệu in-hút-cắt định hình đều nằm trong báo cáo.",
            "wrong_zh": "电影院的爆米花卖完了。",
            "wrong_vi": "Bắp rang bơ ở rạp chiếu phim bán hết rồi.",
        },
        "tag": "Theo dõi chạy thử lô nhỏ SMI-16 (in-hút-cắt định hình)",
    },
    {
        "match": "SP-165",
        "vocab": [
            {"vi": "Điểm Cần Lưu Ý", "en": "Key Points to Note", "zh": "需要注意的点"},
            {"vi": "Tem Niên Hạn Sử Dụng", "en": "Service-Life Label", "zh": "年限标"},
        ],
        "dialogue": {
            "speaker": "👷 Đồng Nghiệp Kỹ Thuật (Zalo)",
            "q_zh": "请问SP-165生产时有哪些需要注意的点？",
            "q_vi": "Xin hỏi mã SP-165 khi sản xuất có những điểm gì cần lưu ý?",
            "correct_zh": "要特别注意贴准年限标，不能漏贴或贴歪。",
            "correct_vi": "Phải đặc biệt chú ý dán chuẩn tem niên hạn, không sót hoặc lệch.",
            "wrong_zh": "图书馆周日不对外开放。",
            "wrong_vi": "Thư viện Chủ nhật không mở cửa đón khách.",
        },
        "tag": "Lưu ý kỹ thuật mã SP-165 & tem niên hạn",
    },
    {
        "match": "租房住",
        "vocab": [
            {"vi": "Thuê Nhà Ở Riêng", "en": "Rent an Apartment", "zh": "租房住"},
            {"vi": "Ở Ký Túc Xá", "en": "Live in Dormitory", "zh": "住宿舍"},
            {"vi": "Chế Độ Phúc Lợi", "en": "Welfare & Benefits", "zh": "福利待遇"},
            {"vi": "Nghỉ Việc (Từ Chức)", "en": "Resign", "zh": "辞职"},
        ],
        "dialogue": {
            "speaker": "💬 Bạn Cũ Trung Quốc (WeChat)",
            "q_zh": "新公司加班多吗？你现在住宿舍还是租房住？",
            "q_vi": "Công ty mới tăng ca nhiều không? Giờ bạn ở ký túc xá hay thuê trọ?",
            "correct_zh": "看订单情况，我是自己在外面租房住的。",
            "correct_vi": "Tùy theo đơn hàng thôi, mình tự thuê nhà ở bên ngoài.",
            "wrong_zh": "请把空调温度调高两度。",
            "wrong_vi": "Làm ơn tăng nhiệt độ máy lạnh lên 2 độ.",
        },
        "tag": "Trò chuyện WeChat hỏi thăm công việc, phúc lợi & thuê trọ",
    },
    {
        "match": "质量部门",
        "vocab": [
            {"vi": "Bộ Phận Chất Lượng (QC)", "en": "Quality Department", "zh": "质量部门"},
            {"vi": "Kế Hoạch Xuất Hàng", "en": "Shipment Schedule", "zh": "出货计划"},
            {"vi": "Gia Hạn / Trễ Tiến Độ", "en": "Delay / Postpone", "zh": "延期"},
            {"vi": "Thì Ra Là Vậy", "en": "So That's How It Is", "zh": "原来是这样"},
        ],
        "dialogue": {
            "speaker": "🤝 Đối Tác Trung Quốc (WeChat)",
            "q_zh": "你们工厂在越南哪个位置？你在哪个部门工作？",
            "q_vi": "Nhà máy các bạn ở đâu tại Việt Nam? Bạn làm ở bộ phận nào?",
            "correct_zh": "我们在工业区，我目前在质量部门负责品检。",
            "correct_vi": "Chúng tôi ở khu công nghiệp, tôi đang phụ trách QC ở bộ phận chất lượng.",
            "wrong_zh": "今天下午超市西瓜打折。",
            "wrong_vi": "Chiều nay siêu thị giảm giá dưa hấu.",
        },
        "tag": "Giới thiệu nhà máy Việt Nam, bộ phận chất lượng & kế hoạch xuất hàng",
    },
]

FALLBACK_DISTRACTORS = [
    ("Bàn Họp", "Meeting Table", "会议桌"),
    ("Cốc Nước", "Water Cup", "水杯"),
    ("Máy In", "Printer", "打印机"),
    (" Kho Hàng", "Warehouse", "仓库"),
    ("Xe Nâng", "Forklift", "叉车"),
    ("Thước Cặp", "Caliper", "卡尺"),
    ("Găng Tay", "Gloves", "手套"),
    ("Băng Keo", "Tape", "胶带"),
]


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

    await asyncio.gather(*[_worker(t, p) for t, p in tasks])
    return created


def is_clean_pair(vi_text: str, zh_text: str) -> bool:
    vi_s = vi_text.strip()
    zh_s = zh_text.strip()
    if not vi_s or not zh_s:
        return False
    if len(zh_s) < 2 or len(zh_s) > 22 or len(vi_s) < 2 or len(vi_s) > 65:
        return False
    if "\n" in zh_s or "\n" in vi_s:
        return False
    if not RE_HANZI.search(zh_s):
        return False
    # Ensure vi_text is not identical Chinese
    if vi_s == zh_s or len(RE_HANZI.findall(vi_s)) > 1:
        return False
    combined_low = (vi_s + " " + zh_s).lower()
    if any(b in combined_low for b in BLOCKED_SUBSTRINGS):
        return False
    return True


def collect_reavault_data() -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    """Read daily entries + technical glossary from ReaKey's reavault.db."""
    days_map: dict[str, dict[str, Any]] = {}
    glossary_items: list[dict[str, Any]] = []

    if not REAVAULT_DB.exists():
        return days_map, glossary_items

    con = sqlite3.connect(f"file:{REAVAULT_DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row

    # 1. Read technical glossary (45 industrial electrical & factory automation terms)
    try:
        rows = con.execute("SELECT id, vi, zh, en, updated_at FROM glossary ORDER BY id ASC").fetchall()
        for r in rows:
            vi_raw = str(r["vi"] or "").strip()
            zh_raw = str(r["zh"] or "").strip()
            en_raw = str(r["en"] or "").strip()
            dt = str(r["updated_at"] or datetime.now().strftime("%Y-%m-%d"))[:10]
            if vi_raw and zh_raw:
                vi_title = vi_raw[:1].upper() + vi_raw[1:]
                en_title = en_raw[:1].upper() + en_raw[1:] if en_raw else "Technical Term"
                glossary_items.append({
                    "date": dt,
                    "vi": vi_title,
                    "en": en_title,
                    "zh": zh_raw,
                })
    except Exception as exc:
        print(f"  [WARN] Không đọc được bảng glossary: {exc}")

    # 2. Read daily entries
    try:
        rows = con.execute(
            "SELECT id, ts, app, source_text, source_lang, target_text, target_lang "
            "FROM entries ORDER BY id ASC"
        ).fetchall()
        for r in rows:
            dt = str(r["ts"] or "")[:10]
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", dt):
                continue
            bucket = days_map.setdefault(dt, {
                "raw_blobs": [],
                "clean_pairs": [],
                "apps": set(),
                "share_notes": [],
            })
            app_name = str(r["app"] or "").strip()
            if app_name:
                bucket["apps"].add(app_name.lower())

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
                bucket["clean_pairs"].append((vi_txt, zh_txt, app_name))
    except Exception as exc:
        print(f"  [WARN] Không đọc được bảng entries: {exc}")

    con.close()
    return days_map, glossary_items


def collect_share_and_inbox_notes(days_map: dict[str, dict[str, Any]]) -> None:
    """Scan Tailscale Share folder, uploads, and local inbox_diary/ for daily notes/alerts/clipboard."""
    INBOX_DIARY_DIR.mkdir(parents=True, exist_ok=True)
    readme_inbox = INBOX_DIARY_DIR / "HUONG_DAN_NHAT_KY.txt"
    if not readme_inbox.exists():
        readme_inbox.write_text(
            "Thả bất kỳ file ghi chú (.txt, .md), nhắc nhở hoặc câu tiếng Trung - Việt theo định dạng:\n"
            "Tiếng Việt | Tiếng Trung\n"
            "Ví dụ:\n"
            "Kiểm tra ngoại quan mũ | 检查头盔外观\n"
            "Watchdog sẽ tự động đọc ngầm, tạo giọng đọc Xiaoxiao và đưa lên Timeline của ngày hôm đó!\n",
            encoding="utf-8",
        )

    scan_dirs = [FOLDER_SHARE_DIR, FOLDER_SHARE_UPLOADS, INBOX_DIARY_DIR]
    for sdir in scan_dirs:
        if not sdir.exists():
            continue
        for f in sdir.iterdir():
            if not f.is_file() or f.name in ("HUONG_DAN_NHAT_KY.txt", "test-write.txt"):
                continue
            dt = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")
            bucket = days_map.setdefault(dt, {
                "raw_blobs": [],
                "clean_pairs": [],
                "apps": set(),
                "share_notes": [],
            })
            if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
                bucket["share_notes"].append(f"📸 Ảnh chia sẻ/clipboard ({f.name})")
            elif f.suffix.lower() in (".txt", ".md", ".log", ".csv"):
                try:
                    content = f.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                bucket["share_notes"].append(f"📝 Ghi chú ({f.stem})")
                bucket["raw_blobs"].append(content)
                for line in content.splitlines():
                    if "|" in line:
                        parts = [p.strip() for p in line.split("|", 1)]
                        if len(parts) == 2 and is_clean_pair(parts[0], parts[1]):
                            bucket["clean_pairs"].append((parts[0], parts[1], "share_note"))


def build_timeline_payload() -> tuple[dict[str, Any], list[tuple[str, Path]]]:
    days_map, glossary_items = collect_reavault_data()
    collect_share_and_inbox_notes(days_map)

    today_str = datetime.now().strftime("%Y-%m-%d")
    if not days_map:
        days_map[today_str] = {"raw_blobs": [], "clean_pairs": [], "apps": set(), "share_notes": []}

    # Group glossary items by updated date
    glossary_by_date: dict[str, list[dict[str, Any]]] = {}
    for g in glossary_items:
        glossary_by_date.setdefault(g["date"], []).append(g)
        days_map.setdefault(g["date"], {"raw_blobs": [], "clean_pairs": [], "apps": set(), "share_notes": []})

    tts_tasks: list[tuple[str, Path]] = []
    timeline_days: list[dict[str, Any]] = []

    for dt in sorted(days_map.keys(), reverse=True):
        bucket = days_map[dt]
        joined_blob = "\n".join(bucket["raw_blobs"])
        summary_tags: list[str] = []
        vocab_list: list[dict[str, Any]] = []
        dialogue_list: list[dict[str, Any]] = []
        seen_zh: set[str] = set()

        # 1. Match curated high-signal workplace patterns from that day's logs
        for idx_p, pat in enumerate(CURATED_REAL_FACTORY_PATTERNS):
            if pat["match"] in joined_blob:
                summary_tags.append(pat["tag"])
                for v in pat["vocab"]:
                    zh = v["zh"]
                    if zh in seen_zh:
                        continue
                    seen_zh.add(zh)
                    dist = FALLBACK_DISTRACTORS[len(vocab_list) % len(FALLBACK_DISTRACTORS)]
                    fname = audio_hash_filename(zh, "dv")
                    tts_tasks.append((zh, DAILY_AUDIO_DIR / fname))
                    vocab_list.append({
                        "cat": "daily",
                        "date": dt,
                        "vi": v["vi"],
                        "en": v["en"],
                        "zh": zh,
                        "pinyin": to_pinyin(zh),
                        "dist_en": dist[1],
                        "dist_zh": dist[2],
                        "dist_pinyin": to_pinyin(dist[2]),
                        "audio": f"audio/daily/{fname}",
                        "source": "Nhật ký Xưởng / WeChat",
                    })
                dlg = pat["dialogue"]
                q_fname = audio_hash_filename(dlg["q_zh"], "dq")
                a_fname = audio_hash_filename(dlg["correct_zh"], "da")
                tts_tasks.append((dlg["q_zh"], DAILY_AUDIO_DIR / q_fname))
                tts_tasks.append((dlg["correct_zh"], DAILY_AUDIO_DIR / a_fname))
                dialogue_list.append({
                    "id": f"daily_{dt}_{idx_p + 1}",
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

        # 2. Add clean conversational / daily lookup phrases from entries & share notes
        seen_vi: set[str] = {v["vi"].lower() for v in vocab_list}
        for vi_txt, zh_txt, app_src in bucket["clean_pairs"]:
            zh_clean = zh_txt.strip(" ，。！？、；：,.!?\\()（）")
            vi_clean_raw = vi_txt.strip(" ，。！？、；：,.!?\\()（）")
            if not zh_clean or not vi_clean_raw:
                continue
            if zh_clean in seen_zh or vi_clean_raw.lower() in seen_vi:
                continue
            # Keep crisp 2..7 char words/phrases as flight portal vocabulary
            if 2 <= len(zh_clean) <= 7 and RE_HANZI.search(zh_clean):
                seen_zh.add(zh_clean)
                seen_vi.add(vi_clean_raw.lower())
                dist = FALLBACK_DISTRACTORS[len(vocab_list) % len(FALLBACK_DISTRACTORS)]
                fname = audio_hash_filename(zh_clean, "dv")
                tts_tasks.append((zh_clean, DAILY_AUDIO_DIR / fname))
                vi_clean = vi_clean_raw[:1].upper() + vi_clean_raw[1:]
                vocab_list.append({
                    "cat": "daily",
                    "date": dt,
                    "vi": vi_clean,
                    "en": f"Log ({app_src or 'ReaKey'})",
                    "zh": zh_clean,
                    "pinyin": to_pinyin(zh_clean),
                    "dist_en": dist[1],
                    "dist_zh": dist[2],
                    "dist_pinyin": to_pinyin(dist[2]),
                    "audio": f"audio/daily/{fname}",
                    "source": f"Nhật ký {app_src}",
                })

        # 3. Add glossary terms updated on this date (with smart neighbor distractors!)
        day_gloss = glossary_by_date.get(dt, [])
        if day_gloss:
            summary_tags.append(f"Tra cứu chuyên sâu {len(day_gloss)} thuật ngữ Tủ điện - Tự động hóa - Nghiệm thu")
            for idx_g, g in enumerate(day_gloss):
                zh = g["zh"]
                if zh in seen_zh:
                    continue
                seen_zh.add(zh)
                # Pick a different glossary term as a realistic technical distractor!
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
                    "source": "ReaKey Glossary",
                })

        if bucket["share_notes"]:
            summary_tags.extend(bucket["share_notes"][:3])

        if not vocab_list and not dialogue_list:
            continue

        dt_obj = datetime.strptime(dt, "%Y-%m-%d")
        short_label = f"Hôm nay ({dt_obj.strftime('%d/%m')})" if dt == today_str else dt_obj.strftime("Ngày %d/%m/%Y")
        summary_str = " • ".join(summary_tags) if summary_tags else f"Đồng bộ {len(vocab_list)} từ vựng & {len(dialogue_list)} tình huống thực tế trong ngày."

        timeline_days.append({
            "date": dt,
            "label": short_label,
            "summary": summary_str,
            "vocab_count": len(vocab_list),
            "dialogue_count": len(dialogue_list),
            "vocab": vocab_list,
            "dialogues": dialogue_list,
        })

    payload = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_days": len(timeline_days),
        "total_vocab": sum(d["vocab_count"] for d in timeline_days),
        "total_dialogues": sum(d["dialogue_count"] for d in timeline_days),
        "days": timeline_days,
    }
    return payload, tts_tasks


def compute_sources_fingerprint() -> str:
    parts: list[str] = []
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


def run_sync(force: bool = False) -> bool:
    fp = compute_sources_fingerprint()
    if not force and STATE_FILE.exists() and TIMELINE_JS.exists():
        try:
            prev = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            if prev.get("fingerprint") == fp:
                return False
        except Exception:
            pass

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Watchdog đang tổng hợp Nhật ký Ngày & cập nhật Timeline...")
    payload, tts_tasks = build_timeline_payload()
    new_mp3 = asyncio.run(synthesize_missing_audio(tts_tasks))

    json_text = json.dumps(payload, ensure_ascii=False, indent=2)
    TIMELINE_JSON.write_text(json_text, encoding="utf-8")
    TIMELINE_JS.write_text(
        "// Auto-generated silently by central_daily_watchdog.py — DO NOT EDIT MANUALLY\n"
        f"window.CYBERBIRD_DAILY_TIMELINE = {json_text};\n",
        encoding="utf-8",
    )
    STATE_FILE.write_text(
        json.dumps({"fingerprint": fp, "updated_at": payload["updated_at"]}, indent=2),
        encoding="utf-8",
    )
    print(
        f"  ✅ Đã cập nhật Timeline ({payload['total_days']} ngày | "
        f"{payload['total_vocab']} từ vựng | {payload['total_dialogues']} hội thoại | "
        f"+{new_mp3} file MP3 mới)!"
    )
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Central Daily Watchdog for CyberBird Lingo PRO")
    parser.add_argument("--once", action="store_true", help="Chạy đồng bộ 1 lần rồi thoát")
    parser.add_argument("--daemon", action="store_true", help="Chạy ngầm theo dõi liên tục (Silent Watchdog)")
    parser.add_argument("--interval", type=int, default=300, help="Chu kỳ quét giây khi chạy daemon (mặc định 300s)")
    parser.add_argument("--force", action="store_true", help="Bắt buộc tổng hợp lại ngay cả khi chưa đổi file")
    args = parser.parse_args()

    if args.daemon:
        print(f"🕵️‍♂️ Central Daily Watchdog khởi chạy ngầm (chu kỳ {args.interval}s)...")
        run_sync(force=args.force)
        while True:
            time.sleep(max(30, args.interval))
            try:
                run_sync(force=False)
            except Exception as exc:
                print(f"[WARN] Watchdog cycle error: {exc}")
    else:
        run_sync(force=True)


if __name__ == "__main__":
    main()
