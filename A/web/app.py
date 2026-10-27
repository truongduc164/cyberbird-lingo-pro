"""
FastAPI Backend for VibeRadar Web Dashboard & Video Automation Studio
"""
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional

import config
from core.github_scanner import GitHubScanner
from core.hn_scanner import HackerNewsScanner
from core.hf_scanner import HuggingFaceScanner
from core.devto_scanner import DevToScanner
from core.vibe_engine import VibeEngine
from core.storage import Storage
from core.report_generator import ReportGenerator
from video_engine.pipeline import run_video_pipeline

app = FastAPI(title="VibeRadar & Video Studio Dashboard", version="1.0.0")

storage = Storage()
engine = VibeEngine()
reporter = ReportGenerator()

class IdeaCreate(BaseModel):
    title: str
    desc: Optional[str] = ""
    tags: Optional[List[str]] = ["Vibe"]

class IdeaUpdateStatus(BaseModel):
    status: str

class VideoRequest(BaseModel):
    content: str
    is_raw_text: Optional[bool] = False
    lang: Optional[str] = "vi"
    ratio: Optional[str] = "9:16"

@app.get("/api/trends")
def get_trends():
    """Retrieve cached trend data, or run a quick scan if none exists"""
    data = storage.load_cache()
    if not data:
        data = trigger_full_scan()
    return data

@app.post("/api/scan")
def trigger_full_scan():
    """Trigger a live refresh scan of all sources"""
    gh = GitHubScanner()
    hn = HackerNewsScanner()
    hf = HuggingFaceScanner()
    devto = DevToScanner()

    all_items = []
    all_items.extend(gh.fetch_trending())
    all_items.extend(hn.fetch_all())
    all_items.extend(hf.fetch_all())
    all_items.extend(devto.fetch_top_articles())

    keywords = engine.extract_keywords(all_items)
    sparks = engine.generate_sparks(all_items, count=8)

    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_items": len(all_items),
        "keywords": keywords,
        "sparks": sparks,
        "items": all_items
    }

    storage.save_cache(data)
    reporter.generate_markdown(data)
    return data

@app.get("/api/sparks/regenerate")
def regenerate_sparks():
    """Regenerate fresh sparks from existing cached items"""
    data = storage.load_cache()
    if not data or not data.get("items"):
        data = trigger_full_scan()
    
    new_sparks = engine.generate_sparks(data["items"], count=8)
    data["sparks"] = new_sparks
    storage.save_cache(data)
    return {"sparks": new_sparks}

@app.get("/api/ideas")
def get_user_ideas():
    """Get all saved user ideas"""
    return storage.load_user_ideas()

@app.post("/api/ideas")
def add_user_idea(idea: IdeaCreate):
    """Add a new spontaneous user idea"""
    if not idea.title.strip():
        raise HTTPException(status_code=400, detail="Idea title cannot be empty")
    created = storage.add_user_idea(idea.title, idea.desc, idea.tags)
    return created

@app.patch("/api/ideas/{idea_id}/status")
def update_idea_status(idea_id: str, payload: IdeaUpdateStatus):
    """Update status of an idea (idea, building, done)"""
    success = storage.update_idea_status(idea_id, payload.status)
    if not success:
        raise HTTPException(status_code=404, detail="Idea not found")
    return {"status": "ok", "idea_id": idea_id, "new_status": payload.status}

@app.delete("/api/ideas/{idea_id}")
def delete_user_idea(idea_id: str):
    """Delete an idea"""
    success = storage.delete_user_idea(idea_id)
    if not success:
        raise HTTPException(status_code=404, detail="Idea not found")
    return {"status": "deleted", "idea_id": idea_id}

@app.get("/api/report/latest")
def get_latest_report():
    """Get the latest markdown report"""
    latest_file = config.REPORTS_DIR / "vibe_digest_latest.md"
    if latest_file.exists():
        with open(latest_file, "r", encoding="utf-8") as f:
            return {"markdown": f.read()}
    return {"markdown": "Chưa có báo cáo nào được tạo."}

# Video Automation Endpoints
@app.post("/api/video/generate")
def generate_video_api(req: VideoRequest):
    """Generate a short video from topic or text"""
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    try:
        res = run_video_pipeline(
            input_content=req.content,
            is_raw_text=req.is_raw_text,
            lang=req.lang or "vi",
            ratio=req.ratio or "9:16"
        )
        filename = Path(res["output_path"]).name
        res["video_url"] = f"/videos/{filename}"
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/video/list")
def list_videos_api():
    """List all created videos"""
    out_dir = BASE_DIR / "video_engine" / "output"
    videos = []
    if out_dir.exists():
        for f in sorted(out_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True):
            videos.append({
                "name": f.name,
                "url": f"/videos/{f.name}",
                "size_mb": round(f.stat().st_size / (1024 * 1024), 2),
                "created_at": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            })
    return videos

# Mount videos output directory
video_output_dir = BASE_DIR / "video_engine" / "output"
video_output_dir.mkdir(parents=True, exist_ok=True)
app.mount("/videos", StaticFiles(directory=str(video_output_dir)), name="videos")

# Mount static frontend
static_dir = BASE_DIR / "web" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
def serve_index():
    index_file = BASE_DIR / "web" / "static" / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "VibeRadar API is running. Static UI not found."}
