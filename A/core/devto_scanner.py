"""
Dev.to Trending & Maker Articles Scanner
Uses official Dev.to API
"""
import urllib.request
import json
import logging
from typing import List, Dict, Any
import config

logger = logging.getLogger(__name__)

class DevToScanner:
    def __init__(self):
        self.headers = {"User-Agent": config.USER_AGENT}

    def fetch_top_articles(self, limit: int = 10) -> List[Dict[str, Any]]:
        items = []
        try:
            url = f"https://dev.to/api/articles?top=1&per_page={limit}"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            for art in data:
                items.append({
                    "id": f"devto_{art.get('id')}",
                    "source": "Dev.to Trending",
                    "title": art.get("title", ""),
                    "url": art.get("url", ""),
                    "desc": art.get("description") or f"By {art.get('user', {}).get('name', 'Dev')}",
                    "stars": str(art.get("positive_reactions_count", 0)),
                    "stars_period": f"{art.get('comments_count', 0)} comments",
                    "language": (art.get("tag_list") or ["General"])[0] if art.get("tag_list") else "Dev",
                    "category": "Tutorial & Thoughts"
                })
        except Exception as e:
            logger.warning(f"Error fetching Dev.to: {e}")
        return items
