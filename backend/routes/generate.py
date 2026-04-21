import json
from fastapi import APIRouter
from backend.generator.script_writer import generate_scripts
from backend.generator.hook_writer import generate_hooks
from backend.generator.copy_writer import generate_copy
from backend.analyzer.pattern_detector import detect_patterns
from backend.db.database import get_db

router = APIRouter(prefix="/api/generate", tags=["generate"])


@router.post("/scripts")
async def gen_scripts(project_id: str, count: int = 5, duration: int = 30):
    db = await get_db()
    project = await db.execute_fetchone(
        "SELECT * FROM projects WHERE id = ?", (project_id,)
    )
    if not project:
        await db.close()
        return {"error": "project not found"}
    p = dict(project)

    rows = await db.execute_fetchall(
        "SELECT analysis FROM trends WHERE analyzed = 1 AND analysis IS NOT NULL"
    )
    await db.close()

    analyses = []
    for r in rows:
        try:
            analyses.append(json.loads(dict(r)["analysis"]))
        except Exception:
            pass
    patterns = detect_patterns(analyses) if analyses else {}

    scripts = generate_scripts(
        p["name"],
        p["description"],
        p.get("features", "[]"),
        p.get("target_audience", ""),
        patterns,
        count,
        duration,
    )
    return {"scripts": scripts}


@router.post("/hooks")
async def gen_hooks(project_id: str, count: int = 20):
    db = await get_db()
    project = await db.execute_fetchone(
        "SELECT * FROM projects WHERE id = ?", (project_id,)
    )
    await db.close()
    if not project:
        return {"error": "project not found"}
    p = dict(project)
    hooks = generate_hooks(p["name"], p["description"], count)
    return {"hooks": hooks}


@router.post("/copy")
async def gen_copy(project_id: str):
    db = await get_db()
    project = await db.execute_fetchone(
        "SELECT * FROM projects WHERE id = ?", (project_id,)
    )
    await db.close()
    if not project:
        return {"error": "project not found"}
    p = dict(project)
    copy = generate_copy(p["name"], p["description"], p.get("features", "[]"))
    return copy
