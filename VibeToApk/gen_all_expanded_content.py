#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Neural Edge-TTS Studio Audio for Expanded CyberBird Lingo Content
Topics: Electronics, Office, Tech & AI, Social & Dining
Voice: zh-CN-XiaoxiaoNeural
"""
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

# 1. NEW VOCABULARY AUDIO
VOCAB_ITEMS = [
    # Electronics & Automation (15)
    ('dianluban', '电路板'),
    ('hanjie', '焊接'),
    ('xinpian', '芯片'),
    ('chuanganqi', '传感器'),
    ('jidianqi', '继电器'),
    ('bujindianji', '步进电机'),
    ('wanyongbiao', '万用表'),
    ('duanlu', '短路'),
    ('kaiguandianyuan', '开关电源'),
    ('plc_biancheng', 'PLC编程'),
    ('monixinhao', '模拟信号'),
    ('baoxiansi', '保险丝'),
    ('dianrong', '电容'),
    ('dianzu', '电阻'),
    ('xianlu', '线路'),

    # Office & Business Trade (15)
    ('shangyehetong', '商业合同'),
    ('baojiadan', '报价单'),
    ('fapiao', '发票'),
    ('jinchukou', '进出口'),
    ('jizhuangxiang', '集装箱'),
    ('fayoujian', '发邮件'),
    ('xianshanghuiyi', '线上会议'),
    ('dayinziliao', '打印资料'),
    ('shenpifeiyong', '审批费用'),
    ('jiagetanpan', '价格谈判'),
    ('zhifudingjin', '支付定金'),
    ('kehudangan', '客户档案'),
    ('tongzhigongwen', '通知公文'),
    ('caigoudingdan', '采购订单'),
    ('tuihuoyanshou', '退货验收'),

    # Tech & Software AI (10)
    ('rengongzhineng', '人工智能'),
    ('shujuku', '数据库'),
    ('yunfuwuqi', '云服务器'),
    ('suanfabiancheng', '算法编程'),
    ('yonghujiemian', '用户界面'),
    ('xiufuloudong', '修复漏洞'),
    ('kaiyuandaima', '开源代码'),
    ('juyuwang', '局域网'),
    ('xinxianquan', '信息安全'),
    ('dashuju', '大数据'),

    # Social & Everyday Communication (10)
    ('qingkechifan', '请客吃饭'),
    ('maidan', '买单'),
    ('saoweixinma', '扫微信码'),
    ('dadididi', '打滴滴'),
    ('yudingjiudian', '预订酒店'),
    ('duihuanhuobi', '兑换货币'),
    ('jidianjianmian', '几点见面'),
    ('ganbei', '干杯'),
    ('meiwenti', '没问题'),
    ('jiageweixin', '加个微信'),

    # Chinese Food & Dining (6)
    ('huoguo', '火锅'),
    ('shuijiao', '水饺'),
    ('kaoya', '烤鸭'),
    ('zhenzhunaicha', '珍珠奶茶'),
    ('chaocai', '炒菜'),
    ('mifan', '米饭')
]

# 2. NEW REAL-LIFE WORKPLACE & SOCIAL DIALOGUES (12 pairs = 24 files)
DIALOGUE_ITEMS = [
    # 14. Electronics PCB Output Voltage
    ("dlg_14_q", "这块电路板为什么没有输出电压？"),
    ("dlg_14_a", "检查发现保险丝烧断了，需要换新的。"),

    # 15. Electronics Sensor Flashing Red
    ("dlg_15_q", "传感器信号灯为什么一直在闪红光？"),
    ("dlg_15_a", "可能是接线松了，重新拧紧就正常了。"),

    # 16. PLC Automation Program Testing
    ("dlg_16_q", "这台PLC程序修改好并测试了吗？"),
    ("dlg_16_a", "已经上传测试完成，运行非常稳定。"),

    # 17. Office Quotation Request
    ("dlg_17_q", "客户催要那份新产品的报价单！"),
    ("dlg_17_a", "我已经核算好成本，马上发邮件给客户。"),

    # 18. Office Shipping Container Customs Clearance
    ("dlg_18_q", "这批集装箱的海关申报手续办好了吗？"),
    ("dlg_18_a", "报关资料全部审核通过，今天可以放行。"),

    # 19. Office Supplier Advance Payment
    ("dlg_19_q", "供应商的预付款今天能安排支付吗？"),
    ("dlg_19_a", "领导已经签字审批，下午网银转账。"),

    # 20. Tech Cloud Server Latency
    ("dlg_20_q", "为什么今天云服务器连接这么慢？"),
    ("dlg_20_a", "正在备份核心数据库，十分钟后恢复正常。"),

    # 21. Tech Security Bug Patch
    ("dlg_21_q", "发现一个系统漏洞，需要紧急修复！"),
    ("dlg_21_a", "收到，我们马上打上安全补丁并重启服务。"),

    # 22. Social Hotpot Dinner Invitation
    ("dlg_22_q", "今晚有空吗？我请大家一起吃四川火锅！"),
    ("dlg_22_a", "太感谢了！下班后我们七点在餐厅门口集合。"),

    # 23. Social WeChat QR Code Payment
    ("dlg_23_q", "你好，请问您微信支付还是支付宝？"),
    ("dlg_23_a", "我扫您的微信收款码，请出示一下。"),

    # 24. Social Add WeChat Friend
    ("dlg_24_q", "很高兴今天认识您，加个微信方便联系吧！"),
    ("dlg_24_a", "好啊，这是我的微信二维码，您扫我。"),

    # 25. Social Airport Didi Ride Duration
    ("dlg_25_q", "师傅，请问到国际机场大概需要多长时间？"),
    ("dlg_25_a", "现在不堵车，大概四十分钟就能到。")
]

async def generate_single(code, text, rate="-5%"):
    out_f = OUT_DIR / f"{code}.mp3"
    if out_f.exists() and out_f.stat().st_size > 800:
        return
    try:
        com = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural", rate=rate)
        await com.save(str(out_f))
        print(f"  ✓ {code}: {text} ({out_f.stat().st_size} bytes)")
    except Exception as e:
        print(f"  ✗ Error {code}: {e}")

async def main():
    print(f"Generating {len(VOCAB_ITEMS)} Vocabulary and {len(DIALOGUE_ITEMS)} Dialogue audio files...")
    tasks = []
    # Batch vocab
    for code, text in VOCAB_ITEMS:
        tasks.append(generate_single(code, text, rate="-6%"))
    # Batch dialogues
    for code, text in DIALOGUE_ITEMS:
        tasks.append(generate_single(code, text, rate="-4%"))
    
    # Run concurrently in chunks of 8 to avoid connection throttling
    chunk_size = 8
    for i in range(0, len(tasks), chunk_size):
        chunk = tasks[i:i+chunk_size]
        await asyncio.gather(*chunk)
    print("Done! All expanded audio files generated successfully.")

if __name__ == "__main__":
    asyncio.run(main())
