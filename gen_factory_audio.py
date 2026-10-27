#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import asyncio
from pathlib import Path
import edge_tts

# Fix console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

OUT_DIR = Path(__file__).resolve().parent / "cyberbird_lingo" / "audio"
OUT_DIR.mkdir(parents=True, exist_ok=True)

VOCAB = [
    ('toukui', '头盔'),
    ('kuike', '盔壳'),
    ('huanchongceng', '缓冲层'),
    ('fengjing', '风镜'),
    ('xiabadai', '下巴带'),
    ('kakou', '卡扣'),
    ('neichen', '内衬'),
    ('tongfengkong', '通风孔'),
    ('liushuixian', '流水线'),
    ('zhusuji', '注塑机'),
    ('muju', '模具'),
    ('penqi', '喷漆'),
    ('zuzhuang', '组装'),
    ('zhuangxiang', '装箱'),
    ('pinjian', '品检'),
    ('hege', '合格'),
    ('cipin', '次品'),
    ('huashang', '划伤'),
    ('zhuangjiceshi', '撞击测试'),
    ('jintianjiaban', '今天加班'),
    ('kaizaohui', '开早会'),
    ('huibaojindu', '汇报进度'),
    ('changzhang', '厂长'),
    ('zuzhang', '组长'),
    ('gandingdan', '赶订单'),
    ('anquandiyi', '安全第一'),
    ('anshijiaohuo', '按时交货'),
    ('praise_taibangle', '太棒了'),
    ('praise_zhengque', '正确'),
    ('praise_lihai', '真厉害')
]

async def gen_all():
    print(f"Generating {len(VOCAB)} studio neural audio files...")
    for code, text in VOCAB:
        out_f = OUT_DIR / f"{code}.mp3"
        if not out_f.exists() or out_f.stat().st_size < 1000:
            com = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural", rate="-6%")
            await com.save(str(out_f))
            print(f"  ✓ {code}: {text} ({out_f.stat().st_size} bytes)")
    print("Done! All audio files generated.")

if __name__ == "__main__":
    asyncio.run(gen_all())
