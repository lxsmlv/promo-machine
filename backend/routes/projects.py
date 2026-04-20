from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form
from backend.db.database import get_db
import uuid
import shutil
from pathlib import Path

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("")
async def list_projects():
    db = await get_db()
    cursor = await db.execute("SELECT * FROM projects ORDER BY created_at DESC")
    rows = await cursor.fetchall()
    await db.close()
    return [dict(r) for r in rows]

@router.post("")
async def create_project(
    name: str = Form(...),
    description: str = Form(""),
    features: str = Form("[]"),
    target_audience: str = Form(""),
    app_url: str = Form(""),
):
    project_id = str(uuid.uuid4())[:8]
    screenshots_dir = f"data/projects/{project_id}/screenshots"
    Path(screenshots_dir).mkdir(parents=True, exist_ok=True)
    Path(f"data/projects/{project_id}/output").mkdir(parents=True, exist_ok=True)

    db = await get_db()
    await db.execute(
        "INSERT INTO projects (id, name, description, features, target_audience, app_url, screenshots_dir) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (project_id, name, description, features, target_audience, app_url, screenshots_dir),
    )
    await db.commit()
    await db.close()
    return {"id": project_id, "name": name}

@router.get("/{project_id}")
async def get_project(project_id: str):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    row = await cursor.fetchone()
    await db.close()
    if not row:
        return {"error": "not found"}
    project = dict(row)
    ss_dir = Path(project["screenshots_dir"]) if project.get("screenshots_dir") else None
    project["screenshots"] = sorted([str(f) for f in ss_dir.glob("*.*")]) if ss_dir and ss_dir.exists() else []
    return project

@router.post("/{project_id}/screenshots")
async def upload_screenshots(project_id: str, files: List[UploadFile] = File(...)):
    db = await get_db()
    cursor = await db.execute("SELECT screenshots_dir FROM projects WHERE id = ?", (project_id,))
    row = await cursor.fetchone()
    await db.close()
    if not row:
        return {"error": "not found"}

    ss_dir = Path(dict(row)["screenshots_dir"])
    ss_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for f in files:
        dest = ss_dir / f.filename
        with open(dest, "wb") as out:
            shutil.copyfileobj(f.file, out)
        saved.append(str(dest))
    return {"uploaded": saved}

@router.delete("/{project_id}")
async def delete_project(project_id: str):
    db = await get_db()
    await db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    await db.commit()
    await db.close()
    project_dir = Path(f"data/projects/{project_id}")
    if project_dir.exists():
        shutil.rmtree(project_dir)
    return {"deleted": project_id}
