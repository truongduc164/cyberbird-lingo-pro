import asyncio
import subprocess
import edge_tts
from pathlib import Path

out_dir = Path("temp_xkcd_353")
out_dir.mkdir(exist_ok=True)

# 4 Scenes dialogs
SCENES = [
    {
        "id": 1,
        "title": "Scene 1 • Sao cậu bay được?",
        "cn": "你居然在飞！你怎么做到的？—— 因为Python啊！",
        "vi": "Cậu đang bay kìa! Sao cậu làm được vậy? — Nhờ Python đó!",
        "speaker1_text": "你居然在飞！你怎么做到的？",
        "speaker1_voice": "zh-CN-YunxiNeural",
        "speaker2_text": "因为Python啊！",
        "speaker2_voice": "zh-CN-YunjianNeural",
    },
    {
        "id": 2,
        "title": "Scene 2 • Học Python tối qua",
        "cn": "我昨晚刚学！打印Hello World只要一行代码！",
        "vi": "Tớ mới học tối qua! In Hello World chỉ cần đúng một dòng!",
        "speaker1_text": "我昨晚刚学！打印Hello World只要一行代码！",
        "speaker1_voice": "zh-CN-YunjianNeural",
        "speaker2_text": "真的假的？编程有这么容易吗？",
        "speaker2_voice": "zh-CN-YunxiNeural",
    },
    {
        "id": 3,
        "title": "Scene 3 • Sao cậu bay được cơ chứ?",
        "cn": "快上来吧！编程变快乐了！—— 但你到底是怎样飞起来的？！",
        "vi": "Lên đây đi, vui lắm! — Nhưng sao cậu BAY được cơ chứ?!",
        "speaker1_text": "快上来吧！编程变得超级快乐！",
        "speaker1_voice": "zh-CN-YunjianNeural",
        "speaker2_text": "但你到底是怎么飞起来的？！",
        "speaker2_voice": "zh-CN-YunxiNeural",
    },
    {
        "id": 4,
        "title": "Scene 4 • import antigravity",
        "cn": "我只输入了import antigravity！我相信绝对是Python的功劳！",
        "vi": "Tớ chỉ gõ import antigravity! Chắc chắn là do Python đó!",
        "speaker1_text": "我刚才只输入了一行代码：import antigravity！",
        "speaker1_voice": "zh-CN-YunjianNeural",
        "speaker2_text": "就这么简单？！",
        "speaker2_voice": "zh-CN-YunxiNeural",
        "speaker3_text": "其实我还吃了药箱里的药片…但我相信绝对是Python的功劳！",
        "speaker3_voice": "zh-CN-YunjianNeural",
    }
]

async def generate():
    for s in SCENES:
        sid = s["id"]
        # Generate speaker 1
        f1 = out_dir / f"s{sid}_v1.mp3"
        await edge_tts.Communicate(s["speaker1_text"], s["speaker1_voice"]).save(str(f1))
        # Generate speaker 2
        f2 = out_dir / f"s{sid}_v2.mp3"
        await edge_tts.Communicate(s["speaker2_text"], s["speaker2_voice"]).save(str(f2))
        
        if "speaker3_text" in s:
            f3 = out_dir / f"s{sid}_v3.mp3"
            await edge_tts.Communicate(s["speaker3_text"], s["speaker3_voice"]).save(str(f3))

    print("Audio generation completed!")

if __name__ == "__main__":
    asyncio.run(generate())
