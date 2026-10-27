"""
Hugging Face Trending Scanner (AI Models & Spaces)
Uses official Hugging Face API
"""
import urllib.request
import json
import logging
from typing import List, Dict, Any
import config

logger = logging.getLogger(__name__)

class HuggingFaceScanner:
    def __init__(self):
        self.headers = {"User-Agent": config.USER_AGENT}

    def fetch_trending_models(self, limit: int = 6) -> List[Dict[str, Any]]:
        items = []
        try:
            url = f"https://huggingface.co/api/models?sort=trendingScore&direction=-1&limit={limit}"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            for model in data:
                model_id = model.get("id", "")
                items.append({
                    "id": f"hf_m_{model_id.replace('/', '_')}",
                    "source": "Hugging Face Model",
                    "title": model_id,
                    "url": f"https://huggingface.co/{model_id}",
                    "desc": f"Pipeline: {model.get('pipeline_tag', 'General AI')} | Downloads: {model.get('downloads', 0):,}",
                    "stars": str(model.get("likes", 0)),
                    "stars_period": f"{model.get('downloads', 0):,} DLs",
                    "language": model.get("pipeline_tag") or "AI Model",
                    "category": "AI / ML"
                })
        except Exception as e:
            logger.warning(f"Error fetching Hugging Face models: {e}")
        return items

    def fetch_trending_spaces(self, limit: int = 6) -> List[Dict[str, Any]]:
        items = []
        try:
            url = f"https://huggingface.co/api/spaces?sort=trendingScore&direction=-1&limit={limit}"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            for space in data:
                space_id = space.get("id", "")
                items.append({
                    "id": f"hf_s_{space_id.replace('/', '_')}",
                    "source": "Hugging Face Space",
                    "title": space_id,
                    "url": f"https://huggingface.co/spaces/{space_id}",
                    "desc": f"Interactive AI Demo / Web App by {space.get('author', 'Community')}",
                    "stars": str(space.get("likes", 0)),
                    "stars_period": "Trending Demo",
                    "language": "AI Web Demo",
                    "category": "Interactive AI"
                })
        except Exception as e:
            logger.warning(f"Error fetching Hugging Face spaces: {e}")
        return items

    def fetch_all(self) -> List[Dict[str, Any]]:
        return self.fetch_trending_models(6) + self.fetch_trending_spaces(6)
