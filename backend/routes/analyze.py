from typing import Optional, List
from fastapi import APIRouter, BackgroundTasks
from backend.db.database import get_db
from backend.analyzer.video_analyzer import analyze_video
from backend.analyzer.pattern_detector import detect_patterns
import json

router = APIRouter(prefix="/api", tags=["analyze"])

_analyze_status = {"running": False, "progress": 0, "total": 0}


async def _run_analysis(video_ids: Optional[List[str]]):
    global _analyze_status
    db = await get_db()

    if video_ids:
        placeholders = ",".join("?" for _ in video_ids)
        rows = await db.execute_fetchall(
            f"SELECT * FROM trends WHERE id IN ({placeholders}) AND file_path IS NOT NULL", video_ids
        )
    else:
        rows = await db.execute_fetchall(
            "SELECT * FROM trends WHERE analyzed = 0 AND file_path IS NOT NULL ORDER BY views DESC LIMIT 20"
        )

    videos = [dict(r) for r in rows]
    _analyze_status = {"running": True, "progress": 0, "total": len(videos)}

    try:
        for v in videos:
            result = analyze_video(v["file_path"])
            if result:
                await db.execute(
                    "UPDATE trends SET analyzed = 1, analysis = ? WHERE id = ?",
                    (json.dumps(result, ensure_ascii=False), v["id"]),
                )
                await db.commit()
            _analyze_status["progress"] += 1
    except Exception as e:
        print(f"Analysis error: {e}")
    finally:
        _analyze_status["running"] = False
        await db.close()


@router.post("/analyze")
async def start_analysis(background_tasks: BackgroundTasks):
    if _analyze_status["running"]:
        return {"error": "analysis already running"}
    background_tasks.add_task(_run_analysis, None)
    return {"status": "started"}


@router.get("/analyze/status")
async def analysis_status():
    return _analyze_status


@router.get("/patterns")
async def get_patterns():
    db = await get_db()
    rows = await db.execute_fetchall("SELECT analysis FROM trends WHERE analyzed = 1 AND analysis IS NOT NULL")
    await db.close()
    analyses = []
    for r in rows:
        try:
            analyses.append(json.loads(dict(r)["analysis"]))
        except Exception:
            pass
    return detect_patterns(analyses)
