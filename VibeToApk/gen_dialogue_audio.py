#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import asyncio
from pathlib import Path
import edge_tts

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

OUT_DIR = Path(__file__).resolve().parent / "cyberbird_lingo" / "audio"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DIALOGUES = [
    ("dlg_01_q", "今天能按时交货吗？"),
    ("dlg_01_a", "可以，已经打包好了。"),
    ("dlg_02_q", "这批盔壳合格了吗？"),
    ("dlg_02_a", "都合格，没有划伤。"),
    ("dlg_03_q", "今晚需要加班吗？"),
    ("dlg_03_a", "要加班两小时赶订单。"),
    ("dlg_04_q", "注塑机为什么停了？"),
    ("dlg_04_a", "正在换模具，马上好。"),
    ("dlg_05_q", "卡扣的方向装反了吗？"),
    ("dlg_05_a", "没有，方向是对的。"),
    ("dlg_06_q", "进车间必须戴什么？"),
    ("dlg_06_a", "必须戴好安全帽。"),
    ("dlg_07_q", "一箱装多少个头盔？"),
    ("dlg_07_a", "一箱装20个，已装完。"),
    ("dlg_08_q", "这顶头盔风镜有划痕！"),
    ("dlg_08_a", "马上换一个新风镜。"),
    ("dlg_09_q", "今天的早会几点开？"),
    ("dlg_09_a", "八点整准时在车间开。"),
    ("dlg_10_q", "撞击测试结果怎么样？"),
    ("dlg_10_a", "缓冲层良好，测试通过！"),
    ("dlg_11_q", "还有多少个下巴带没装？"),
    ("dlg_11_a", "还剩最后50条。"),
    ("dlg_12_q", "这批喷漆颜色对不对？"),
    ("dlg_12_a", "跟客户样板完全一致。"),
]

async def gen_all():
    print(f"Generating {len(DIALOGUES)} studio dialogue audio files...")
    for code, text in DIALOGUES:
        out_f = OUT_DIR / f"{code}.mp3"
        if not out_f.exists() or out_f.stat().st_size < 1000:
            com = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural", rate="-4%")
            await com.save(str(out_f))
            print(f"  ✓ {code}: {text} ({out_f.stat().st_size} bytes)")
    print("Done! All dialogue audio files generated.")

if __name__ == "__main__":
    asyncio.run(gen_all())
