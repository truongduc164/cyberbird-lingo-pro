"""
Hacker News Scanner (Show HN & Top Tech Stories)
Uses official Firebase REST API (fast, free, no auth required).
"""
import urllib.request
import json
import logging
from typing import List, Dict, Any
import config

logger = logging.getLogger(__name__)

class HackerNewsScanner:
    def __init__(self):
        self.headers = {"User-Agent": config.USER_AGENT}
        self.base_url = "https://hacker-news.firebaseio.com/v0"

    def fetch_item(self, item_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/item/{item_id}.json"
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def fetch_show_hn(self, limit: int = 8) -> List[Dict[str, Any]]:
        """Fetch latest 'Show HN' items (new apps, tools made by developers)"""
        items = []
        try:
            url = f"{self.base_url}/showstories.json"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=7) as resp:
                ids = json.loads(resp.read().decode("utf-8"))[:limit]

            for item_id in ids:
                try:
                    data = self.fetch_item(item_id)
                    if not data:
                        continue
                    items.append({
                        "id": f"hn_{data.get('id')}",
                        "source": "Show HN",
                        "title": data.get("title", ""),
                        "url": data.get("url") or f"https://news.ycombinator.com/item?id={data.get('id')}",
                        "desc": f"Showcase by @{data.get('by', 'anon')} ({data.get('score', 0)} points, {len(data.get('kids', []))} comments)",
                        "stars": str(data.get("score", 0)),
                        "stars_period": f"{len(data.get('kids', []))} comments",
                        "language": "Indie Maker",
                        "category": "Show HN"
                    })
                except Exception as ex:
                    logger.debug(f"Failed fetching HN item {item_id}: {ex}")
        except Exception as e:
            logger.warning(f"Error fetching Show HN: {e}")
        return items

    def fetch_top_stories(self, limit: int = 8) -> List[Dict[str, Any]]:
        """Fetch top general tech stories"""
        items = []
        try:
            url = f"{self.base_url}/topstories.json"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=7) as resp:
                ids = json.loads(resp.read().decode("utf-8"))[:limit]

            for item_id in ids:
                try:
                    data = self.fetch_item(item_id)
                    if not data:
                        continue
                    items.append({
                        "id": f"hn_top_{data.get('id')}",
                        "source": "Hacker News",
                        "title": data.get("title", ""),
                        "url": data.get("url") or f"https://news.ycombinator.com/item?id={data.get('id')}",
                        "desc": f"By @{data.get('by', 'anon')} ({data.get('score', 0)} upvotes)",
                        "stars": str(data.get("score", 0)),
                        "stars_period": f"{len(data.get('kids', []))} comments",
                        "language": "Tech News",
                        "category": "Hot Discussion"
                    })
                except Exception as ex:
                    logger.debug(f"Failed fetching HN top item {item_id}: {ex}")
        except Exception as e:
            logger.warning(f"Error fetching HN top stories: {e}")
        return items

    def fetch_all(self) -> List[Dict[str, Any]]:
        return self.fetch_show_hn(limit=7) + self.fetch_top_stories(limit=7)
