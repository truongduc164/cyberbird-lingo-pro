#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI PEDAGOGICAL DIARY CURATOR (ANTIGRAVITY LS BRIDGE) — CYBERBIRD LINGO PRO v3.3
===============================================================================
Sử dụng 100% Quota Antigravity sẵn có trên máy (giống hệt cơ chế của `central-trending-bot`!):
- Tự động kết nối tới `language_server.exe` của Antigravity (`discover_antigravity_ls()`)
  và gọi `agentapi new-conversation --model=flash` (0 đồng API trả phí bên ngoài!).
- Đọc hiểu dữ liệu nhật ký trong ngày, sửa triệt để lỗi OCR chữ Hán, lọc tên riêng/mã nội bộ,
  và biên soạn thành JSON bài học sư phạm hoàn chỉnh (`topic_title`, `summary`, `learning_tip`,
  `vocab` kèm từ nhiễu cùng trường nghĩa, và `dialogues` cân xứng).
- Lưu bộ nhớ đệm SHA-256 tại `.ai_curated_days_cache.json` để các ngày cũ tốn 0 quota!
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import threading
import time
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parent
AI_CACHE_FILE = PROJECT_DIR / ".ai_curated_days_cache.json"
PROMPT_VERSION = "v3.3-antigravity-ls-flash"

_LS_CACHE: dict[str, Any] | None = None

_DISCOVERY_PS = (
    "$procs = Get-CimInstance Win32_Process -Filter \"Name='language_server.exe'\";"
    "$out = @(foreach($p in $procs){"
    "  $ports = @(Get-NetTCPConnection -OwningProcess $p.ProcessId -State Listen "
    "    -ErrorAction SilentlyContinue | Select-Object -ExpandProperty LocalPort);"
    "  [pscustomobject]@{ pid = $p.ProcessId; cmd = $p.CommandLine; ports = $ports }"
    "});"
    "ConvertTo-Json -InputObject $out -Depth 5 -Compress"
)

RE_SENSITIVE_OR_NOISE = re.compile(
    r"(https?://\S+|sk-[A-Za-z0-9_-]{12,}|\b\d{6,}:[A-Za-z0-9_-]{20,}\b|"
    r"memory usage|ctrl\s*\+\s*alt|telegravity|telecoder)",
    re.I,
)


def _find_ls_binary() -> Path | None:
    local = os.environ.get("LOCALAPPDATA") or r"C:\Users\User\AppData\Local"
    for sub in ("Antigravity", "antigravity"):
        cand = Path(local) / "Programs" / sub / "resources" / "bin" / "language_server.exe"
        if cand.exists():
            return cand
    return None


def _extract_flag(cmd_line: str, flag_name: str) -> str:
    tokens = (cmd_line or "").split()
    for i, tok in enumerate(tokens):
        if tok.startswith(flag_name + "="):
            return tok.split("=", 1)[1].strip('"')
        if tok == flag_name and i + 1 < len(tokens):
            return tokens[i + 1].strip('"')
    return ""


def _clean_env() -> dict[str, str]:
    env = dict(os.environ)
    for k in (
        "ANTIGRAVITY_SOURCE_METADATA",
        "ANTIGRAVITY_CONVERSATION_ID",
        "ANTIGRAVITY_TRAJECTORY_ID",
        "ANTIGRAVITY_AGENT",
    ):
        env.pop(k, None)
    return env


def discover_antigravity_ls(refresh: bool = False) -> dict[str, Any] | None:
    """Discover local Antigravity language_server.exe address & CSRF token (identical to central-trending-bot)."""
    global _LS_CACHE
    if _LS_CACHE is not None and not refresh:
        return _LS_CACHE

    exe = _find_ls_binary()
    if exe is None:
        return None

    ps_bin = shutil.which("powershell.exe") or r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
    try:
        res = subprocess.run(
            [ps_bin, "-NoProfile", "-NonInteractive", "-Command", _DISCOVERY_PS],
            capture_output=True,
            text=True,
            timeout=15,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        raw = (res.stdout or "").strip()
        if not raw:
            return None
        parsed = json.loads(raw)
        servers = [parsed] if isinstance(parsed, dict) else [x for x in parsed if isinstance(x, dict)]
    except Exception:
        return None

    for srv in servers:
        cmd = str(srv.get("cmd") or "")
        csrf = _extract_flag(cmd, "--csrf_token")
        if not csrf:
            continue
        ports = srv.get("ports") or []
        if isinstance(ports, (int, str)):
            ports = [ports]
        for port in ports:
            try:
                addr = f"127.0.0.1:{int(port)}"
            except Exception:
                continue
            env = _clean_env()
            env["ANTIGRAVITY_LS_ADDRESS"] = addr
            env["ANTIGRAVITY_CSRF_TOKEN"] = csrf
            try:
                probe = subprocess.run(
                    [str(exe), "agentapi", "get-conversation-metadata", "00000000-0000-0000-0000-000000000000"],
                    capture_output=True,
                    text=True,
                    timeout=6,
                    env=env,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
                out = (probe.stdout or "") + (probe.stderr or "")
                if "trajectory not found" in out:
                    _LS_CACHE = {"exe": str(exe), "address": addr, "csrf": csrf, "pid": srv.get("pid")}
                    return _LS_CACHE
            except Exception:
                continue
    return None


def resolve_project_id() -> str:
    proj_dir = Path.home() / ".gemini" / "config" / "projects"
    for folder in (PROJECT_DIR, PROJECT_DIR.parent / "18.Central-trending"):
        quoted = urllib.parse.quote(str(folder.resolve()).replace("\\", "/"), safe="/")
        uri = re.sub(r"^([A-Za-z])%3A", lambda m: f"{m.group(1).lower()}%3A", quoted)
        target_uri = f"file:///{uri}".lower()
        if proj_dir.exists():
            for p in sorted(proj_dir.glob("*.json")):
                try:
                    data = json.loads(p.read_text(encoding="utf-8-sig"))
                    resources = ((data.get("projectResources") or {}).get("resources")) or []
                    for r in resources:
                        f1 = str(r.get("folderUri") or "").lower()
                        f2 = str(((r.get("gitFolder") or {}).get("folderUri")) or "").lower()
                        if target_uri in (f1, f2):
                            return str(data.get("id") or p.stem)
                except Exception:
                    continue
    if proj_dir.exists():
        first = next(proj_dir.glob("*.json"), None)
        if first:
            try:
                return str(json.loads(first.read_text(encoding="utf-8-sig")).get("id") or first.stem)
            except Exception:
                return first.stem
    return "0d3e0c0c-1ef2-4430-b951-c980fca12d72"


def _extract_conv_id(stdout_text: str) -> str:
    try:
        obj = json.loads(stdout_text)
        if isinstance(obj, dict):
            for k in ("conversationId", "conversation_id"):
                if obj.get(k):
                    return str(obj[k])
    except Exception:
        pass
    m = re.search(r'"conversation(?:Id|_id)"\s*:\s*"([0-9a-fA-F-]{20,64})"', stdout_text or "")
    return m.group(1) if m else ""


def _find_transcript_by_req_id(req_id: str, since_ts: float, known_conv_id: str = "") -> tuple[str, Path | None]:
    brain_root = Path.home() / ".gemini" / "antigravity" / "brain"
    if not brain_root.exists():
        return "", None

    if known_conv_id:
        for fname in ("transcript_full.jsonl", "transcript.jsonl"):
            cand = brain_root / known_conv_id / ".system_generated" / "logs" / fname
            if cand.exists():
                return known_conv_id, cand

    candidates = []
    for child in brain_root.iterdir():
        if not child.is_dir():
            continue
        tfull = child / ".system_generated" / "logs" / "transcript_full.jsonl"
        tcomp = child / ".system_generated" / "logs" / "transcript.jsonl"
        tf = tfull if tfull.exists() else (tcomp if tcomp.exists() else None)
        if tf is not None:
            try:
                mtime = tf.stat().st_mtime
                if mtime >= since_ts - 3.0:
                    candidates.append((mtime, child.name, tf))
            except OSError:
                continue

    candidates.sort(reverse=True)
    for _, cid, tf in candidates[:12]:
        try:
            head = tf.read_text(encoding="utf-8", errors="replace")[:16384]
            if req_id in head:
                return cid, tf
        except OSError:
            continue
    return "", None


def _check_final_response(transcript_path: Path) -> tuple[bool, str]:
    try:
        lines = transcript_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return False, ""

    records = []
    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
            if isinstance(obj, dict):
                records.append(obj)
        except Exception:
            continue

    if not records:
        return False, ""

    last_rec = records[-1]
    if str(last_rec.get("type") or "") == "PLANNER_RESPONSE" and str(last_rec.get("status") or "") == "DONE":
        tcalls = last_rec.get("tool_calls") or []
        content = str(last_rec.get("content") or "").strip()
        if not tcalls and content:
            return True, content
    return False, ""


def invoke_antigravity_flash_json(prompt: str, title: str, timeout_sec: int = 90) -> str:
    """Invoke Antigravity's built-in `flash` model via local `language_server.exe` ($0 paid API!)."""
    ls = discover_antigravity_ls() or discover_antigravity_ls(refresh=True)
    if ls is None:
        raise RuntimeError("Antigravity IDE (language_server.exe) hiện chưa bật.")

    req_id = f"cb_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    tagged_prompt = f"[{req_id}]\n{prompt}"

    env = _clean_env()
    env["ANTIGRAVITY_LS_ADDRESS"] = ls["address"]
    env["ANTIGRAVITY_CSRF_TOKEN"] = ls["csrf"]
    env["ANTIGRAVITY_PROJECT_ID"] = resolve_project_id()

    argv = [
        ls["exe"],
        "agentapi",
        "new-conversation",
        "--model=flash",
        f"--title={title}",
        tagged_prompt,
    ]

    launch_ts = time.time()
    conv_id = ""
    proc = subprocess.Popen(
        argv,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        cwd=str(PROJECT_DIR),
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    try:
        out_s, _ = proc.communicate(timeout=3.0)
        conv_id = _extract_conv_id(out_s)
    except subprocess.TimeoutExpired:
        def _reap(p: subprocess.Popen) -> None:
            try:
                p.communicate(timeout=150)
            except Exception:
                try:
                    p.kill()
                except Exception:
                    pass
        threading.Thread(target=_reap, args=(proc,), daemon=True).start()

    deadline = time.time() + timeout_sec
    transcript_path: Path | None = None
    while time.time() < deadline:
        if transcript_path is None or not transcript_path.exists():
            found_cid, found_tf = _find_transcript_by_req_id(req_id, launch_ts, known_conv_id=conv_id)
            if found_cid:
                conv_id = found_cid
            if found_tf is not None:
                transcript_path = found_tf
        if transcript_path is not None and transcript_path.exists():
            full_cand = transcript_path.with_name("transcript_full.jsonl")
            if full_cand.exists():
                transcript_path = full_cand
            done, content = _check_final_response(transcript_path)
            if done:
                time.sleep(0.5)
                done2, content2 = _check_final_response(transcript_path)
                if done2 and content2:
                    return content2
        time.sleep(1.0)

    raise TimeoutError("Quá thời gian chờ phản hồi từ Antigravity LS.")


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


def prepare_sanitized_day_digest_input(
    raw_blobs: list[str],
    clean_pairs: list[tuple[str, str, str]],
    raw_zh_candidates: list[tuple[str, bool, str]],
) -> str:
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


CURATION_INSTRUCTIONS = """Bạn đang chạy ở chế độ **BIÊN TẬP VIÊN SƯ PHẠM CYBERBIRD LINGO PRO**.
TUYỆT ĐỐI KHÔNG gọi bất kỳ công cụ (tool) nào — KHÔNG gọi read_file, write_file, run_command hay ask_question. Hãy trả lời TRỰC TIẾP duy nhất 1 JSON Object hợp lệ!

NHIỆM VỤ:
Từ các mảnh nhật ký công việc / tin nhắn WeChat / OCR thô trong ngày bên dưới, hãy TỔNG KẾT, SỬA LỖI và BIÊN TẬP LẠI thành một bài học ngôn ngữ Tiếng Trung - Tiếng Anh Thực Chiến chuẩn sư phạm.

QUY TẮC BẮT BUỘC:
1. KHÔNG BÊ NGUYÊN XI:
   - Tự động sửa triệt để mọi chữ Hán bị lỗi OCR ngay cả trong `q_zh` (VD: '不合拾' -> '不合格', '拟现件' -> '限度样', '熬分箱' -> '单独分箱包装').
   - Xóa sạch tên riêng cá nhân, ngày tháng ký tên, mã đơn hàng/sản phẩm nội bộ (SMI-17, SP-165, 7071, BTN-8-11...), và nhắc việc cá nhân ngoài lề.
2. ĐÚC KẾT SƯ PHẠM:
   - `topic_title`: Tiêu đề chủ đề bài học trong ngày (ngắn gọn 5-10 từ tiếng Việt).
   - `summary`: 2 câu tiếng Việt mạch lạc, truyền cảm hứng, tóm tắt hôm nay người học nắm được nhóm từ vựng/kỹ năng nào (kèm 3-4 từ Hán trọng tâm trong ngoặc).
   - `learning_tip`: 1 câu bắt đầu bằng '💡 Mẹo thực chiến:' phân biệt cặp từ dễ nhầm hoặc cấu trúc câu đắt giá trong bài.
3. TỪ VỰNG (`vocab` — 8 đến 15 từ/cụm từ đắt giá nhất, dài 2–5 chữ Hán):
   - Mỗi mục gồm: `zh`, `vi` (nghĩa Việt chuẩn chuyên ngành), `en`, `dist_zh` (từ nhiễu chữ Hán CÙNG TRƯỜNG NGHĨA nhưng khác nghĩa rõ ràng), `dist_en`.
4. HỘI THOẠI (`dialogues` — 5 đến 7 tình huống thực chiến):
   - Mỗi mục gồm: `speaker` (kèm emoji vai trò), `q_zh` (12–24 chữ Hán chuẩn), `q_vi`, `correct_zh` (ngắn gọn 12–20 chữ Hán), `correct_vi`, `wrong_zh` (sai ngữ cảnh nhưng CÓ ĐỘ DÀI TƯƠNG ĐƯƠNG `correct_zh`, 12–20 chữ Hán), `wrong_vi`.

CHỈ XUẤT DUY NHẤT KHỐI JSON HỢP LỆ THEO MẪU:
{
  "topic_title": "...",
  "summary": "...",
  "learning_tip": "💡 Mẹo thực chiến: ...",
  "vocab": [{"zh": "...", "vi": "...", "en": "...", "dist_zh": "...", "dist_en": "..."}],
  "dialogues": [{"speaker": "...", "q_zh": "...", "q_vi": "...", "correct_zh": "...", "correct_vi": "...", "wrong_zh": "...", "wrong_vi": "..."}]
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
    Curate day's raw diary via Antigravity LS Bridge (`--model=flash`, 100% Antigravity Quota, $0 Paid API!).
    """
    digest_input = prepare_sanitized_day_digest_input(raw_blobs, clean_pairs, raw_zh_candidates)
    if not digest_input.strip():
        return None

    input_hash = compute_day_input_hash(date_str, digest_input)
    cache = load_ai_cache()

    if not force_refresh and date_str in cache:
        cached_entry = cache[date_str]
        if isinstance(cached_entry, dict) and cached_entry.get("input_hash") == input_hash:
            lesson = cached_entry.get("lesson")
            if isinstance(lesson, dict) and (lesson.get("vocab") or lesson.get("dialogues")):
                return lesson
        # Reuse existing cached lesson if only PROMPT_VERSION bumped and not forced, unless we want fresh AG curation
        if not force_refresh and isinstance(cached_entry, dict) and isinstance(cached_entry.get("lesson"), dict):
            prev_raw_hash = cached_entry.get("raw_only_hash")
            cur_raw_hash = hashlib.sha256(f"{date_str}|{digest_input}".encode("utf-8")).hexdigest()
            if prev_raw_hash == cur_raw_hash:
                return cached_entry["lesson"]

    cur_raw_hash = hashlib.sha256(f"{date_str}|{digest_input}".encode("utf-8")).hexdigest()
    prompt = (
        f"{CURATION_INSTRUCTIONS}\n\n"
        f"NGÀY NHẬT KÝ: {date_str}\n"
        f"DỮ LIỆU THÔ TRONG NGÀY:\n---\n{digest_input}\n---"
    )

    try:
        print(f"  🤖 [Antigravity Flash Quota] Đang trau chuốt bài học ngày {date_str} ($0 API ngoài)...")
        raw_reply = invoke_antigravity_flash_json(
            prompt=prompt,
            title=f"[CyberBird Lesson] {date_str}",
            timeout_sec=95,
        )
        lesson = extract_json_object(raw_reply)
        if not lesson or not isinstance(lesson, dict):
            print("  [WARN] Antigravity LS không trả về JSON hợp lệ.")
            if date_str in cache and isinstance(cache[date_str].get("lesson"), dict):
                return cache[date_str]["lesson"]
            return None

        clean_vocab = []
        for v in lesson.get("vocab") or []:
            if not isinstance(v, dict):
                continue
            zh = str(v.get("zh") or "").strip()
            vi = str(v.get("vi") or "").strip()
            en = str(v.get("en") or "Workplace Term").strip()
            dist_zh = str(v.get("dist_zh") or "包装箱").strip()
            dist_en = str(v.get("dist_en") or "Carton Box").strip()
            if 2 <= len(zh) <= 8 and vi and re.search(r"[\u4e00-\u9fff]", zh):
                if dist_zh == zh:
                    dist_zh, dist_en = "合格品", "Qualified Item"
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
            "raw_only_hash": cur_raw_hash,
            "updated_by_model": "antigravity-ls-flash",
            "lesson": polished,
        }
        save_ai_cache(cache)
        return polished

    except Exception as exc:
        print(f"  [WARN] Tạm chưa kết nối được Antigravity LS cho ngày {date_str}: {exc}")
        if date_str in cache and isinstance(cache[date_str].get("lesson"), dict):
            return cache[date_str]["lesson"]
        return None
