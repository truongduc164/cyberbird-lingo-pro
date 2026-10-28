#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI PEDAGOGICAL DIARY CURATOR — CYBERBIRD LINGO PRO v3.2 (DEAN OPTIMIZE)
=======================================================================
Biên tập viên AI Sư Phạm (DeepSeek LLM):
- Đọc dữ liệu thô trong ngày từ nhật ký công việc (Ổ Z:\\, WeChat, Zalo, ReaKey).
- TUYỆT ĐỐI KHÔNG BÊ NGUYÊN XI tin nhắn vụn, lỗi OCR (như '不合拾', '熬分箱'), tên cá nhân,
  mã nội bộ nhạy cảm hay lời nhắc cá nhân ngoài lề.
- Tự động tổng kết, chuẩn hóa và trau chuốt lại thành một BÀI HỌC NGÔN NGỮ SƯ PHẠM hoàn chỉnh:
  1. `topic_title`: Chủ đề trọng tâm của ngày (ngắn gọn, hấp dẫn).
  2. `summary`: Bản tóm tắt bài học dành cho người học (2-3 câu tự nhiên, đúc kết ngữ cảnh & từ khóa).
  3. `learning_tip`: Mẹo ghi nhớ từ vựng / mẫu câu giao tiếp thực chiến trong ngày.
  4. `vocab`: Bộ từ vựng / cụm từ đắt giá nhất trong ngày (2-6 chữ Hán), dịch chuẩn chuyên ngành
     Việt - Anh kèm từ nhiễu (`dist_zh`, `dist_en`) cùng trường nghĩa để luyện phản xạ thông minh.
  5. `dialogues`: Các tình huống đối đáp công việc / đời sống tự nhiên (10-26 chữ Hán), câu chữ chuẩn xác,
     lịch sự, thực tế để người học áp dụng được ngay ngày hôm sau!
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import requests

PROJECT_DIR = Path(__file__).resolve().parent
DEAN_ROOT = PROJECT_DIR.parent
AI_CACHE_FILE = PROJECT_DIR / ".ai_curated_days_cache.json"

PROMPT_VERSION = "v3.2-pedagogical-pro-2"

ENV_SEARCH_PATHS = [
    PROJECT_DIR / ".env",
    DEAN_ROOT / "1.TELECODER" / ".env",
]


def load_llm_credentials() -> tuple[str, str, str]:
    """Load (api_key, base_url, model) safely from environment or local .env files."""
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip()
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat").strip()

    if not api_key:
        for env_path in ENV_SEARCH_PATHS:
            if not env_path.exists():
                continue
            try:
                txt = env_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            vals: dict[str, str] = {}
            for raw_line in txt.splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                vals[k.strip()] = v.strip().strip("\"'")
            if vals.get("DEEPSEEK_API_KEY"):
                api_key = vals["DEEPSEEK_API_KEY"]
                base_url = vals.get("DEEPSEEK_BASE_URL", base_url)
                model = vals.get("DEEPSEEK_MODEL", model)
                break

    if not model:
        model = "deepseek-chat"
    return api_key, base_url.rstrip("/"), model


def load_ai_cache() -> dict[str, Any]:
    if AI_CACHE_FILE.exists():
        try:
            return json.loads(AI_CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_ai_cache(cache: dict[str, Any]) -> None:
    try:
        AI_CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


RE_SENSITIVE_OR_NOISE = re.compile(
    r"(https?://\S+|sk-[A-Za-z0-9_-]{12,}|\b\d{6,}:[A-Za-z0-9_-]{20,}\b|"
    r"memory usage|ctrl\s*\+\s*alt|telegravity|telecoder)",
    re.I,
)


def prepare_sanitized_day_digest_input(
    raw_blobs: list[str],
    clean_pairs: list[tuple[str, str, str]],
    raw_zh_candidates: list[tuple[str, bool, str]],
) -> str:
    """Deduplicate and pre-clean raw diary notes before sending to AI Pedagogical Editor."""
    seen_lines: set[str] = set()
    collected: list[str] = []

    for vi, zh, src in clean_pairs:
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
            # Keep lines containing Chinese characters or factory/technical keywords
            has_zh = bool(re.search(r"[\u4e00-\u9fff]", line))
            if not has_zh:
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


SYSTEM_PEDAGOGICAL_PROMPT = """Bạn là Chuyên gia Biên tập Giáo trình Tiếng Trung - Tiếng Anh Thực Chiến (Công xưởng, Sản xuất, QC, Kỹ thuật Tự động hóa & Giao tiếp công sở) cho ứng dụng game luyện phản xạ CyberBird Lingo PRO.

NHIỆM VỤ CỐT LÕI:
Từ các mảnh nhật ký công việc / tin nhắn WeChat / OCR thô trong ngày của người học, hãy TỔNG KẾT, SỬA LỖI và BIÊN TẬP LẠI thành một bài học ngôn ngữ sư phạm, tinh gọn, chuẩn xác.

QUY TẮC VÀNG (BẮT BUỘC TUÂN THỦ 100%):
1. TUYỆT ĐỐI KHÔNG BÊ NGUYÊN XI (NO VERBATIM DUMP):
   - Tự động nhận diện và SỬA TRIỆT ĐỂ mọi chữ Hán bị lỗi OCR ngay cả trong `q_zh` (ví dụ: tuyệt đối KHÔNG giữ '不合拾', '如样拟现件', '熬分箱'; phải viết lại thành chữ Hán chuẩn mực như '不合格', '按照限度样标准', '粉尘多的产品请单独分箱包装').
   - XÓA SẠCH tên riêng cá nhân (như 马启敏, 程主任, 张公德...), ngày tháng ký tên, TẤT CẢ mã sản phẩm/đơn hàng nội bộ (như SMI-17, SP-165, SP 165, 7071, BTN-8-11, 8/10PCS — hãy thay bằng danh từ chung như '这批货', '这款头盔', '出口订单'), và các việc cá nhân ngoài lề.
   - Khái quát hóa thành câu giao tiếp Tiếng Trung chuẩn mực, tự nhiên, lịch sự mà người học có thể nói/nhắn lại ngay trong xưởng hoặc văn phòng.

2. TÓM TẮT SƯ PHẠM (`topic_title`, `summary`, `learning_tip`):
   - `topic_title`: Tiêu đề chủ đề bài học trong ngày (ngắn gọn 5-10 từ tiếng Việt).
   - `summary`: 2 câu tiếng Việt mạch lạc, truyền cảm hứng, tóm tắt hôm nay người học nắm được nhóm kỹ năng/từ vựng thực tế nào (có đính kèm 3-4 từ Hán trọng tâm trong ngoặc).
   - `learning_tip`: 1 mẹo ngắn gọn (1 câu bắt đầu bằng '💡 Mẹo thực chiến:') chỉ ra cấu trúc câu hay hoặc cách phân biệt từ dễ nhầm trong bài hôm nay.

3. TỪ VỰNG TRỌNG TÂM (`vocab` — chọn lọc từ 8 đến 16 từ/cụm từ đắt giá nhất, dài 2–5 chữ Hán):
   - Mỗi từ gồm:
     • `zh`: Chữ Hán chuẩn (2–5 ký tự, KHÔNG chứa mã tiếng Anh/số vụn nếu không cần thiết).
     • `vi`: Nghĩa tiếng Việt chuẩn thuật ngữ nhà xưởng/kỹ thuật, viết hoa chữ cái đầu, ngắn gọn dễ đọc nhanh khi bay (2–6 từ).
     • `en`: Nghĩa tiếng Anh chuẩn xác, ngắn gọn (1–4 từ).
     • `dist_zh`: Từ nhiễu chữ Hán (2–5 ký tự) CÙNG TRƯỜNG NGHĨA công xưởng/đời sống nhưng KHÁC NGHĨA RÕ RÀNG với `zh` (để người học luyện phân biệt thật sự, không dùng từ ngô nghê).
     • `dist_en`: Nghĩa tiếng Anh tương ứng của `dist_zh`.

4. HỘI THOẠI PHẢN XẠ (`dialogues` — biên tập từ 5 đến 8 tình huống thực chiến đắt giá nhất):
   - Mỗi tình huống gồm:
     • `speaker`: Vai trò người nói rõ ràng kèm emoji (VD: '🔍 Kỹ Sư QC Ngoại Quan', '🏭 Tổ Trưởng Sản Xuất', '📦 Quản Lý Đóng Gói', '⚡ Kỹ Sư Kỹ Thuật', '🤝 Đối Tác Trung Quốc').
     • `q_zh`: Câu nói/câu hỏi tình huống Tiếng Trung tự nhiên, trau chuốt, 100% chữ Hán chuẩn (dài 12–24 chữ Hán, dễ đọc nhanh trên banner).
     • `q_vi`: Nghĩa tiếng Việt tự nhiên, sát thực tế của `q_zh`.
     • `correct_zh`: Câu đáp trả lời logic, chuyên nghiệp bằng Tiếng Trung — BẮT BUỘC NGẮN GỌN SÚC TÍCH (chỉ dài 10–16 chữ Hán để hiển thị to rõ trên cổng bay!).
     • `correct_vi`: Nghĩa tiếng Việt của `correct_zh`.
     • `wrong_zh`: Câu nhiễu sai ngữ cảnh — BẮT BUỘC CÓ ĐỘ DÀI TƯƠNG ĐƯƠNG `correct_zh` (10–16 chữ Hán) để người chơi không thể đoán mò theo độ dài câu!
     • `wrong_vi`: Nghĩa tiếng Việt của `wrong_zh`.

ĐỊNH DẠNG ĐẦU RA:
Chỉ trả về DUY NHẤT 1 JSON Object hợp lệ theo đúng cấu trúc sau (không bọc giải thích thừa):
{
  "topic_title": "...",
  "summary": "...",
  "learning_tip": "💡 Mẹo thực chiến: ...",
  "vocab": [
    {"zh": "...", "vi": "...", "en": "...", "dist_zh": "...", "dist_en": "..."}
  ],
  "dialogues": [
    {
      "speaker": "...",
      "q_zh": "...",
      "q_vi": "...",
      "correct_zh": "...",
      "correct_vi": "...",
      "wrong_zh": "...",
      "wrong_vi": "..."
    }
  ]
}"""


def extract_json_object(raw_text: str) -> dict[str, Any] | None:
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except Exception:
        return None


def curate_day_lesson_with_ai(
    date_str: str,
    raw_blobs: list[str],
    clean_pairs: list[tuple[str, str, str]],
    raw_zh_candidates: list[tuple[str, bool, str]],
    force_refresh: bool = False,
) -> dict[str, Any] | None:
    """
    Synthesize and polish a day's raw diary snippets into a structured pedagogical lesson.
    Uses SHA-256 content caching so unchanged days cost 0 API calls.
    """
    digest_input = prepare_sanitized_day_digest_input(raw_blobs, clean_pairs, raw_zh_candidates)
    if not digest_input.strip():
        return None

    input_hash = hashlib.sha256(f"{PROMPT_VERSION}|{date_str}|{digest_input}".encode("utf-8")).hexdigest()
    cache = load_ai_cache()

    if not force_refresh and date_str in cache:
        cached_entry = cache[date_str]
        if isinstance(cached_entry, dict) and cached_entry.get("input_hash") == input_hash:
            lesson = cached_entry.get("lesson")
            if isinstance(lesson, dict) and (lesson.get("vocab") or lesson.get("dialogues")):
                return lesson

    api_key, base_url, model = load_llm_credentials()
    if not api_key:
        print("  [WARN] Không tìm thấy DEEPSEEK_API_KEY để biên tập AI — dùng chế độ dự phòng.")
        return None

    user_prompt = (
        f"Ngày nhật ký: {date_str}\n"
        f"Dưới đây là các ghi chú / tin nhắn / từ tra cứu thực tế phát sinh trong ngày:\n"
        f"---\n{digest_input}\n---\n"
        f"Hãy tổng kết, khử lỗi OCR/tên riêng/mã vụn và biên soạn thành bài học JSON chuẩn sư phạm cho học viên!"
    )

    try:
        print(f"  🤖 [AI Biên Tập Sư Phạm] Đang trau chuốt bài học ngày {date_str} qua {model}...")
        resp = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PEDAGOGICAL_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.35,
                "max_tokens": 3200,
                "response_format": {"type": "json_object"},
            },
            timeout=45,
        )
        if resp.status_code != 200:
            print(f"  [WARN] AI Curator HTTP {resp.status_code}: {resp.text[:180]}")
            return None

        content = resp.json()["choices"][0]["message"]["content"]
        lesson = extract_json_object(content)
        if not lesson or not isinstance(lesson, dict):
            print("  [WARN] AI Curator không trả về JSON hợp lệ.")
            return None

        # Validate & sanitize items
        clean_vocab = []
        for v in lesson.get("vocab") or []:
            if not isinstance(v, dict):
                continue
            zh = str(v.get("zh") or "").strip()
            vi = str(v.get("vi") or "").strip()
            en = str(v.get("en") or "Workplace Term").strip()
            dist_zh = str(v.get("dist_zh") or "会议桌").strip()
            dist_en = str(v.get("dist_en") or "Meeting Table").strip()
            if 2 <= len(zh) <= 8 and vi and re.search(r"[\u4e00-\u9fff]", zh):
                if dist_zh == zh:
                    dist_zh, dist_en = "包装箱", "Carton Box"
                clean_vocab.append({
                    "zh": zh,
                    "vi": vi[:1].upper() + vi[1:],
                    "en": en[:1].upper() + en[1:],
                    "dist_zh": dist_zh,
                    "dist_en": dist_en[:1].upper() + dist_en[1:],
                })

        clean_dlgs = []
        for d in lesson.get("dialogues") or []:
            if not isinstance(d, dict):
                continue
            q_zh = str(d.get("q_zh") or "").strip()
            q_vi = str(d.get("q_vi") or "").strip()
            c_zh = str(d.get("correct_zh") or "").strip()
            c_vi = str(d.get("correct_vi") or "").strip()
            w_zh = str(d.get("wrong_zh") or "").strip()
            w_vi = str(d.get("wrong_vi") or "").strip()
            speaker = str(d.get("speaker") or "🏭 Tình Huống Thực Chiến").strip()
            if q_zh and q_vi and c_zh and c_vi and w_zh and re.search(r"[\u4e00-\u9fff]", q_zh):
                clean_dlgs.append({
                    "speaker": speaker,
                    "q_zh": q_zh,
                    "q_vi": q_vi,
                    "correct_zh": c_zh,
                    "correct_vi": c_vi,
                    "wrong_zh": w_zh,
                    "wrong_vi": w_vi or "Câu trả lời không phù hợp ngữ cảnh.",
                })

        polished = {
            "topic_title": str(lesson.get("topic_title") or "Thực chiến Tiếng Trung Công Xưởng").strip(),
            "summary": str(lesson.get("summary") or "").strip(),
            "learning_tip": str(lesson.get("learning_tip") or "").strip(),
            "vocab": clean_vocab,
            "dialogues": clean_dlgs,
            "ai_curated": True,
        }

        cache[date_str] = {
            "input_hash": input_hash,
            "updated_by_model": model,
            "lesson": polished,
        }
        save_ai_cache(cache)
        return polished

    except Exception as exc:
        print(f"  [WARN] Lỗi gọi AI Curator cho ngày {date_str}: {exc}")
        # Fallback to stale cache for this date if available
        if date_str in cache and isinstance(cache[date_str].get("lesson"), dict):
            return cache[date_str]["lesson"]
        return None
