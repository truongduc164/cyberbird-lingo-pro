"""
Report Generator for VibeRadar
Outputs beautiful Markdown and HTML reports of trending topics and sparked ideas.
"""
from datetime import datetime
from typing import Dict, Any, List
import config

class ReportGenerator:
    def __init__(self):
        config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    def generate_markdown(self, data: Dict[str, Any]) -> str:
        timestamp = data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M"))
        items = data.get("items", [])
        sparks = data.get("sparks", [])
        keywords = data.get("keywords", [])

        md = []
        md.append(f"# 🚀 VibeRadar — Báo Cáo Xu Hướng & Ý Tưởng Nảy Ra ({timestamp})\n")
        md.append("> *Tự động quét từ GitHub Trending, Hacker News, Hugging Face và Dev.to*\n")
        
        md.append("## 💡 Tia Sáng Ý Tưởng Mới Nảy Ra (Vibe Sparks)")
        md.append("Dưới đây là các ý tưởng dự án có thể build nhanh dựa trên các trend nóng hôm nay:\n")
        
        for i, spark in enumerate(sparks, 1):
            md.append(f"### {i}. {spark['title']}")
            md.append(f"- **Mô tả**: {spark['desc']}")
            md.append(f"- **Nguồn cảm hứng**: [{spark['inspiration_source']}]({spark['inspiration_url']})")
            md.append(f"- **Độ khó**: `{spark['difficulty']}` | **Tech Stack**: `{spark['tech_stack']}` | **Vibe Score**: ⭐ `{spark['vibe_score']}/100`")
            md.append(f"- **Tags**: {', '.join([f'`#{t}`' for t in spark.get('tags', [])])}\n")

        md.append("## 🔍 Từ Khoá Nóng Nhất Hôm Nay (Hot Keywords)")
        md.append(" ".join([f"`#{kw}`" for kw in keywords[:12]]) + "\n")

        md.append("## 🌟 Danh Sách Xu Hướng Chi Tiết\n")
        
        # Group by source
        grouped = {}
        for it in items:
            src = it.get("source", "Khác")
            grouped.setdefault(src, []).append(it)

        for src, group_items in grouped.items():
            md.append(f"### 📌 {src}")
            for it in group_items:
                md.append(f"- **[{it['title']}]({it['url']})** ({it.get('language', 'General')})")
                md.append(f"  - *{it.get('desc', '')}*")
                md.append(f"  - 📈 {it.get('stars', '0')} tương tác | {it.get('stars_period', '')}\n")

        content = "\n".join(md)

        # Save files
        date_str = datetime.now().strftime("%Y-%m-%d")
        daily_file = config.REPORTS_DIR / f"vibe_digest_{date_str}.md"
        latest_file = config.REPORTS_DIR / "vibe_digest_latest.md"

        with open(daily_file, "w", encoding="utf-8") as f:
            f.write(content)
        with open(latest_file, "w", encoding="utf-8") as f:
            f.write(content)

        return content
