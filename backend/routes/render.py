from typing import Optional
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse
from backend.renderer.composer import render_video
from backend.db.database import get_db
from pathlib import Path
import uuid
import shutil

router = APIRouter(prefix="/api/render", tags=["render"])

_render_jobs = {}

async def _run_render(
    job_id: str,
    project_id: str,
    template: str,
    hook_text: str,
    cta_text: str,
    audio_path: Optional[str],
    duration: float,
):
    _render_jobs[job_id] = {"status": "rendering", "progress": 0}

    if not shutil.which("ffmpeg"):
        _render_jobs[job_id] = {"status": "error", "error": "FFmpeg not installed. Run: brew install ffmpeg"}
        return

    db = await get_db()
    try:
        cursor = await db.execute("SELECT screenshots_dir FROM projects WHERE id = ?", (project_id,))
        project = await cursor.fetchone()
    finally:
        await db.close()

    if not project:
        _render_jobs[job_id] = {"status": "error", "error": "project not found"}
        return

    ss_dir = Path(project["screenshots_dir"])
    screenshots = (
        sorted([
            str(f) for f in ss_dir.glob("*.*")
            if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
        ])
        if ss_dir.exists()
        else []
    )

    output_path = f"data/projects/{project_id}/output/{job_id}.mp4"

    try:
        render_video(template, screenshots, hook_text, cta_text, audio_path, output_path, duration)

        db2 = await get_db()
        try:
            await db2.execute(
                "INSERT INTO renders (id, project_id, template, hook_text, audio_path, output_path, duration, status) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (job_id, project_id, template, hook_text, audio_path, output_path, duration, "done"),
            )
            await db2.commit()
        finally:
            await db2.close()

        _render_jobs[job_id] = {"status": "done", "output_path": output_path}
    except Exception as e:
        _render_jobs[job_id] = {"status": "error", "error": str(e)}


@router.post("")
async def start_render(
    background_tasks: BackgroundTasks,
    project_id: str,
    template: str = "AppReveal",
    hook_text: str = "Это приложение взорвёт 🔥",
    cta_text: str = "Ссылка в био 👇",
    audio_path: str = "",
    duration: float = 30,
):
    job_id = uuid.uuid4().hex[:8]
    background_tasks.add_task(
        _run_render, job_id, project_id, template, hook_text, cta_text, audio_path or None, duration
    )
    return {"job_id": job_id, "status": "started"}


@router.get("/status/{job_id}")
async def render_status(job_id: str):
    return _render_jobs.get(job_id, {"status": "not_found"})


@router.get("/output/{job_id}")
async def render_output(job_id: str):
    job = _render_jobs.get(job_id)
    if not job or job.get("status") != "done":
        return {"error": "not ready"}
    return FileResponse(job["output_path"], media_type="video/mp4", filename=f"promo_{job_id}.mp4")


@router.get("/list/{project_id}")
async def list_renders(project_id: str):
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM renders WHERE project_id = ? ORDER BY created_at DESC", (project_id,)
        )
        rows = await cursor.fetchall()
    finally:
        await db.close()
    return [dict(r) for r in rows]
