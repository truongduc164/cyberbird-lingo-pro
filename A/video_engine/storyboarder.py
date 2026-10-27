"""
Storyboarder Module: Splits topics or long texts into structured video scenes.
"""
import re
from typing import List, Dict, Any

class Storyboarder:
    def __init__(self):
        pass

    def create_storyboard_from_topic(self, topic: str, lang: str = "vi") -> List[Dict[str, Any]]:
        """
        Generate a 4-5 scene storyboard from a topic.
        """
        clean_topic = topic.strip()
        if lang == "vi":
            scenes = [
                {
                    "scene_id": 1,
                    "title": "BẬT MÍ BẤT NGỜ",
                    "text": f"Bạn đã biết điều này về {clean_topic} chưa?",
                    "theme": "cyber_blue",
                    "motion": "zoom_in"
                },
                {
                    "scene_id": 2,
                    "title": "ĐIỂM ĐẶC BIỆT #1",
                    "text": "Đầu tiên, công nghệ đang thay đổi nhanh hơn bao giờ hết mỗi ngày.",
                    "theme": "neon_purple",
                    "motion": "zoom_out"
                },
                {
                    "scene_id": 3,
                    "title": "ĐIỂM ĐẶC BIỆT #2",
                    "text": "Những ai làm chủ được tự động hóa sẽ tiết kiệm được hàng trăm giờ làm việc.",
                    "theme": "sunset_orange",
                    "motion": "zoom_in"
                },
                {
                    "scene_id": 4,
                    "title": "KẾT LUẬN & HÀNH ĐỘNG",
                    "text": "Hãy bắt đầu thử nghiệm ngay hôm nay để đón đầu làn sóng mới nhé!",
                    "theme": "emerald_green",
                    "motion": "zoom_out"
                }
            ]
        else:
            scenes = [
                {
                    "scene_id": 1,
                    "title": "DID YOU KNOW?",
                    "text": f"Here is something fascinating about {clean_topic}.",
                    "theme": "cyber_blue",
                    "motion": "zoom_in"
                },
                {
                    "scene_id": 2,
                    "title": "KEY INSIGHT",
                    "text": "Automation and AI are accelerating faster than ever before.",
                    "theme": "neon_purple",
                    "motion": "zoom_out"
                },
                {
                    "scene_id": 3,
                    "title": "WHY IT MATTERS",
                    "text": "Those who adapt early will gain an exponential advantage.",
                    "theme": "sunset_orange",
                    "motion": "zoom_in"
                },
                {
                    "scene_id": 4,
                    "title": "ACTION POINT",
                    "text": "Start building your ideas today and lead the future!",
                    "theme": "emerald_green",
                    "motion": "zoom_out"
                }
            ]
        return scenes

    def create_storyboard_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Partition arbitrary text or story into bite-sized scenes.
        """
        # Split by periods, question marks, exclamation marks, or newlines
        raw_sentences = re.split(r"[.\n?!]+", text)
        sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 3]

        themes = ["cyber_blue", "neon_purple", "sunset_orange", "emerald_green", "deep_ruby"]
        motions = ["zoom_in", "zoom_out"]

        scenes = []
        for i, s in enumerate(sentences):
            theme = themes[i % len(themes)]
            motion = motions[i % len(motions)]
            scenes.append({
                "scene_id": i + 1,
                "title": f"PHẦN {i + 1}" if len(sentences) > 1 else "NỘI DUNG",
                "text": s,
                "theme": theme,
                "motion": motion
            })

        if not scenes:
            scenes = self.create_storyboard_from_topic("Ý Tưởng Mới")

        return scenes
