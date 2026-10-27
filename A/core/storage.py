"""
Storage module for caching trending data and persisting user vibe ideas.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import config

class Storage:
    def __init__(self):
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.cache_file = config.DATA_DIR / "trends_cache.json"
        self.ideas_file = config.DATA_DIR / "my_vibe_ideas.json"
        self._init_files()

    def _init_files(self):
        if not self.ideas_file.exists():
            default_ideas = [
                {
                    "id": str(uuid.uuid4())[:8],
                    "title": "⚡ GitHub Trending Telegram/Discord Bot",
                    "desc": "Tự động gửi digest 5 repo AI hot nhất vào 8h sáng mỗi ngày vào channel cá nhân.",
                    "tags": ["Automation", "Bot", "AI"],
                    "status": "idea",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                },
                {
                    "id": str(uuid.uuid4())[:8],
                    "title": "🧠 Local LLM Prompt Benchmark Studio",
                    "desc": "Một tool GUI mini (PySide hoặc Streamlit) so sánh câu trả lời của 3 model Ollama cùng lúc.",
                    "tags": ["Local LLM", "UI Tool"],
                    "status": "building",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
            ]
            self.save_user_ideas(default_ideas)

    def load_cache(self) -> Optional[Dict[str, Any]]:
        if not self.cache_file.exists():
            return None
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def save_cache(self, data: Dict[str, Any]):
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def load_user_ideas(self) -> List[Dict[str, Any]]:
        if not self.ideas_file.exists():
            return []
        try:
            with open(self.ideas_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_user_ideas(self, ideas: List[Dict[str, Any]]):
        try:
            with open(self.ideas_file, "w", encoding="utf-8") as f:
                json.dump(ideas, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving user ideas: {e}")

    def add_user_idea(self, title: str, desc: str = "", tags: List[str] = None) -> Dict[str, Any]:
        ideas = self.load_user_ideas()
        new_idea = {
            "id": str(uuid.uuid4())[:8],
            "title": title.strip(),
            "desc": desc.strip(),
            "tags": tags or ["Vibe"],
            "status": "idea",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        ideas.insert(0, new_idea)
        self.save_user_ideas(ideas)
        return new_idea

    def update_idea_status(self, idea_id: str, new_status: str) -> bool:
        ideas = self.load_user_ideas()
        updated = False
        for it in ideas:
            if it["id"] == idea_id:
                it["status"] = new_status
                updated = True
                break
        if updated:
            self.save_user_ideas(ideas)
        return updated

    def delete_user_idea(self, idea_id: str) -> bool:
        ideas = self.load_user_ideas()
        filtered = [it for it in ideas if it["id"] != idea_id]
        if len(filtered) != len(ideas):
            self.save_user_ideas(filtered)
            return True
        return False
