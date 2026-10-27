"""
GitHub Trending & Rising Repositories Scanner
"""
import urllib.request
import json
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import config

logger = logging.getLogger(__name__)

class GitHubScanner:
    def __init__(self):
        self.headers = {"User-Agent": config.USER_AGENT}

    def fetch_trending(self, language: str = "", since: str = "daily") -> List[Dict[str, Any]]:
        """
        Fetch trending repos from GitHub Trending page.
        language: e.g. '', 'python', 'javascript', 'typescript', 'rust', 'go'
        since: 'daily', 'weekly', 'monthly'
        """
        url = "https://github.com/trending"
        if language:
            url += f"/{language}"
        url += f"?since={since}"

        items = []
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8")

            soup = BeautifulSoup(html, "html.parser")
            rows = soup.select("article.Box-row")

            for row in rows[:config.GITHUB_TRENDING_LIMIT]:
                # Repo title & link
                h2 = row.select_one("h2 a")
                if not h2:
                    continue
                repo_name = "".join(h2.text.split())
                repo_url = f"https://github.com/{repo_name}"

                # Description
                p_desc = row.select_one("p")
                desc = p_desc.text.strip() if p_desc else "No description provided."

                # Language
                lang_span = row.select_one("span[itemprop='programmingLanguage']")
                prog_lang = lang_span.text.strip() if lang_span else "Unknown"

                # Stars total
                stars_total = 0
                stars_today = "0 stars today"
                star_links = row.select("a.Link--muted")
                for sl in star_links:
                    href = sl.get("href", "")
                    if "stargazers" in href:
                        stars_total = sl.text.strip().replace(",", "")

                # Stars gained today/period
                float_right = row.select_one("span.d-inline-block.float-sm-right")
                if float_right:
                    stars_today = float_right.text.strip()

                items.append({
                    "id": f"gh_{repo_name.replace('/', '_')}",
                    "source": "GitHub Trending",
                    "title": repo_name,
                    "url": repo_url,
                    "desc": desc,
                    "stars": stars_total,
                    "stars_period": stars_today,
                    "language": prog_lang,
                    "category": "Open Source Code"
                })
        except Exception as e:
            logger.warning(f"Error scraping GitHub trending ({url}): {e}")

        # If trending returned nothing (blocked or changed layout), fallback to search API
        if not items:
            items = self.fetch_breakout_repos()

        return items

    def fetch_breakout_repos(self) -> List[Dict[str, Any]]:
        """
        Fetch newly rising breakout repositories created/updated in the last 14 days.
        """
        items = []
        try:
            since_date = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
            # Query for active AI/Tool projects with good traction
            query = f"stars:>30+created:>{since_date}"
            url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page={config.GITHUB_RISING_LIMIT}"
            
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            for repo in data.get("items", []):
                items.append({
                    "id": f"gh_api_{repo['id']}",
                    "source": "GitHub Rising",
                    "title": repo.get("full_name", ""),
                    "url": repo.get("html_url", ""),
                    "desc": repo.get("description") or "No description",
                    "stars": str(repo.get("stargazers_count", 0)),
                    "stars_period": f"{repo.get('forks_count', 0)} forks",
                    "language": repo.get("language") or "Various",
                    "category": "Rising Star"
                })
        except Exception as e:
            logger.warning(f"Error calling GitHub Search API: {e}")

        return items
