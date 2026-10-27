#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CENTRAL DAILY WATCHDOG — CYBERBIRD LINGO PRO v3.1 (DEAN OPTIMIZE)
=================================================================
Silent Background Watchdog & Daily Diary Timeline Synchronizer ("Very Silent"):
  1. CHỈ ĐỌC (100% Read-Only, tuyệt đối KHÔNG ghi thêm file làm đầy VPS) từ Ổ Đĩa Mạng `Z:\\` (`\\\\100.77.193.96\\DeanHub`):
     - `Z:\\_system\\nhat_ky.db` (bảng `entries`: clipboard_text, note, reminder, rescue_file, starred ⭐; bảng `reminders`)
       -> Copy an toàn ra thư mục tạm trước khi đọc để tuyệt đối KHÔNG khóa DB trên VPS!
     - `Z:\\03_Nhat_Ky_Hang_Ngay\\YYYY-MM-DD.md` (nhật ký hoạt động & clipboard từ cả máy Dell, T14 & Bot 007)
     - `Z:\\01_Files_Cuu_Ho\\`
     - Kết hợp cùng `15. REA/ReaKey/server/data/reavault.db` (`entries` + 45 thuật ngữ `glossary`) và `inbox_diary/` trong dự án.
  2. Tự động lọc nhiễu, tự dịch Tiếng Trung -> Tiếng Việt & Tiếng Anh (có bộ nhớ đệm `.translation_cache.json`),
     tự dựng cả Từ Vựng lẫn Tình Huống Hội Thoại Thực Chiến cho mọi câu WeChat nhà xưởng mới mỗi ngày,
     gắn Pinyin thanh điệu (`pypinyin`) & sinh giọng đọc Neural `zh-CN-XiaoxiaoNeural` (`edge-tts`).
  3. Toàn bộ dữ liệu cập nhật (`daily_timeline.json`, `daily_timeline_data.js`, `audio/daily/*.mp3`) CHỈ lưu gọn bên trong
     thư mục dự án cục bộ `D:\\0.PROGRAMME\\4. DEAN OPTIMIZE\\23. CyberBird-Lingo-Game\\cyberbird_lingo\\`!
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
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

import requests

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
TRANS_CACHE_FILE = PROJECT_DIR / ".translation_cache.json"

# Nguồn dữ liệu Ổ Z: (VPS Dean 007 24/7) + Fallback UNC trực tiếp qua Tailscale
Z_DRIVE_CANDIDATES = [
    Path(r"Z:\\"),
    Path(r"\\100.77.193.96\DeanHub"),
]

# Nguồn phụ trợ trên máy cục bộ
REAVAULT_DB = DEAN_ROOT / "15. REA" / "ReaKey" / "server" / "data" / "reavault.db"
FOLDER_SHARE_DIR = DEAN_ROOT / "19. Folder Share" / "Share"
FOLDER_SHARE_UPLOADS = DEAN_ROOT / "19. Folder Share" / "uploads"

TIMELINE_JSON = GAME_DIR / "daily_timeline.json"
TIMELINE_JS = GAME_DIR / "daily_timeline_data.js"

VOICE_ZH = "zh-CN-XiaoxiaoNeural"
RE_HANZI = re.compile(r"[\u4e00-\u9fff]+")
RE_MENTION = re.compile(r"@[^\s\u2005]+[\s\u2005]*")
RE_URL = re.compile(r"https?://\S+")

# Bộ lọc chặn câu rác, quảng cáo, câu test bàn phím, câu cảm thán vụn vặt
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
    "别高兴得太早",
    "你就是你",
    "你以为你是谁",
    "你是谁",
    "为什么这么奇怪",
    "我的天啊",
    "嘿伙计",
    "嘿我累了",
    "你有问题吗",
    "你是做什么的",
    "做某事",
    "你很健康吗",
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

TRIVIAL_ZH_EXACT = {
    "你好", "您好", "好的", "好", "谢谢", "啊", "哦", "呵呵", "哈哈", "中国人", "十", "快乐", "欢迎", "欢迎，呵呵",
}

# Các mẫu tình huống thực chiến nhà xưởng EON nhận diện chính xác từ WeChat / Zalo / Ổ Z:
CURATED_REAL_FACTORY_PATTERNS: list[dict[str, Any]] = [
    {
        "match": "吸塑模",
        "vocab": [
            {"vi": "Khuôn Hút Định Hình Nhựa", "en": "Blister / Vacuum Mold", "zh": "吸塑模"},
            {"vi": "Khuôn Số 4", "en": "Mold #4", "zh": "4号模"},
            {"vi": "Khuôn 2 Lòng (2 Hốc)", "en": "2-Cavity Mold", "zh": "2穴模"},
            {"vi": "Bộ Phận Định Hình (Hút Nhựa)", "en": "Vacuum Forming Dept", "zh": "吸塑部门"},
        ],
        "dialogue": {
            "speaker": "🏭 Tổ Trưởng Định Hình (Ổ Z: WeChat)",
            "q_zh": "是不是4号吸塑模有问题？我现在做的也是4号模严重！",
            "q_vi": "Có phải khuôn hút nhựa số 4 có vấn đề không? Hàng tôi đang chạy khuôn số 4 cũng bị lỗi nặng!",
            "correct_zh": "马上停下4号模检查，通知模具部过来修模！",
            "correct_vi": "Cho dừng khuôn số 4 kiểm tra ngay, báo bộ phận khuôn qua sửa khuôn!",
            "wrong_zh": "周末我们一起去公园骑自行车吧。",
            "wrong_vi": "Cuối tuần chúng mình cùng ra công viên đạp xe nhé.",
        },
        "tag": "Xử lý lỗi khuôn hút nhựa số 4 (4号吸塑模) & khuôn 2 lòng (2穴模)",
    },
    {
        "match": "翘边",
        "vocab": [
            {"vi": "Cong Vênh Mép (Bavia/Vênh)", "en": "Warped / Lifted Edge", "zh": "翘边"},
            {"vi": "Lựa / Nhặt Riêng Ra", "en": "Pick / Sort Out", "zh": "挑出来"},
            {"vi": "Kiểm Tra Rõ Nguyên Nhân", "en": "Verify Root Cause", "zh": "查核原因"},
            {"vi": "Khẩn Trương Khắc Phục", "en": "Promptly Improve", "zh": "速查改善"},
        ],
        "dialogue": {
            "speaker": "🔍 Chủ Nhiệm QC (Ổ Z: WeChat)",
            "q_zh": "程主任请速查核原因改善，先把有翘边的挑出来！",
            "q_vi": "Chủ nhiệm Trình vui lòng kiểm tra nhanh nguyên nhân để khắc phục, trước mắt nhặt riêng hàng bị vênh mép ra!",
            "correct_zh": "收到，产线正在逐个挑出翘边品，同时排查模具温度！",
            "correct_vi": "Đã nhận, chuyền đang nhặt riêng hàng vênh mép và kiểm tra nhiệt độ khuôn!",
            "wrong_zh": "这家咖啡店的拿铁味道很不错。",
            "wrong_vi": "Món cà phê Latte của quán này vị rất ngon.",
        },
        "tag": "QC yêu cầu nhặt hàng vênh mép (翘边) & điều tra nguyên nhân cải tiến",
    },
    {
        "match": "作业指导书",
        "vocab": [
            {"vi": "Hướng Dẫn Thao Tác (SOP)", "en": "Work Instruction (SOP)", "zh": "作业指导书"},
            {"vi": "Lắp Vỏ Nhựa ABS", "en": "Assemble ABS Shell", "zh": "装ABS壳"},
            {"vi": "Hàng Mẫu Kinh Doanh", "en": "Sales Sample", "zh": "销样"},
            {"vi": "In & Phát Xuống Xưởng", "en": "Print & Distribute", "zh": "打印下发"},
        ],
        "dialogue": {
            "speaker": "📋 Quản Lý Kỹ Thuật (Ổ Z: WeChat)",
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
            "speaker": "🔍 Phó Tổng Tiêu (QC Xuất Nhật)",
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
            "speaker": "💬 Bạn Cũ Trung Quốc (Ổ Z: WeChat)",
            "q_zh": "新公司加班多吗？你现在住宿舍还是租房住？",
            "q_vi": "Công ty mới tăng ca nhiều không? Giờ bạn ở ký túc xá hay thuê trọ?",
            "correct_zh": "看订单情况，我是自己在外面租房住的。",
            "correct_vi": "Tùy theo đơn hàng thôi, mình tự thuê nhà ở bên ngoài.",
            "wrong_zh": "请把空调温度调高两度。",
            "wrong_vi": "Làm ơn tăng nhiệt độ máy lạnh lên 2 độ.",
        },
        "tag": "Trò chuyện WeChat hỏi thăm công việc & bộ phận định hình",
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
        "tag": "Giới thiệu nhà máy Việt Nam, bộ phận QC & kế hoạch xuất hàng",
    },
]

FALLBACK_DISTRACTORS = [
    ("Bàn Họp", "Meeting Table", "会议桌"),
    ("Cốc Nước", "Water Cup", "水杯"),
    ("Máy In", "Printer", "打印机"),
    ("Kho Hàng", "Warehouse", "仓库"),
    ("Xe Nâng", "Forklift", "叉车"),
    ("Thước Cặp", "Caliper", "卡尺"),
    ("Găng Tay", "Gloves", "手套"),
    ("Băng Keo", "Tape", "胶带"),
]

AUTO_WRONG_REPLIES = [
    ("今天下午超市西瓜打折。", "Chiều nay siêu thị giảm giá dưa hấu."),
    ("电影院的爆米花卖完了。", "Bắp rang bơ ở rạp chiếu phim bán hết rồi."),
    ("这双运动鞋穿起来很舒服。", "Đôi giày thể thao này đi rất êm chân."),
    ("周末我们去海边钓鱼吧。", "Cuối tuần chúng mình ra biển câu cá nhé."),
]


def resolve_z_hub() -> Path | None:
    """Locate Z:\\ or \\\\100.77.193.96\\DeanHub, re-mounting Z: silently if needed."""
    for cand in Z_DRIVE_CANDIDATES:
        try:
            if cand.exists():
                return cand
        except Exception:
            pass
    # Silent reconnect attempt via Tailscale SMB if Z: dropped after sleep
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


def load_trans_cache() -> dict[str, dict[str, str]]:
    if TRANS_CACHE_FILE.exists():
        try:
            return json.loads(TRANS_CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_trans_cache(cache: dict[str, dict[str, str]]) -> None:
    try:
        TRANS_CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def auto_translate_zh(zh_text: str, cache: dict[str, dict[str, str]]) -> tuple[str, str]:
    """Translate unseen Chinese workplace phrases from Z:\\ into Vietnamese & English (cached)."""
    if zh_text in cache:
        item = cache[zh_text]
        return item.get("vi", ""), item.get("en", "")

    def _gtx(tl: str) -> str:
        try:
            r = requests.get(
                "https://translate.googleapis.com/translate_a/single",
                params={"client": "gtx", "sl": "zh-CN", "tl": tl, "dt": "t", "q": zh_text},
                timeout=4,
            )
            if r.status_code == 200:
                arr = r.json()
                out = "".join(seg[0] for seg in arr[0] if seg and seg[0]).strip()
                return out[:1].upper() + out[1:] if out else ""
        except Exception:
            pass
        return ""

    vi = _gtx("vi")
    en = _gtx("en")
    if vi:
        cache[zh_text] = {"vi": vi, "en": en or "Workplace Term"}
    return vi, en or "Workplace Term"


def build_smart_auto_reply(zh_sentence: str) -> tuple[str, str]:
    """Generate a realistic factory/workplace Chinese reply based on sentence intent."""
    if any(k in zh_sentence for k in ("挑出", "翘边", "返工", "全检", "不良", "次品", "贴纸", "漏")):
        return (
            "收到，马上安排产线逐个检查并把不良品挑出隔离！",
            "Đã nhận, sắp xếp chuyền kiểm từng cái và nhặt riêng hàng lỗi cách ly ngay!",
        )
    if any(k in zh_sentence for k in ("模", "机", "异常", "问题", "严重", "原因", "改善", "坏")):
        return (
            "明白，马上排查具体原因并通知技术部过来改善处理！",
            "Rõ, kiểm tra nguyên nhân cụ thể và báo bộ phận kỹ thuật qua xử lý ngay!",
        )
    if any(k in zh_sentence for k in ("指导书", "打印", "下发", "计划", "交货", "试产", "报告", "单")):
        return (
            "好的，我马上跟进确认并按要求落实到位。",
            "Vâng, tôi theo sát xác nhận và triển khai đúng yêu cầu ngay.",
        )
    return (
        "已经核对清楚了，我马上整理好发给您确认。",
        "Đã đối chiếu rõ ràng rồi, tôi tổng hợp gửi anh/chị xác nhận ngay.",
    )


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
    if len(zh_s) < 2 or len(zh_s) > 22 or len(vi_s) < 2 or len(vi_s) > 65:
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
        "raw_zh_candidates": [],  # (zh_line, is_starred, origin_label)
        "apps": set(),
        "share_notes": [],
        "reminders": [],
    }


def extract_zh_lines_from_text(content: str, starred: bool, origin: str, bucket: dict[str, Any]) -> None:
    """Extract clean Chinese phrases/sentences from Z:\\ clipboard, WeChat multi-line logs, or notes."""
    for raw_line in content.splitlines():
        line = RE_MENTION.sub("", raw_line).strip()
        line = line.strip(" \t\r\n•*-—|")
        if not line or is_noise_text(line):
            continue
        # Skip timestamp headers like 2026/10/27 8:06 or speaker headers like Đức EON (张公德)
        if re.match(r"^\d{4}[/-]\d{1,2}[/-]\d{1,2}", line):
            continue
        if "张公德" in line and len(line) < 18:
            continue
        # Support explicit "Tiếng Việt | Tiếng Trung" note format on Z:
        if "|" in line and "⚡" not in line:
            parts = [p.strip() for p in line.split("|", 1)]
            if len(parts) == 2 and is_clean_pair(parts[0], parts[1]):
                bucket["clean_pairs"].append((parts[0], parts[1], origin))
                continue
            if len(parts) == 2 and is_clean_pair(parts[1], parts[0]):
                bucket["clean_pairs"].append((parts[1], parts[0], origin))
                continue

        # Pure/predominantly Chinese line from WeChat / Clipboard on Z:
        hanzi_count = sum(len(m) for m in RE_HANZI.findall(line))
        # Must contain at least 2 Hanzi and be mostly Chinese/numbers/punctuation (no Vietnamese paragraphs)
        vi_chars = re.findall(r"[ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ]", line.lower())
        if hanzi_count >= 2 and not vi_chars and 2 <= len(line) <= 45:
            clean_zh = line.strip(" ，。、；：,.\\")
            if clean_zh not in TRIVIAL_ZH_EXACT:
                bucket["raw_zh_candidates"].append((clean_zh, starred, origin))


def collect_z_drive_hub(days_map: dict[str, dict[str, Any]]) -> Path | None:
    """Read daily diary, SQLite nhat_ky.db, reminders, and shared notes from Z:\\ (DeanHub VPS 24/7)."""
    z_root = resolve_z_hub()
    if not z_root:
        print("  [WARN] Tạm thời chưa thấy ổ Z:\\ (\\\\100.77.193.96\\DeanHub) — dùng dữ liệu cục bộ.")
        return None

    # 1. Đọc an toàn Z:\_system\nhat_ky.db qua bản chụp tạm (Zero-Lock trên SMB/VPS)
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

                # Đọc bảng entries
                rows = con.execute(
                    "SELECT id, created_at, category, app_context, content, file_name, starred "
                    "FROM entries ORDER BY id ASC"
                ).fetchall()
                for r in rows:
                    dt = str(r["created_at"] or "")[:10]
                    if not re.match(r"^\d{4}-\d{2}-\d{2}$", dt):
                        continue
                    bucket = days_map.setdefault(dt, make_day_bucket())
                    cat = str(r["category"] or "")
                    content = str(r["content"] or "").strip()
                    starred = bool(r["starred"])

                    if content and cat in ("clipboard_text", "note", "rescue_file", "reminder"):
                        bucket["raw_blobs"].append(content)
                        origin = "⭐ Ghim Ổ Z:" if starred else "Ổ Z: DeanHub"
                        extract_zh_lines_from_text(content, starred, origin, bucket)

                    if starred and content and len(content) < 80:
                        bucket["share_notes"].append(f"⭐ Đã ghim: {content[:45]}")

                # Đọc bảng reminders (nhắc việc hằng ngày từ Bot Dean 007)
                rem_rows = con.execute(
                    "SELECT created_at, remind_at, note, status FROM reminders ORDER BY id DESC LIMIT 20"
                ).fetchall()
                for rr in rem_rows:
                    dt = str(rr["created_at"] or rr["remind_at"] or "")[:10]
                    note = str(rr["note"] or "").strip()
                    status = str(rr["status"] or "")
                    remind_time = str(rr["remind_at"] or "")[11:16]
                    if re.match(r"^\d{4}-\d{2}-\d{2}$", dt) and note and "uống nước" not in note.lower():
                        bucket = days_map.setdefault(dt, make_day_bucket())
                        tag_rem = f"⏰ Nhắc việc ({remind_time}): {note}" if status == "pending" else f"✅ Đã nhắc: {note}"
                        if tag_rem not in bucket["reminders"]:
                            bucket["reminders"].append(tag_rem)

                con.close()
        except Exception as exc:
            print(f"  [WARN] Lỗi đọc bản sao Z:\\_system\\nhat_ky.db: {exc}")

    # 2. Quét Z:\03_Nhat_Ky_Hang_Ngay\*.md (nhật ký Markdown theo từng ngày)
    md_dir = z_root / "03_Nhat_Ky_Hang_Ngay"
    if md_dir.exists():
        for md_file in sorted(md_dir.glob("*.md"))[-14:]:  # Quét 14 ngày gần nhất cho siêu nhanh
            m = re.match(r"^(\d{4}-\d{2}-\d{2})", md_file.stem)
            if not m:
                continue
            dt = m.group(1)
            bucket = days_map.setdefault(dt, make_day_bucket())
            try:
                md_txt = md_file.read_text(encoding="utf-8", errors="replace")
                bucket["raw_blobs"].append(md_txt)
            except Exception:
                pass

    # 3. CHỈ ĐỌC các file văn bản cứu hộ trên Z:\01_Files_Cuu_Ho (Tuyệt đối KHÔNG tạo/ghi bất kỳ thư mục nào lên ổ Z:!)
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
                    bucket["share_notes"].append(f"📂 File Ổ Z: {f.name}")
                    extract_zh_lines_from_text(txt, True, f"Ổ Z: {f.name}", bucket)
                except Exception:
                    pass

    return z_root


def collect_reavault_and_local(days_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Also merge local ReaKey SQLite Vault & inbox_diary/ if present."""
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


def build_timeline_payload() -> tuple[dict[str, Any], list[tuple[str, Path]], Path | None]:
    days_map: dict[str, dict[str, Any]] = {}
    z_root = collect_z_drive_hub(days_map)
    glossary_items = collect_reavault_and_local(days_map)
    trans_cache = load_trans_cache()
    trans_dirty = False

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
        joined_blob = "\n".join(bucket["raw_blobs"])
        summary_tags: list[str] = []
        vocab_list: list[dict[str, Any]] = []
        dialogue_list: list[dict[str, Any]] = []
        seen_zh: set[str] = set()
        seen_dlg_q: set[str] = set()

        # 0. Nhắc việc trong ngày từ Z:\_system\nhat_ky.db
        if bucket["reminders"]:
            summary_tags.extend(bucket["reminders"][:2])

        # 1. Khớp các tình huống nhà xưởng chuẩn xác từ nhật ký Ổ Z: & WeChat
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
                        "source": "Ổ Z: / WeChat Xưởng",
                    })
                dlg = pat["dialogue"]
                seen_dlg_q.add(dlg["q_zh"])
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

        # 2. Tự động dịch & nạp các câu/từ Tiếng Trung MỚI phát sinh trên Ổ Z: (cho mọi ngày tiếp theo!)
        seen_vi: set[str] = {v["vi"].lower() for v in vocab_list}
        for zh_cand, is_starred, origin in bucket["raw_zh_candidates"]:
            if zh_cand in seen_zh or zh_cand in seen_dlg_q:
                continue
            # Bỏ qua nếu đã nằm trong câu mẫu curated ở trên
            if any(zh_cand in q_existing or q_existing[:8] in zh_cand for q_existing in seen_dlg_q):
                continue

            if 2 <= len(zh_cand) <= 8:
                before_len = len(trans_cache)
                vi_tr, en_tr = auto_translate_zh(zh_cand, trans_cache)
                if len(trans_cache) != before_len:
                    trans_dirty = True
                if not vi_tr or vi_tr.lower() in seen_vi or is_noise_text(vi_tr):
                    continue
                seen_zh.add(zh_cand)
                seen_vi.add(vi_tr.lower())
                dist = FALLBACK_DISTRACTORS[len(vocab_list) % len(FALLBACK_DISTRACTORS)]
                fname = audio_hash_filename(zh_cand, "dv")
                tts_tasks.append((zh_cand, DAILY_AUDIO_DIR / fname))
                vocab_list.append({
                    "cat": "daily",
                    "date": dt,
                    "vi": ("⭐ " + vi_tr) if is_starred else vi_tr,
                    "en": en_tr,
                    "zh": zh_cand,
                    "pinyin": to_pinyin(zh_cand),
                    "dist_en": dist[1],
                    "dist_zh": dist[2],
                    "dist_pinyin": to_pinyin(dist[2]),
                    "audio": f"audio/daily/{fname}",
                    "source": origin,
                })
            elif 10 <= len(zh_cand) <= 38 and len(dialogue_list) < 16:
                before_len = len(trans_cache)
                vi_tr, _ = auto_translate_zh(zh_cand, trans_cache)
                if len(trans_cache) != before_len:
                    trans_dirty = True
                if not vi_tr or is_noise_text(vi_tr):
                    continue
                seen_dlg_q.add(zh_cand)
                corr_zh, corr_vi = build_smart_auto_reply(zh_cand)
                wrong_zh, wrong_vi = AUTO_WRONG_REPLIES[len(dialogue_list) % len(AUTO_WRONG_REPLIES)]
                q_fname = audio_hash_filename(zh_cand, "dq")
                a_fname = audio_hash_filename(corr_zh, "da")
                tts_tasks.append((zh_cand, DAILY_AUDIO_DIR / q_fname))
                tts_tasks.append((corr_zh, DAILY_AUDIO_DIR / a_fname))
                dialogue_list.append({
                    "id": f"daily_{dt}_z_{len(dialogue_list) + 1}",
                    "cat": "daily",
                    "date": dt,
                    "speaker": f"💬 Nhật Ký {origin}",
                    "q_zh": zh_cand,
                    "q_pinyin": to_pinyin(zh_cand),
                    "q_vi": vi_tr,
                    "q_audio": f"audio/daily/{q_fname}",
                    "correct_zh": corr_zh,
                    "correct_pinyin": to_pinyin(corr_zh),
                    "correct_vi": corr_vi,
                    "wrong_zh": wrong_zh,
                    "wrong_pinyin": to_pinyin(wrong_zh),
                    "wrong_vi": wrong_vi,
                    "a_audio": f"audio/daily/{a_fname}",
                })

        # 3. Nạp các cặp dịch song ngữ từ ReaKey & ghi chú thủ công
        for vi_txt, zh_txt, app_src in bucket["clean_pairs"]:
            zh_clean = zh_txt.strip(" ，。！？、；：,.!?\\()（）")
            vi_clean_raw = vi_txt.strip(" ，。！？、；：,.!?\\()（）")
            if not zh_clean or not vi_clean_raw:
                continue
            if zh_clean in seen_zh or vi_clean_raw.lower() in seen_vi:
                continue
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
                    "en": f"Log ({app_src or 'Ổ Z:'})",
                    "zh": zh_clean,
                    "pinyin": to_pinyin(zh_clean),
                    "dist_en": dist[1],
                    "dist_zh": dist[2],
                    "dist_pinyin": to_pinyin(dist[2]),
                    "audio": f"audio/daily/{fname}",
                    "source": f"Nhật ký {app_src}",
                })

        # 4. Nạp bộ thuật ngữ kỹ thuật Tủ điện & Tự động hóa
        day_gloss = glossary_by_date.get(dt, [])
        if day_gloss:
            summary_tags.append(f"Tra cứu {len(day_gloss)} thuật ngữ Tủ điện - Tự động hóa")
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
                    "source": "ReaKey Glossary",
                })

        if bucket["share_notes"]:
            summary_tags.extend(bucket["share_notes"][:3])

        if not vocab_list and not dialogue_list:
            continue

        dt_obj = datetime.strptime(dt, "%Y-%m-%d")
        short_label = f"Hôm nay ({dt_obj.strftime('%d/%m')})" if dt == today_str else dt_obj.strftime("Ngày %d/%m/%Y")
        summary_str = " • ".join(summary_tags) if summary_tags else f"Đồng bộ từ Ổ Z: {len(vocab_list)} từ vựng & {len(dialogue_list)} tình huống thực chiến."

        timeline_days.append({
            "date": dt,
            "label": short_label,
            "summary": summary_str,
            "vocab_count": len(vocab_list),
            "dialogue_count": len(dialogue_list),
            "vocab": vocab_list,
            "dialogues": dialogue_list,
        })

    if trans_dirty:
        save_trans_cache(trans_cache)

    payload = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_hub": str(z_root) if z_root else "Local Fallback",
        "total_days": len(timeline_days),
        "total_vocab": sum(d["vocab_count"] for d in timeline_days),
        "total_dialogues": sum(d["dialogue_count"] for d in timeline_days),
        "days": timeline_days,
    }
    return payload, tts_tasks, z_root


def compute_sources_fingerprint() -> str:
    parts: list[str] = []
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


def run_sync(force: bool = False) -> bool:
    fp = compute_sources_fingerprint()
    if not force and STATE_FILE.exists() and TIMELINE_JS.exists():
        try:
            prev = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            if prev.get("fingerprint") == fp:
                return False
        except Exception:
            pass

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Watchdog đang đồng bộ Nhật ký từ Ổ Share Z:\\ (DeanHub 24/7)...")
    payload, tts_tasks, z_root = build_timeline_payload()
    new_mp3 = asyncio.run(synthesize_missing_audio(tts_tasks))

    json_text = json.dumps(payload, ensure_ascii=False, indent=2)
    TIMELINE_JSON.write_text(json_text, encoding="utf-8")
    TIMELINE_JS.write_text(
        "// Auto-generated silently by central_daily_watchdog.py from Z:\\ DeanHub (Read-Only) — DO NOT EDIT MANUALLY\n"
        f"window.CYBERBIRD_DAILY_TIMELINE = {json_text};\n",
        encoding="utf-8",
    )

    STATE_FILE.write_text(
        json.dumps(
            {
                "fingerprint": fp,
                "updated_at": payload["updated_at"],
                "source_hub": payload["source_hub"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        f"  ✅ Đã cập nhật vào thư mục dự án 23 ({payload['total_days']} ngày | "
        f"{payload['total_vocab']} từ vựng | {payload['total_dialogues']} hội thoại | "
        f"+{new_mp3} MP3 mới | Ổ Z: chỉ đọc 100%, tốn 0 KB trên VPS)!"
    )
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Central Daily Watchdog (Z:\\ DeanHub Edition)")
    parser.add_argument("--once", action="store_true", help="Chạy đồng bộ 1 lần rồi thoát")
    parser.add_argument("--daemon", action="store_true", help="Chạy ngầm theo dõi Ổ Z: liên tục (Silent Watchdog)")
    parser.add_argument("--interval", type=int, default=300, help="Chu kỳ quét giây khi chạy daemon (mặc định 300s)")
    parser.add_argument("--force", action="store_true", help="Bắt buộc tổng hợp lại ngay cả khi chưa đổi file")
    args = parser.parse_args()

    if args.daemon:
        print(f"🕵️‍♂️ Central Daily Watchdog (Z:\\ DeanHub) khởi chạy ngầm (chu kỳ {args.interval}s)...")
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
