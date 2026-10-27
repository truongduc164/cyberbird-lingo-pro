"""
Vibe Spark Engine: Transforms trends & hot topics into spontaneous project ideas.
Works 100% offline with Smart Heuristics, or enhances with LLM if API key is present.
"""
import os
import re
import random
from typing import List, Dict, Any
from collections import Counter
import logging

logger = logging.getLogger(__name__)

# Curated sparks templates for cross-pollination
VIBE_RECIPES = [
    {
        "pattern": ["agent", "ai", "automation"],
        "title": "🤖 {keyword} Micro-Agent Companion",
        "desc": "Tạo một agent siêu nhỏ (single-file python) chuyên tự động hóa quy trình {topic}. Chạy nền, không ngốn RAM.",
        "difficulty": "Easy (1 buổi tối)",
        "tech_stack": "Python + FastUI / Click + SQLite",
        "vibe_score": 96
    },
    {
        "pattern": ["llm", "local", "model"],
        "title": "🧠 Local {keyword} Playground & Benchmark",
        "desc": "Tool mini so sánh tốc độ sinh token và độ chuẩn xác giữa các model nhẹ mới nhất ngay trên máy tính cá nhân.",
        "difficulty": "Medium (1 ngày cuối tuần)",
        "tech_stack": "Streamlit + Ollama / PyTorch + Rich",
        "vibe_score": 94
    },
    {
        "pattern": ["github", "stars", "tools", "developer"],
        "title": "⚡ {keyword} Star Watcher & Instant Alert",
        "desc": "Bộ radar theo dõi và gửi thông báo qua Discord/Telegram ngay khi có repo hoặc công cụ cùng chủ đề tăng vọt tương tác.",
        "difficulty": "Easy (2 giờ)",
        "tech_stack": "Python + Requests + Webhook + Schedule",
        "vibe_score": 91
    },
    {
        "pattern": ["voice", "audio", "speech", "vision"],
        "title": "🎙️ Quick {keyword} Voice/Vision Assistant",
        "desc": "Tích hợp model nhận diện/âm thanh mới nổi thành phím tắt Windows (Global Hotkey), bấm là phân tích ngay lập tức.",
        "difficulty": "Medium (1-2 ngày)",
        "tech_stack": "Python + Keyboard/PyStray + Edge-TTS/Whisper",
        "vibe_score": 95
    },
    {
        "pattern": ["cli", "terminal", "tool"],
        "title": "💻 Supercharged {keyword} TUI / CLI",
        "desc": "Biến thao tác lặp đi lặp lại thường ngày thành giao diện Terminal Interactive siêu ngầu bằng Rich/Textual.",
        "difficulty": "Easy (3 giờ)",
        "tech_stack": "Python + Rich + Typer / Prompt-Toolkit",
        "vibe_score": 89
    },
    {
        "pattern": ["crawler", "scrape", "news", "digest"],
        "title": "📰 {keyword} Personalized Morning Briefing",
        "desc": "Hệ thống tự động gom tin tức, phân loại sentiment và xuất file PDF/HTML tóm tắt gửi về hòm thư mỗi buổi sáng.",
        "difficulty": "Easy (1 buổi tối)",
        "tech_stack": "BeautifulSoup + FastAPI + Jinja2",
        "vibe_score": 92
    }
]

class VibeEngine:
    def __init__(self):
        pass

    def extract_keywords(self, items: List[Dict[str, Any]]) -> List[str]:
        """Extract top trending keywords across all scraped items"""
        words = []
        stop_words = {
            "the", "a", "an", "and", "or", "to", "in", "of", "for", "with", "on", "at", 
            "by", "from", "is", "that", "this", "it", "as", "are", "be", "your", "you", 
            "new", "all", "via", "using", "how", "why", "what", "into", "can", "more", 
            "open", "source", "show", "hn", "github", "trending"
        }
        for it in items:
            text = f"{it.get('title', '')} {it.get('desc', '')} {it.get('language', '')}"
            cleaned = re.findall(r"[a-zA-Z]{3,}", text.lower())
            for w in cleaned:
                if w not in stop_words and len(w) > 3:
                    words.append(w)
        
        counter = Counter(words)
        return [word for word, count in counter.most_common(20)]

    def generate_sparks(self, items: List[Dict[str, Any]], count: int = 6) -> List[Dict[str, Any]]:
        """
        Generate spontaneous project sparks based on current trends.
        """
        top_keywords = self.extract_keywords(items)
        if not top_keywords:
            top_keywords = ["ai", "automation", "agent", "devtools", "minimalist", "crawler"]

        sparks = []
        used_titles = set()

        # Step 1: Match with trending items directly
        for item in items[:15]:
            title_lower = item.get("title", "").lower()
            desc_lower = item.get("desc", "").lower()
            combined = f"{title_lower} {desc_lower}"

            for recipe in VIBE_RECIPES:
                if any(p in combined for p in recipe["pattern"]):
                    kw = item.get("title", "").split("/")[-1].replace("-", " ").title()
                    spark_title = recipe["title"].format(keyword=kw[:25], topic=kw[:20])
                    if spark_title not in used_titles:
                        used_titles.add(spark_title)
                        sparks.append({
                            "title": spark_title,
                            "desc": recipe["desc"].format(keyword=kw[:25], topic=kw[:20]),
                            "inspiration_source": f"{item.get('source')}: {item.get('title')}",
                            "inspiration_url": item.get("url"),
                            "difficulty": recipe["difficulty"],
                            "tech_stack": recipe["tech_stack"],
                            "vibe_score": min(99, recipe["vibe_score"] + random.randint(0, 3)),
                            "tags": [p.capitalize() for p in recipe["pattern"][:3]]
                        })
                        break
            if len(sparks) >= count:
                break

        # Step 2: Fallback / Fill up to count if needed
        while len(sparks) < count:
            kw = random.choice(top_keywords).capitalize()
            recipe = random.choice(VIBE_RECIPES)
            spark_title = recipe["title"].format(keyword=kw, topic=kw.lower())
            if spark_title not in used_titles:
                used_titles.add(spark_title)
                sparks.append({
                    "title": spark_title,
                    "desc": recipe["desc"].format(keyword=kw, topic=kw.lower()),
                    "inspiration_source": f"Trend Keyword: {kw}",
                    "inspiration_url": "https://github.com/trending",
                    "difficulty": recipe["difficulty"],
                    "tech_stack": recipe["tech_stack"],
                    "vibe_score": random.randint(90, 98),
                    "tags": [kw, "Vibe Idea", "Trending"]
                })

        return sparks
