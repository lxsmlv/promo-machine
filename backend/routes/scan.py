from typing import Optional, List
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse
from backend.scanner.downloader import download_video
from backend.db.database import get_db
import json

router = APIRouter(prefix="/api", tags=["scan"])

_scan_status = {"running": False, "progress": 0, "total": 0, "results": []}


async def _run_scan(urls: List[str], platform: str):
    """Background task to scan and download videos."""
    global _scan_status
    _scan_status = {"running": True, "progress": 0, "total": len(urls), "results": []}
    output_dir = f"data/downloads/{platform}"

    try:
        db = await get_db()
        for url in urls:
            meta = download_video(url, output_dir)
            if meta:
                video_id = meta["id"]
                await db.execute(
                    """INSERT OR REPLACE INTO trends
                    (id, platform, url, views, likes, shares, comments, duration,
                     hashtags, description, file_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (video_id, platform, meta.get("url"), meta.get("views", 0),
                     meta.get("likes", 0), meta.get("shares", 0), meta.get("comments", 0),
                     meta.get("duration", 0), json.dumps(meta.get("tags", [])),
                     meta.get("description"), meta.get("file_path")),
                )
                _scan_status["results"].append(meta)
            _scan_status["progress"] += 1
        await db.commit()
        await db.close()
    except Exception as e:
        print(f"Scan error: {e}")
    finally:
        _scan_status["running"] = False


@router.post("/scan")
async def start_scan(background_tasks: BackgroundTasks, urls: str = "", platform: str = "tiktok"):
    """Start scanning. Pass comma-separated TikTok/VK video URLs."""
    if _scan_status["running"]:
        return {"error": "scan already running"}
    url_list = [u.strip() for u in urls.split(",") if u.strip()]
    if not url_list:
        return {"error": "no URLs provided. Pass comma-separated video URLs in 'urls' param"}
    background_tasks.add_task(_run_scan, url_list, platform)
    return {"status": "started", "count": len(url_list)}


@router.get("/scan/status")
async def scan_status():
    """Get current scan status and progress."""
    return _scan_status


@router.get("/trends")
async def list_trends(limit: int = 50):
    """List trending videos from database."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM trends ORDER BY views DESC LIMIT ?", (limit,)
    )
    rows = await cursor.fetchall()
    await db.close()
    return [dict(r) for r in rows]


@router.get("/trends/{video_id}/video")
async def stream_video(video_id: str):
    """Stream a downloaded video by ID."""
    db = await get_db()
    cursor = await db.execute("SELECT file_path FROM trends WHERE id = ?", (video_id,))
    row = await cursor.fetchone()
    await db.close()
    if not row:
        return {"error": "not found"}
    file_path = dict(row).get("file_path")
    if not file_path:
        return {"error": "video not downloaded"}
    return FileResponse(file_path, media_type="video/mp4")
