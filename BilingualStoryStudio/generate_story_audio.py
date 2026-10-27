import urllib.request
import urllib.parse
import subprocess
import json
import re
from pathlib import Path

FFMPEG_EXE = "C:/Users/User/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin/ffmpeg.exe"
AUDIO_DIR = Path("audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

SCENES = [
    {
        "id": 1,
        "hanzi_ruby": "<ruby>有<rt>yǒu</rt></ruby><ruby>一<rt>yì</rt></ruby><ruby>天<rt>tiān</rt></ruby>，<ruby>森<rt>sēn</rt></ruby><ruby>林<rt>lín</rt></ruby><ruby>里<rt>lǐ</rt></ruby><ruby>的<rt>de</rt></ruby><ruby>兔<rt>tù</rt></ruby><ruby>子<rt>zi</rt></ruby><ruby>嘲<rt>cháo</rt></ruby><ruby>笑<rt>xiào</rt></ruby><ruby>乌<rt>wū</rt></ruby><ruby>龟<rt>guī</rt></ruby><ruby>走<rt>zǒu</rt></ruby><ruby>得<rt>de</rt></ruby><ruby>慢<rt>màn</rt></ruby>。",
        "hanzi_plain": "有一天，森林里的兔子嘲笑乌龟走得慢。",
        "pinyin_plain": "Yǒu yì tiān, sēnlín lǐ de tùzi cháoxiào wūguī zǒu de màn.",
        "vi": "Một ngày nọ, thỏ trong rừng cười nhạo rùa vì đi chậm.",
        "vocab_word": "乌龟 (wūguī)",
        "vocab_meaning": "Con Rùa",
        "vocab_word2": "兔子 (tùzi)",
        "vocab_meaning2": "Con Thỏ"
    },
    {
        "id": 2,
        "hanzi_ruby": "<ruby>乌<rt>wū</rt></ruby><ruby>龟<rt>guī</rt></ruby><ruby>说<rt>shuō</rt></ruby>：“<ruby>我<rt>wǒ</rt></ruby><ruby>们<rt>men</rt></ruby><ruby>来<rt>lái</rt></ruby><ruby>比<rt>bǐ</rt></ruby><ruby>赛<rt>sài</rt></ruby><ruby>跑<rt>pǎo</rt></ruby><ruby>吧<rt>ba</rt></ruby>，<ruby>看<rt>kàn</rt></ruby><ruby>谁<rt>shéi</rt></ruby><ruby>先<rt>xiān</rt></ruby><ruby>到<rt>dào</rt></ruby><ruby>山<rt>shān</rt></ruby><ruby>顶<rt>dǐng</rt></ruby>。”",
        "hanzi_plain": "乌龟说：我们来比赛跑吧，看谁先到山顶。",
        "pinyin_plain": "Wūguī shuō: Wǒmen lái bǐ sàipǎo ba, kàn shéi xiān dào shāndǐng.",
        "vi": "Rùa nói: Chúng ta thi chạy xem ai đến đỉnh núi trước.",
        "vocab_word": "比赛 (bǐsài)",
        "vocab_meaning": "Thi Đấu",
        "vocab_word2": "山顶 (shāndǐng)",
        "vocab_meaning2": "Đỉnh Núi"
    },
    {
        "id": 3,
        "hanzi_ruby": "<ruby>兔<rt>tù</rt></ruby><ruby>子<rt>zi</rt></ruby><ruby>飞<rt>fēi</rt></ruby><ruby>快<rt>kuài</rt></ruby><ruby>地<rt>de</rt></ruby><ruby>跑<rt>pǎo</rt></ruby><ruby>在<rt>zài</rt></ruby><ruby>前<rt>qián</rt></ruby><ruby>面<rt>mian</rt></ruby>，<ruby>跑<rt>pǎo</rt></ruby><ruby>了<rt>le</rt></ruby><ruby>一<rt>yí</rt></ruby><ruby>半<rt>bàn</rt></ruby><ruby>便<rt>biàn</rt></ruby><ruby>在<rt>zài</rt></ruby><ruby>树<rt>shù</rt></ruby><ruby>下<rt>xià</rt></ruby><ruby>睡<rt>shuì</rt></ruby><ruby>午<rt>wǔ</rt></ruby><ruby>觉<rt>jiào</rt></ruby>。",
        "hanzi_plain": "兔子飞快地跑在前面，跑了一半便在树下睡午觉。",
        "pinyin_plain": "Tùzi fēikuài de pǎo zài qiánmian, pǎo le yíbàn biàn zài shù xià shuì wǔjiào.",
        "vi": "Thỏ chạy nhanh dẫn trước, được một nửa đường liền ngủ trưa dưới gốc cây.",
        "vocab_word": "飞快 (fēikuài)",
        "vocab_meaning": "Nhanh Như Bay",
        "vocab_word2": "睡午觉 (shuì wǔjiào)",
        "vocab_meaning2": "Ngủ Trưa"
    },
    {
        "id": 4,
        "hanzi_ruby": "<ruby>乌<rt>wū</rt></ruby><ruby>龟<rt>guī</rt></ruby><ruby>坚<rt>jiān</rt></ruby><ruby>持<rt>chí</rt></ruby><ruby>往<rt>wǎng</rt></ruby><ruby>前<rt>qián</rt></ruby><ruby>爬<rt>pá</rt></ruby>，<ruby>终<rt>zhōng</rt></ruby><ruby>于<rt>yú</rt></ruby><ruby>赢<rt>yíng</rt></ruby><ruby>得<rt>dé</rt></ruby><ruby>胜<rt>shèng</rt></ruby><ruby>利<rt>lì</rt></ruby>。<ruby>坚<rt>jiān</rt></ruby><ruby>持<rt>chí</rt></ruby><ruby>就<rt>jiù</rt></ruby><ruby>能<rt>néng</rt></ruby><ruby>成<rt>chéng</rt></ruby><ruby>功<rt>gōng</rt></ruby>！",
        "hanzi_plain": "乌龟坚持往前爬，终于赢得胜利。坚持就能成功！",
        "pinyin_plain": "Wūguī jiānchí wǎng qián pá, zhōngyú yíngdé shènglì. Jiānchí jiù néng chénggōng!",
        "vi": "Rùa kiên trì bò về phía trước, cuối cùng giành chiến thắng. Kiên trì ắt thành công!",
        "vocab_word": "坚持 (jiānchí)",
        "vocab_meaning": "Kiên Trì",
        "vocab_word2": "成功 (chénggōng)",
        "vocab_meaning2": "Thành Công"
    }
]

def get_duration(audio_path):
    proc = subprocess.run([FFMPEG_EXE, "-i", str(audio_path)], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors="replace")
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", proc.stderr)
    if m:
        h, mn, s = float(m.group(1)), float(m.group(2)), float(m.group(3))
        return h * 3600 + mn * 60 + s
    return 4.0

current_start = 0.0
results = []

print("Generating Chinese speech audio...")
for sc in SCENES:
    text = sc["hanzi_plain"]
    url = "https://translate.google.com/translate_tts?ie=UTF-8&tl=zh-CN&client=tw-ob&q=" + urllib.parse.quote(text)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    audio_file = AUDIO_DIR / f"voice_{sc['id']}.mp3"
    
    with urllib.request.urlopen(req) as resp:
        audio_file.write_bytes(resp.read())

    dur = get_duration(audio_file)
    # Add a short buffer pause (0.8s) for scene breathing room
    scene_dur = round(dur + 0.8, 2)
    
    sc_data = {
        **sc,
        "audio_file": f"audio/voice_{sc['id']}.mp3",
        "audio_duration": dur,
        "scene_start": round(current_start, 2),
        "scene_duration": scene_dur
    }
    results.append(sc_data)
    print(f"Scene {sc['id']}: start={current_start:.2f}s, dur={scene_dur:.2f}s")
    current_start += scene_dur

total_duration = round(current_start, 2)
print(f"\nTotal video duration: {total_duration}s")

with open("scenes_data.json", "w", encoding="utf-8") as f:
    json.dump({"total_duration": total_duration, "scenes": results}, f, ensure_ascii=False, indent=2)

print("Saved scenes_data.json successfully!")
