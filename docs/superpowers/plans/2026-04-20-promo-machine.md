# Промо-машина — План реализации

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Десктопный инструмент для автоматической генерации вирусных промо-роликов мобильных приложений.

**Architecture:** Python FastAPI бэкенд + React Vite фронт. Запуск через `python main.py` → localhost. 5 модулей: Scanner (сбор трендов), Analyzer (AI разбор), Generator (сценарии/тексты), Audio (TTS/микс), Renderer (видео сборка).

**Tech Stack:** Python 3.12, FastAPI, React, Vite, Tailwind, moviepy, FFmpeg, OpenAI API, edge-tts, TikTokApi, yt-dlp, SQLite.

---

## Предварительные требования

Перед началом установить:
```bash
brew install ffmpeg python@3.12
```

OpenAI API ключ получить на platform.openai.com и вставить в config.yaml.

---

### Task 1: Инициализация проекта — Python бэкенд

**Files:**
- Create: `backend/__init__.py`
- Create: `backend/app.py`
- Create: `backend/db/__init__.py`
- Create: `backend/db/database.py`
- Create: `backend/db/models.py`
- Create: `main.py`
- Create: `requirements.txt`
- Create: `config.yaml`
- Delete: `src/`, `package.json`, `package-lock.json`, `tsconfig.json`, `node_modules/`, `input/`, `output/`, `out/`

- [ ] **Step 1: Удалить старый Node.js проект**

```bash
cd promo-machine
rm -rf src/ node_modules/ input/ output/ out/ package.json package-lock.json tsconfig.json
```

- [ ] **Step 2: Создать структуру директорий**

```bash
mkdir -p backend/{routes,scanner,analyzer,generator,audio,renderer/templates,db}
mkdir -p frontend
mkdir -p assets/{fonts,frames,sounds/{energetic,chill,dramatic}}
mkdir -p data/{downloads/{tiktok,vk},projects}
touch backend/__init__.py backend/routes/__init__.py backend/scanner/__init__.py
touch backend/analyzer/__init__.py backend/generator/__init__.py
touch backend/audio/__init__.py backend/renderer/__init__.py backend/db/__init__.py
touch backend/renderer/templates/__init__.py
```

- [ ] **Step 3: Создать requirements.txt**

```
fastapi>=0.115
uvicorn[standard]>=0.34
openai>=1.60
moviepy>=2.1
Pillow>=11.0
pydub>=0.25
edge-tts>=7.0
yt-dlp>=2024.12
TikTokApi>=7.3
vk-api>=11.9
aiosqlite>=0.20
python-multipart>=0.0.18
httpx>=0.28
playwright>=1.49
pyyaml>=6.0
```

- [ ] **Step 4: Создать виртуальное окружение и установить зависимости**

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

- [ ] **Step 5: Создать config.yaml**

```yaml
openai_api_key: "sk-YOUR-KEY-HERE"
data_dir: "./data"
downloads_dir: "./data/downloads"
projects_dir: "./data/projects"
db_path: "./data/promo.db"
host: "127.0.0.1"
port: 8000
frontend_port: 5173
```

- [ ] **Step 6: Создать backend/db/database.py**

```python
import aiosqlite
import yaml
from pathlib import Path

_db_path: str | None = None

def get_db_path() -> str:
    global _db_path
    if _db_path is None:
        config_path = Path(__file__).parent.parent.parent / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        _db_path = config.get("db_path", "./data/promo.db")
    return _db_path

async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(get_db_path())
    db.row_factory = aiosqlite.Row
    return db
```

- [ ] **Step 7: Создать backend/db/models.py**

```python
SCHEMA = """
CREATE TABLE IF NOT EXISTS trends (
    id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    url TEXT,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    duration REAL DEFAULT 0,
    hashtags TEXT DEFAULT '[]',
    audio_id TEXT,
    audio_name TEXT,
    description TEXT,
    file_path TEXT,
    analyzed INTEGER DEFAULT 0,
    analysis TEXT,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    features TEXT DEFAULT '[]',
    target_audience TEXT DEFAULT '',
    app_url TEXT DEFAULT '',
    screenshots_dir TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS renders (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    template TEXT NOT NULL,
    hook_text TEXT,
    script TEXT DEFAULT '{}',
    audio_path TEXT,
    output_path TEXT,
    duration REAL DEFAULT 30,
    status TEXT DEFAULT 'pending',
    platform_copy TEXT DEFAULT '{}',
    hashtags TEXT DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
"""

async def init_db(db):
    await db.executescript(SCHEMA)
    await db.commit()
```

- [ ] **Step 8: Создать backend/app.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from backend.db.database import get_db
from backend.db.models import init_db

app = FastAPI(title="Promo Machine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    Path("data/downloads/tiktok").mkdir(parents=True, exist_ok=True)
    Path("data/downloads/vk").mkdir(parents=True, exist_ok=True)
    Path("data/projects").mkdir(parents=True, exist_ok=True)
    db = await get_db()
    await init_db(db)
    await db.close()

@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 9: Создать main.py**

```python
import subprocess
import sys
import webbrowser
import time
import yaml
from pathlib import Path

def main():
    config_path = Path("config.yaml")
    if not config_path.exists():
        print("ERROR: config.yaml not found. Copy from config.example.yaml")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    host = config.get("host", "127.0.0.1")
    port = config.get("port", 8000)

    print(f"\n🚀 Promo Machine starting at http://{host}:{port}\n")

    # Open browser after 2 sec delay
    import threading
    threading.Timer(2, lambda: webbrowser.open(f"http://{host}:{port}")).start()

    import uvicorn
    uvicorn.run("backend.app:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    main()
```

- [ ] **Step 10: Проверить запуск**

```bash
source venv/bin/activate
python main.py
```

Открыть http://localhost:8000/api/health — ожидается `{"status": "ok"}`.

- [ ] **Step 11: Commit**

```bash
git init
echo "venv/\ndata/\n__pycache__/\n*.pyc\n.env\nnode_modules/" > .gitignore
git add -A
git commit -m "feat: init promo-machine — FastAPI + SQLite skeleton"
```

---

### Task 2: CRUD проектов — бэкенд

**Files:**
- Create: `backend/routes/projects.py`
- Modify: `backend/app.py`

- [ ] **Step 1: Создать backend/routes/projects.py**

```python
from fastapi import APIRouter, UploadFile, File, Form
from backend.db.database import get_db
import uuid
import json
import shutil
from pathlib import Path

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("")
async def list_projects():
    db = await get_db()
    rows = await db.execute_fetchall("SELECT * FROM projects ORDER BY created_at DESC")
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
    row = await db.execute_fetchone("SELECT * FROM projects WHERE id = ?", (project_id,))
    await db.close()
    if not row:
        return {"error": "not found"}, 404
    project = dict(row)
    # List screenshots
    ss_dir = Path(project["screenshots_dir"]) if project["screenshots_dir"] else None
    project["screenshots"] = sorted([str(f) for f in ss_dir.glob("*.*")]) if ss_dir and ss_dir.exists() else []
    return project

@router.post("/{project_id}/screenshots")
async def upload_screenshots(project_id: str, files: list[UploadFile] = File(...)):
    db = await get_db()
    row = await db.execute_fetchone("SELECT screenshots_dir FROM projects WHERE id = ?", (project_id,))
    await db.close()
    if not row:
        return {"error": "not found"}, 404

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
```

- [ ] **Step 2: Подключить роут в backend/app.py**

Добавить после middleware:

```python
from backend.routes.projects import router as projects_router
app.include_router(projects_router)
```

- [ ] **Step 3: Проверить**

```bash
# Создать проект
curl -X POST http://localhost:8000/api/projects -F "name=BabyFace AI" -F "description=AI генерация ребёнка"

# Список проектов
curl http://localhost:8000/api/projects
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: projects CRUD + screenshot upload"
```

---

### Task 3: Scanner — TikTok + yt-dlp

**Files:**
- Create: `backend/scanner/tiktok.py`
- Create: `backend/scanner/downloader.py`
- Create: `backend/routes/scan.py`
- Modify: `backend/app.py`

- [ ] **Step 1: Создать backend/scanner/downloader.py**

```python
import subprocess
import json
from pathlib import Path

def download_video(url: str, output_dir: str) -> dict | None:
    """Download video via yt-dlp, return metadata dict or None."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_template = str(output_dir / "%(id)s.%(ext)s")

    try:
        # Get metadata first
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-download", url],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return None
        meta = json.loads(result.stdout)

        # Download video
        subprocess.run(
            ["yt-dlp", "-o", output_template, "--no-check-certificate", url],
            capture_output=True, timeout=120,
        )

        video_id = meta.get("id", "unknown")
        ext = meta.get("ext", "mp4")
        file_path = output_dir / f"{video_id}.{ext}"

        return {
            "id": video_id,
            "url": url,
            "title": meta.get("title", ""),
            "description": meta.get("description", ""),
            "views": meta.get("view_count", 0),
            "likes": meta.get("like_count", 0),
            "comments": meta.get("comment_count", 0),
            "duration": meta.get("duration", 0),
            "uploader": meta.get("uploader", ""),
            "tags": meta.get("tags", []),
            "file_path": str(file_path) if file_path.exists() else None,
        }
    except Exception as e:
        print(f"Download error: {e}")
        return None
```

- [ ] **Step 2: Создать backend/scanner/tiktok.py**

```python
from TikTokApi import TikTokApi
import asyncio
from backend.scanner.downloader import download_video

async def scan_tiktok_hashtag(hashtag: str, count: int = 20) -> list[dict]:
    """Scan TikTok for trending videos by hashtag."""
    results = []

    try:
        async with TikTokApi() as api:
            await api.create_sessions(num_sessions=1, sleep_after=3)
            tag = api.hashtag(name=hashtag)

            async for video in tag.videos(count=count):
                video_data = video.as_dict
                stats = video_data.get("stats", {})
                music = video_data.get("music", {})

                results.append({
                    "id": video_data.get("id"),
                    "url": f"https://www.tiktok.com/@{video_data.get('author', {}).get('uniqueId', '')}/video/{video_data.get('id')}",
                    "views": stats.get("playCount", 0),
                    "likes": stats.get("diggCount", 0),
                    "shares": stats.get("shareCount", 0),
                    "comments": stats.get("commentCount", 0),
                    "duration": video_data.get("video", {}).get("duration", 0),
                    "description": video_data.get("desc", ""),
                    "hashtags": [c.get("hashtagName", "") for c in video_data.get("challenges", [])],
                    "audio_id": music.get("id"),
                    "audio_name": music.get("title"),
                })
    except Exception as e:
        print(f"TikTok scan error: {e}")

    return sorted(results, key=lambda x: x.get("views", 0), reverse=True)

async def scan_and_download(hashtag: str, count: int = 10, output_dir: str = "data/downloads/tiktok") -> list[dict]:
    """Scan + download top videos."""
    videos = await scan_tiktok_hashtag(hashtag, count * 2)
    downloaded = []

    for video in videos[:count]:
        if not video.get("url"):
            continue
        meta = download_video(video["url"], output_dir)
        if meta and meta.get("file_path"):
            video["file_path"] = meta["file_path"]
            downloaded.append(video)

    return downloaded
```

- [ ] **Step 3: Создать backend/routes/scan.py**

```python
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse
from backend.scanner.tiktok import scan_and_download
from backend.db.database import get_db
import json

router = APIRouter(prefix="/api", tags=["scan"])

_scan_status = {"running": False, "progress": 0, "total": 0, "results": []}

async def _run_scan(keywords: str, count: int, platform: str):
    global _scan_status
    _scan_status = {"running": True, "progress": 0, "total": count, "results": []}

    try:
        if platform in ("tiktok", "both"):
            videos = await scan_and_download(keywords, count)
            db = await get_db()
            for v in videos:
                await db.execute(
                    """INSERT OR REPLACE INTO trends
                    (id, platform, url, views, likes, shares, comments, duration, hashtags, audio_id, audio_name, description, file_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (v["id"], "tiktok", v.get("url"), v.get("views", 0), v.get("likes", 0),
                     v.get("shares", 0), v.get("comments", 0), v.get("duration", 0),
                     json.dumps(v.get("hashtags", [])), v.get("audio_id"), v.get("audio_name"),
                     v.get("description"), v.get("file_path")),
                )
                _scan_status["progress"] += 1
                _scan_status["results"].append(v)
            await db.commit()
            await db.close()
    finally:
        _scan_status["running"] = False

@router.post("/scan")
async def start_scan(background_tasks: BackgroundTasks, keywords: str = "app promo", count: int = 10, platform: str = "tiktok"):
    if _scan_status["running"]:
        return {"error": "scan already running"}
    background_tasks.add_task(_run_scan, keywords, count, platform)
    return {"status": "started", "keywords": keywords, "count": count}

@router.get("/scan/status")
async def scan_status():
    return _scan_status

@router.get("/trends")
async def list_trends(limit: int = 50):
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT * FROM trends ORDER BY views DESC LIMIT ?", (limit,)
    )
    await db.close()
    return [dict(r) for r in rows]

@router.get("/trends/{video_id}/video")
async def stream_video(video_id: str):
    db = await get_db()
    row = await db.execute_fetchone("SELECT file_path FROM trends WHERE id = ?", (video_id,))
    await db.close()
    if not row or not dict(row).get("file_path"):
        return {"error": "not found"}, 404
    return FileResponse(dict(row)["file_path"], media_type="video/mp4")
```

- [ ] **Step 4: Подключить роут в backend/app.py**

```python
from backend.routes.scan import router as scan_router
app.include_router(scan_router)
```

- [ ] **Step 5: Проверить**

```bash
curl -X POST "http://localhost:8000/api/scan?keywords=mobile+app&count=5&platform=tiktok"
# Подождать 30 сек
curl http://localhost:8000/api/scan/status
curl http://localhost:8000/api/trends
```

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: TikTok scanner + yt-dlp downloader"
```

---

### Task 4: Analyzer — GPT-4o Vision разбор видео

**Files:**
- Create: `backend/analyzer/frame_extractor.py`
- Create: `backend/analyzer/video_analyzer.py`
- Create: `backend/analyzer/pattern_detector.py`
- Create: `backend/routes/analyze.py`
- Modify: `backend/app.py`

- [ ] **Step 1: Создать backend/analyzer/frame_extractor.py**

```python
import subprocess
import json
from pathlib import Path
import base64

def extract_frames(video_path: str, num_frames: int = 6) -> list[str]:
    """Extract key frames from video, return list of base64 encoded JPEGs."""
    video_path = Path(video_path)
    if not video_path.exists():
        return []

    # Get duration via ffprobe
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", video_path],
        capture_output=True, text=True,
    )
    duration = float(json.loads(probe.stdout).get("format", {}).get("duration", 10))

    frames = []
    for i in range(num_frames):
        timestamp = (duration / (num_frames + 1)) * (i + 1)
        result = subprocess.run(
            ["ffmpeg", "-ss", str(timestamp), "-i", str(video_path),
             "-vframes", "1", "-f", "image2pipe", "-vcodec", "mjpeg", "-q:v", "5", "-"],
            capture_output=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout:
            b64 = base64.b64encode(result.stdout).decode()
            frames.append(b64)

    return frames
```

- [ ] **Step 2: Создать backend/analyzer/video_analyzer.py**

```python
import json
import yaml
from pathlib import Path
from openai import OpenAI
from backend.analyzer.frame_extractor import extract_frames

def _get_client() -> OpenAI:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return OpenAI(api_key=config["openai_api_key"])

ANALYSIS_PROMPT = """Проанализируй эти кадры из короткого промо-видео для мобильного приложения.

Определи и верни JSON (без markdown):
{
  "hook_type": "question|shock|pattern_interrupt|curiosity|pain_point",
  "hook_text": "текст хука если виден на экране",
  "structure": "описание структуры: что происходит в начале, середине, конце",
  "estimated_cuts": число примерных переходов/катов,
  "cta_type": "download|link_in_bio|swipe_up|none",
  "cta_text": "текст CTA если виден",
  "text_style": "bold_overlay|subtitles|minimal|none",
  "text_placement": "top|center|bottom",
  "has_face": true/false,
  "has_screen_recording": true/false,
  "has_device_frame": true/false,
  "mood": "energetic|calm|dramatic|funny|shocking",
  "virality_factors": ["фактор1", "фактор2"],
  "score": 1-10
}"""

def analyze_video(video_path: str) -> dict | None:
    """Analyze video frames with GPT-4o Vision. Returns analysis dict."""
    frames = extract_frames(video_path, num_frames=6)
    if not frames:
        return None

    client = _get_client()

    messages = [
        {"role": "user", "content": [
            {"type": "text", "text": ANALYSIS_PROMPT},
            *[{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{f}", "detail": "low"}} for f in frames],
        ]}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=800,
        temperature=0.3,
    )

    text = response.choices[0].message.content or ""
    # Strip markdown code blocks if present
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text, "error": "parse_failed"}
```

- [ ] **Step 3: Создать backend/analyzer/pattern_detector.py**

```python
from collections import Counter
import json

def detect_patterns(analyses: list[dict]) -> dict:
    """Aggregate individual video analyses into niche patterns."""
    if not analyses:
        return {"error": "no analyses"}

    valid = [a for a in analyses if "error" not in a]
    if not valid:
        return {"error": "no valid analyses"}

    hook_types = Counter(a.get("hook_type", "unknown") for a in valid)
    cta_types = Counter(a.get("cta_type", "none") for a in valid)
    moods = Counter(a.get("mood", "unknown") for a in valid)
    text_styles = Counter(a.get("text_style", "none") for a in valid)

    all_factors = []
    for a in valid:
        all_factors.extend(a.get("virality_factors", []))
    top_factors = Counter(all_factors).most_common(5)

    avg_cuts = sum(a.get("estimated_cuts", 0) for a in valid) / len(valid)
    avg_score = sum(a.get("score", 0) for a in valid) / len(valid)
    face_pct = sum(1 for a in valid if a.get("has_face")) / len(valid) * 100
    screen_pct = sum(1 for a in valid if a.get("has_screen_recording")) / len(valid) * 100

    return {
        "total_analyzed": len(valid),
        "top_hook_types": hook_types.most_common(3),
        "top_cta_types": cta_types.most_common(3),
        "top_moods": moods.most_common(3),
        "top_text_styles": text_styles.most_common(3),
        "top_virality_factors": top_factors,
        "avg_cuts": round(avg_cuts, 1),
        "avg_score": round(avg_score, 1),
        "face_percentage": round(face_pct),
        "screen_recording_percentage": round(screen_pct),
        "recommendation": {
            "hook": hook_types.most_common(1)[0][0] if hook_types else "curiosity",
            "cta": cta_types.most_common(1)[0][0] if cta_types else "link_in_bio",
            "mood": moods.most_common(1)[0][0] if moods else "energetic",
            "use_face": face_pct > 50,
            "use_screen_recording": screen_pct > 50,
        },
    }
```

- [ ] **Step 4: Создать backend/routes/analyze.py**

```python
from fastapi import APIRouter, BackgroundTasks
from backend.db.database import get_db
from backend.analyzer.video_analyzer import analyze_video
from backend.analyzer.pattern_detector import detect_patterns
import json

router = APIRouter(prefix="/api", tags=["analyze"])

_analyze_status = {"running": False, "progress": 0, "total": 0}

async def _run_analysis(video_ids: list[str] | None):
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
    finally:
        _analyze_status["running"] = False
        await db.close()

@router.post("/analyze")
async def start_analysis(background_tasks: BackgroundTasks, video_ids: list[str] | None = None):
    if _analyze_status["running"]:
        return {"error": "analysis already running"}
    background_tasks.add_task(_run_analysis, video_ids)
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
        except:
            pass
    return detect_patterns(analyses)
```

- [ ] **Step 5: Подключить роут в backend/app.py**

```python
from backend.routes.analyze import router as analyze_router
app.include_router(analyze_router)
```

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: video analyzer — GPT-4o Vision + pattern detection"
```

---

### Task 5: Generator — сценарии, hooks, копирайтинг

**Files:**
- Create: `backend/generator/prompts.py`
- Create: `backend/generator/script_writer.py`
- Create: `backend/generator/hook_writer.py`
- Create: `backend/generator/copy_writer.py`
- Create: `backend/routes/generate.py`
- Modify: `backend/app.py`

- [ ] **Step 1: Создать backend/generator/prompts.py**

```python
SCRIPT_SYSTEM = """Ты — эксперт по созданию вирусных коротких видео для продвижения мобильных приложений.
Формат: VK Клипы / YouTube Shorts / Reels. Аудитория: 14-25 лет, Россия.

Правила:
- Сценарий на русском
- Хук в первые 3 секунды — цепляет внимание
- Длительность: {duration} секунд
- Структура: Hook (0-3 сек) → Проблема (3-8 сек) → Решение через приложение (8-{mid} сек) → CTA ({mid}-{duration} сек)
- Каждая сцена описана: что на экране + текст оверлей + что говорит голос (если есть)
- Формат JSON"""

SCRIPT_USER = """Приложение: {app_name}
Описание: {description}
Ключевые фичи: {features}
Целевая аудитория: {target_audience}

Паттерны из анализа трендов:
- Лучший тип хука: {hook_type}
- Лучший CTA: {cta_type}
- Настроение: {mood}
- Использовать лицо: {use_face}
- Использовать запись экрана: {use_screen}

Сгенерируй {count} разных сценариев. Каждый — JSON объект:
{{
  "title": "краткое название",
  "duration": {duration},
  "scenes": [
    {{
      "time": "0-3",
      "visual": "что на экране",
      "text_overlay": "текст поверх видео",
      "voiceover": "что говорит голос или null"
    }}
  ],
  "hook_text": "текст хука для первого кадра",
  "cta_text": "текст призыва к действию"
}}

Верни массив JSON без markdown."""

HOOKS_USER = """Приложение: {app_name}
Описание: {description}

Сгенерируй {count} разных hook-текстов для первых 3 секунд видео.
Правила:
- На русском
- Максимум 8 слов
- Вызывают любопытство, шок, смех или интригу
- 1-2 эмодзи
- Каждый на новой строке, без нумерации"""

COPY_USER = """Приложение: {app_name}
Описание: {description}
Ключевые фичи: {features}

Сгенерируй контент-пакет. Верни JSON:
{{
  "vk_descriptions": ["5 вариантов описания для VK Клипов, до 300 символов каждое"],
  "youtube_titles": ["5 вариантов заголовков для YouTube Shorts, до 70 символов"],
  "tiktok_descriptions": ["5 вариантов описания для TikTok, до 300 символов"],
  "hashtags": ["15 хэштегов, микс трендовых и нишевых"],
  "bio_text": "текст для профиля/био, 1-2 предложения"
}}

Без markdown, только JSON."""
```

- [ ] **Step 2: Создать backend/generator/script_writer.py**

```python
import json
import yaml
from pathlib import Path
from openai import OpenAI
from backend.generator.prompts import SCRIPT_SYSTEM, SCRIPT_USER

def _get_client() -> OpenAI:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return OpenAI(api_key=config["openai_api_key"])

def generate_scripts(
    app_name: str, description: str, features: str, target_audience: str,
    patterns: dict, count: int = 5, duration: int = 30,
) -> list[dict]:
    client = _get_client()
    rec = patterns.get("recommendation", {})
    mid = duration - 5

    system = SCRIPT_SYSTEM.format(duration=duration, mid=mid)
    user = SCRIPT_USER.format(
        app_name=app_name, description=description, features=features,
        target_audience=target_audience,
        hook_type=rec.get("hook", "curiosity"),
        cta_type=rec.get("cta", "link_in_bio"),
        mood=rec.get("mood", "energetic"),
        use_face=rec.get("use_face", False),
        use_screen=rec.get("use_screen_recording", True),
        count=count, duration=duration,
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        max_tokens=3000,
        temperature=0.9,
    )

    text = response.choices[0].message.content or "[]"
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return [{"error": "parse_failed", "raw": text}]
```

- [ ] **Step 3: Создать backend/generator/hook_writer.py**

```python
from openai import OpenAI
from pathlib import Path
import yaml
from backend.generator.prompts import HOOKS_USER

def _get_client() -> OpenAI:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return OpenAI(api_key=config["openai_api_key"])

def generate_hooks(app_name: str, description: str, count: int = 20) -> list[str]:
    client = _get_client()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": HOOKS_USER.format(
            app_name=app_name, description=description, count=count,
        )}],
        max_tokens=1000,
        temperature=1.0,
    )

    text = response.choices[0].message.content or ""
    return [line.strip() for line in text.split("\n") if line.strip() and len(line.strip()) < 60]
```

- [ ] **Step 4: Создать backend/generator/copy_writer.py**

```python
import json
from openai import OpenAI
from pathlib import Path
import yaml
from backend.generator.prompts import COPY_USER

def _get_client() -> OpenAI:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return OpenAI(api_key=config["openai_api_key"])

def generate_copy(app_name: str, description: str, features: str) -> dict:
    client = _get_client()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": COPY_USER.format(
            app_name=app_name, description=description, features=features,
        )}],
        max_tokens=1500,
        temperature=0.8,
    )

    text = response.choices[0].message.content or "{}"
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"error": "parse_failed", "raw": text}
```

- [ ] **Step 5: Создать backend/routes/generate.py**

```python
from fastapi import APIRouter
from backend.generator.script_writer import generate_scripts
from backend.generator.hook_writer import generate_hooks
from backend.generator.copy_writer import generate_copy
from backend.db.database import get_db
import json

router = APIRouter(prefix="/api/generate", tags=["generate"])

@router.post("/scripts")
async def gen_scripts(project_id: str, count: int = 5, duration: int = 30):
    db = await get_db()
    project = await db.execute_fetchone("SELECT * FROM projects WHERE id = ?", (project_id,))
    await db.close()
    if not project:
        return {"error": "project not found"}
    p = dict(project)

    # Get patterns
    db2 = await get_db()
    rows = await db2.execute_fetchall("SELECT analysis FROM trends WHERE analyzed = 1 AND analysis IS NOT NULL")
    await db2.close()
    analyses = []
    for r in rows:
        try:
            analyses.append(json.loads(dict(r)["analysis"]))
        except:
            pass

    from backend.analyzer.pattern_detector import detect_patterns
    patterns = detect_patterns(analyses) if analyses else {}

    scripts = generate_scripts(
        p["name"], p["description"], p.get("features", "[]"),
        p.get("target_audience", ""), patterns, count, duration,
    )
    return {"scripts": scripts}

@router.post("/hooks")
async def gen_hooks(project_id: str, count: int = 20):
    db = await get_db()
    project = await db.execute_fetchone("SELECT * FROM projects WHERE id = ?", (project_id,))
    await db.close()
    if not project:
        return {"error": "project not found"}
    p = dict(project)
    hooks = generate_hooks(p["name"], p["description"], count)
    return {"hooks": hooks}

@router.post("/copy")
async def gen_copy(project_id: str):
    db = await get_db()
    project = await db.execute_fetchone("SELECT * FROM projects WHERE id = ?", (project_id,))
    await db.close()
    if not project:
        return {"error": "project not found"}
    p = dict(project)
    copy = generate_copy(p["name"], p["description"], p.get("features", "[]"))
    return copy
```

- [ ] **Step 6: Подключить роут в backend/app.py**

```python
from backend.routes.generate import router as generate_router
app.include_router(generate_router)
```

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "feat: content generator — scripts, hooks, copy via GPT"
```

---

### Task 6: Audio — TTS + микширование

**Files:**
- Create: `backend/audio/tts.py`
- Create: `backend/audio/trending.py`
- Create: `backend/audio/mixer.py`
- Create: `backend/routes/audio.py`
- Modify: `backend/app.py`

- [ ] **Step 1: Создать backend/audio/tts.py**

```python
import edge_tts
import asyncio
from pathlib import Path
import uuid

async def generate_tts(text: str, voice: str = "ru-RU-DmitryNeural", output_dir: str = "data/projects") -> str:
    """Generate TTS audio file. Returns path to MP3."""
    output_path = Path(output_dir) / f"tts_{uuid.uuid4().hex[:8]}.mp3"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))
    return str(output_path)

# Available Russian voices
RUSSIAN_VOICES = [
    {"id": "ru-RU-DmitryNeural", "name": "Дмитрий", "gender": "male"},
    {"id": "ru-RU-SvetlanaNeural", "name": "Светлана", "gender": "female"},
]
```

- [ ] **Step 2: Создать backend/audio/trending.py**

```python
from backend.db.database import get_db
from collections import Counter
import json

async def get_trending_audio(limit: int = 10) -> list[dict]:
    """Get most used audio from scanned trends."""
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT audio_id, audio_name FROM trends WHERE audio_id IS NOT NULL"
    )
    await db.close()

    audio_counts = Counter()
    audio_names = {}
    for r in rows:
        d = dict(r)
        aid = d["audio_id"]
        if aid:
            audio_counts[aid] += 1
            audio_names[aid] = d.get("audio_name", "Unknown")

    return [
        {"audio_id": aid, "name": audio_names.get(aid, "Unknown"), "count": count}
        for aid, count in audio_counts.most_common(limit)
    ]
```

- [ ] **Step 3: Создать backend/audio/mixer.py**

```python
from pydub import AudioSegment
from pathlib import Path
import uuid

def mix_audio(
    voice_path: str | None = None,
    music_path: str | None = None,
    output_dir: str = "data/projects",
    voice_db: float = -6,
    music_db: float = -18,
    duration_ms: int | None = None,
) -> str:
    """Mix voice + music tracks. Returns path to output file."""
    output_path = Path(output_dir) / f"mixed_{uuid.uuid4().hex[:8]}.mp3"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if voice_path and music_path:
        voice = AudioSegment.from_file(voice_path) + voice_db
        music = AudioSegment.from_file(music_path) + music_db

        # Loop music to match voice length
        target_len = len(voice) if not duration_ms else duration_ms
        if len(music) < target_len:
            loops = (target_len // len(music)) + 1
            music = music * loops
        music = music[:target_len]

        # Pad voice if shorter
        if len(voice) < len(music):
            silence = AudioSegment.silent(duration=len(music) - len(voice))
            voice = voice + silence

        mixed = voice.overlay(music)
    elif voice_path:
        mixed = AudioSegment.from_file(voice_path) + voice_db
    elif music_path:
        mixed = AudioSegment.from_file(music_path) + music_db
        if duration_ms:
            mixed = mixed[:duration_ms]
    else:
        return ""

    mixed.export(str(output_path), format="mp3")
    return str(output_path)
```

- [ ] **Step 4: Создать backend/routes/audio.py**

```python
from fastapi import APIRouter
from backend.audio.tts import generate_tts, RUSSIAN_VOICES
from backend.audio.trending import get_trending_audio
from backend.audio.mixer import mix_audio
from pathlib import Path
import os

router = APIRouter(prefix="/api/audio", tags=["audio"])

@router.get("/voices")
async def list_voices():
    return RUSSIAN_VOICES

@router.post("/tts")
async def create_tts(text: str, voice: str = "ru-RU-DmitryNeural", project_id: str = ""):
    output_dir = f"data/projects/{project_id}" if project_id else "data/projects"
    path = await generate_tts(text, voice, output_dir)
    return {"path": path}

@router.get("/trending")
async def trending_audio():
    return await get_trending_audio()

@router.get("/library")
async def audio_library():
    library = []
    for mood in ["energetic", "chill", "dramatic"]:
        mood_dir = Path(f"assets/sounds/{mood}")
        if mood_dir.exists():
            for f in mood_dir.glob("*.mp3"):
                library.append({"name": f.stem, "mood": mood, "path": str(f)})
    return library

@router.post("/mix")
async def mix(voice_path: str = "", music_path: str = "", project_id: str = "", duration_ms: int = 30000):
    output_dir = f"data/projects/{project_id}" if project_id else "data/projects"
    path = mix_audio(
        voice_path=voice_path or None,
        music_path=music_path or None,
        output_dir=output_dir,
        duration_ms=duration_ms,
    )
    return {"path": path}
```

- [ ] **Step 5: Подключить роут в backend/app.py**

```python
from backend.routes.audio import router as audio_router
app.include_router(audio_router)
```

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: audio engine — edge-tts + pydub mixer + trending audio"
```

---

### Task 7: Renderer — сборка видео (moviepy)

**Files:**
- Create: `backend/renderer/effects.py`
- Create: `backend/renderer/text_overlay.py`
- Create: `backend/renderer/device_frame.py`
- Create: `backend/renderer/composer.py`
- Create: `backend/renderer/templates/app_reveal.py`
- Create: `backend/renderer/batch.py`
- Create: `backend/routes/render.py`
- Modify: `backend/app.py`

- [ ] **Step 1: Создать backend/renderer/effects.py**

```python
from moviepy import *
import numpy as np

def zoom_in(clip, start_scale=1.0, end_scale=1.15):
    """Ken Burns zoom-in effect."""
    def resize_func(t):
        progress = t / clip.duration
        scale = start_scale + (end_scale - start_scale) * progress
        return scale
    return clip.resized(resize_func)

def fade_in(clip, duration=0.5):
    return clip.with_effects([vfx.CrossFadeIn(duration)])

def fade_out(clip, duration=0.5):
    return clip.with_effects([vfx.CrossFadeOut(duration)])
```

- [ ] **Step 2: Создать backend/renderer/text_overlay.py**

```python
from moviepy import *
from pathlib import Path

FONT_PATH = str(Path(__file__).parent.parent.parent / "assets" / "fonts" / "Montserrat-Bold.ttf")
FALLBACK_FONT = "Arial-Bold"

def create_text_clip(
    text: str, duration: float, fontsize: int = 60, color: str = "white",
    stroke_color: str = "black", stroke_width: int = 3,
    position: str = "center", size: tuple = (1080, 1920),
) -> TextClip:
    """Create text overlay with stroke for readability."""
    font = FONT_PATH if Path(FONT_PATH).exists() else FALLBACK_FONT

    # Safe zone: not below 80% height, not beyond 90% width
    max_width = int(size[0] * 0.85)

    txt = TextClip(
        text=text,
        font=font,
        font_size=fontsize,
        color=color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
        size=(max_width, None),
        method="caption",
        text_align="center",
    ).with_duration(duration)

    if position == "top":
        txt = txt.with_position(("center", int(size[1] * 0.12)))
    elif position == "bottom":
        txt = txt.with_position(("center", int(size[1] * 0.72)))
    else:
        txt = txt.with_position("center")

    return txt

def create_cta_clip(text: str, duration: float, size: tuple = (1080, 1920)) -> TextClip:
    """CTA text at bottom-center."""
    return create_text_clip(text, duration, fontsize=40, position="bottom", size=size)
```

- [ ] **Step 3: Создать backend/renderer/device_frame.py**

```python
from moviepy import *
from PIL import Image
from pathlib import Path
import numpy as np

def wrap_in_device_frame(
    screenshot_path: str, duration: float, size: tuple = (1080, 1920),
    frame_type: str = "iphone",
) -> ImageClip:
    """Place screenshot inside a phone frame mockup."""
    # Load screenshot and resize to phone screen area
    screenshot = Image.open(screenshot_path).convert("RGBA")

    # Phone dimensions on 1080x1920 canvas
    phone_w, phone_h = 380, 780
    screen_x, screen_y = (size[0] - phone_w) // 2, (size[1] - phone_h) // 2

    # Resize screenshot to fit phone screen (with padding for rounded corners)
    inner_w, inner_h = phone_w - 20, phone_h - 20
    screenshot = screenshot.resize((inner_w, inner_h), Image.LANCZOS)

    # Create canvas
    canvas = Image.new("RGBA", size, (10, 10, 15, 255))

    # Draw phone frame (rounded rectangle)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(canvas)
    frame_rect = [screen_x, screen_y, screen_x + phone_w, screen_y + phone_h]
    draw.rounded_rectangle(frame_rect, radius=35, fill=(30, 30, 40), outline=(139, 92, 246, 100), width=3)

    # Paste screenshot inside frame
    canvas.paste(screenshot, (screen_x + 10, screen_y + 10), screenshot)

    arr = np.array(canvas.convert("RGB"))
    return ImageClip(arr).with_duration(duration)
```

- [ ] **Step 4: Создать backend/renderer/composer.py**

```python
from moviepy import *
from pathlib import Path
from backend.renderer.effects import zoom_in, fade_in, fade_out
from backend.renderer.text_overlay import create_text_clip, create_cta_clip
from backend.renderer.device_frame import wrap_in_device_frame
import numpy as np

SIZE = (1080, 1920)
FPS = 30
BG_COLOR = (10, 10, 15)

def black_bg(duration: float) -> ColorClip:
    return ColorClip(SIZE, color=BG_COLOR).with_duration(duration)

def compose_app_reveal(
    screenshots: list[str], hook_text: str, cta_text: str,
    audio_path: str | None = None, duration: float = 30,
) -> str:
    """AppReveal template: black → hook → screenshots in phone → CTA."""
    clips = []

    # Phase 1: Hook text on black (3 sec)
    hook_bg = black_bg(3)
    hook_txt = create_text_clip(hook_text, 3, fontsize=72, position="center")
    hook_phase = CompositeVideoClip([hook_bg, hook_txt])
    clips.append(hook_phase)

    # Phase 2: Screenshots in device frames
    if screenshots:
        screen_duration = (duration - 6) / len(screenshots)
        for ss in screenshots:
            frame_clip = wrap_in_device_frame(ss, screen_duration)
            frame_clip = zoom_in(frame_clip)
            frame_clip = fade_in(frame_clip, 0.3)
            clips.append(frame_clip)

    # Phase 3: CTA (3 sec)
    cta_bg = black_bg(3)
    cta_txt = create_cta_clip(cta_text, 3)
    cta_phase = CompositeVideoClip([cta_bg, cta_txt])
    clips.append(cta_phase)

    # Concatenate
    final = concatenate_videoclips(clips, method="compose")

    # Add audio
    if audio_path and Path(audio_path).exists():
        audio = AudioFileClip(audio_path)
        if audio.duration < final.duration:
            audio = audio.loop(duration=final.duration)
        else:
            audio = audio.subclipped(0, final.duration)
        final = final.with_audio(audio)

    return final

def render_video(
    template: str, screenshots: list[str], hook_text: str, cta_text: str,
    audio_path: str | None, output_path: str, duration: float = 30,
):
    """Render video to MP4 file."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if template == "AppReveal":
        video = compose_app_reveal(screenshots, hook_text, cta_text, audio_path, duration)
    else:
        # Default to AppReveal for now
        video = compose_app_reveal(screenshots, hook_text, cta_text, audio_path, duration)

    video.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="fast",
        logger=None,
    )

    # Cleanup
    video.close()
    return output_path
```

- [ ] **Step 5: Создать backend/renderer/batch.py**

```python
from concurrent.futures import ProcessPoolExecutor
from backend.renderer.composer import render_video
from pathlib import Path
import uuid

def render_single(args: dict) -> dict:
    """Render a single video (runs in subprocess)."""
    try:
        output = render_video(
            template=args["template"],
            screenshots=args["screenshots"],
            hook_text=args["hook_text"],
            cta_text=args["cta_text"],
            audio_path=args.get("audio_path"),
            output_path=args["output_path"],
            duration=args.get("duration", 30),
        )
        return {"status": "done", "output": output, "id": args["id"]}
    except Exception as e:
        return {"status": "error", "error": str(e), "id": args["id"]}

def batch_render(jobs: list[dict], max_workers: int = 2) -> list[dict]:
    """Render multiple videos in parallel."""
    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(render_single, job) for job in jobs]
        for f in futures:
            results.append(f.result())
    return results
```

- [ ] **Step 6: Создать backend/routes/render.py**

```python
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse
from backend.renderer.composer import render_video
from backend.db.database import get_db
from pathlib import Path
import uuid
import json

router = APIRouter(prefix="/api/render", tags=["render"])

_render_jobs: dict[str, dict] = {}

async def _run_render(job_id: str, project_id: str, template: str, hook_text: str, cta_text: str, audio_path: str | None, duration: float):
    _render_jobs[job_id] = {"status": "rendering", "progress": 0}

    db = await get_db()
    project = await db.execute_fetchone("SELECT screenshots_dir FROM projects WHERE id = ?", (project_id,))
    await db.close()
    if not project:
        _render_jobs[job_id] = {"status": "error", "error": "project not found"}
        return

    ss_dir = Path(dict(project)["screenshots_dir"])
    screenshots = sorted([str(f) for f in ss_dir.glob("*.*") if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")])

    output_path = f"data/projects/{project_id}/output/{job_id}.mp4"

    try:
        render_video(template, screenshots, hook_text, cta_text, audio_path, output_path, duration)

        db2 = await get_db()
        await db2.execute(
            "INSERT INTO renders (id, project_id, template, hook_text, audio_path, output_path, duration, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (job_id, project_id, template, hook_text, audio_path, output_path, duration, "done"),
        )
        await db2.commit()
        await db2.close()

        _render_jobs[job_id] = {"status": "done", "output_path": output_path}
    except Exception as e:
        _render_jobs[job_id] = {"status": "error", "error": str(e)}

@router.post("")
async def start_render(
    background_tasks: BackgroundTasks,
    project_id: str, template: str = "AppReveal",
    hook_text: str = "Это приложение взорвёт 🔥",
    cta_text: str = "Ссылка в био 👇",
    audio_path: str = "",
    duration: float = 30,
):
    job_id = uuid.uuid4().hex[:8]
    background_tasks.add_task(_run_render, job_id, project_id, template, hook_text, cta_text, audio_path or None, duration)
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
    rows = await db.execute_fetchall("SELECT * FROM renders WHERE project_id = ? ORDER BY created_at DESC", (project_id,))
    await db.close()
    return [dict(r) for r in rows]
```

- [ ] **Step 7: Подключить роут в backend/app.py**

```python
from backend.routes.render import router as render_router
app.include_router(render_router)
```

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "feat: video renderer — moviepy composer + batch render + effects"
```

---

### Task 8: React фронтенд

**Files:**
- Create: `frontend/` (полный React + Vite проект)

- [ ] **Step 1: Инициализировать React проект**

```bash
cd promo-machine
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install lucide-react
```

- [ ] **Step 2: Настроить Vite proxy на FastAPI**

В `frontend/vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
```

- [ ] **Step 3: Создать frontend/src/api.ts**

```typescript
const BASE = '/api';

export async function fetchAPI(path: string, options?: RequestInit) {
  const res = await fetch(`${BASE}${path}`, options);
  return res.json();
}

export const api = {
  // Projects
  getProjects: () => fetchAPI('/projects'),
  createProject: (form: FormData) => fetchAPI('/projects', { method: 'POST', body: form }),
  getProject: (id: string) => fetchAPI(`/projects/${id}`),
  deleteProject: (id: string) => fetchAPI(`/projects/${id}`, { method: 'DELETE' }),
  uploadScreenshots: (id: string, form: FormData) => fetchAPI(`/projects/${id}/screenshots`, { method: 'POST', body: form }),

  // Scan
  startScan: (keywords: string, count: number) => fetchAPI(`/scan?keywords=${encodeURIComponent(keywords)}&count=${count}`, { method: 'POST' }),
  scanStatus: () => fetchAPI('/scan/status'),
  getTrends: () => fetchAPI('/trends'),

  // Analyze
  startAnalysis: () => fetchAPI('/analyze', { method: 'POST' }),
  analysisStatus: () => fetchAPI('/analyze/status'),
  getPatterns: () => fetchAPI('/patterns'),

  // Generate
  generateScripts: (projectId: string, count: number, duration: number) =>
    fetchAPI(`/generate/scripts?project_id=${projectId}&count=${count}&duration=${duration}`, { method: 'POST' }),
  generateHooks: (projectId: string) =>
    fetchAPI(`/generate/hooks?project_id=${projectId}`, { method: 'POST' }),
  generateCopy: (projectId: string) =>
    fetchAPI(`/generate/copy?project_id=${projectId}`, { method: 'POST' }),

  // Audio
  getVoices: () => fetchAPI('/audio/voices'),
  createTTS: (text: string, voice: string, projectId: string) =>
    fetchAPI(`/audio/tts?text=${encodeURIComponent(text)}&voice=${voice}&project_id=${projectId}`, { method: 'POST' }),
  getTrendingAudio: () => fetchAPI('/audio/trending'),

  // Render
  startRender: (projectId: string, template: string, hookText: string, ctaText: string, duration: number) =>
    fetchAPI(`/render?project_id=${projectId}&template=${template}&hook_text=${encodeURIComponent(hookText)}&cta_text=${encodeURIComponent(ctaText)}&duration=${duration}`, { method: 'POST' }),
  renderStatus: (jobId: string) => fetchAPI(`/render/status/${jobId}`),
  listRenders: (projectId: string) => fetchAPI(`/render/list/${projectId}`),
};
```

- [ ] **Step 4: Создать frontend/src/App.tsx** — основной layout с табами

```typescript
import { useState } from 'react';
import { Scan, BarChart3, FolderOpen, Sparkles, Download } from 'lucide-react';

const TABS = [
  { id: 'trends', label: 'Тренды', icon: Scan },
  { id: 'analysis', label: 'Анализ', icon: BarChart3 },
  { id: 'projects', label: 'Проекты', icon: FolderOpen },
  { id: 'generate', label: 'Генерация', icon: Sparkles },
  { id: 'export', label: 'Экспорт', icon: Download },
] as const;

export default function App() {
  const [activeTab, setActiveTab] = useState('projects');

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white flex">
      {/* Sidebar */}
      <nav className="w-56 border-r border-white/10 p-4 flex flex-col gap-1">
        <h1 className="text-lg font-bold mb-6 px-3" style={{ textShadow: '0 0 20px rgba(139,92,246,0.5)' }}>
          🎬 Promo Machine
        </h1>
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
              activeTab === id
                ? 'bg-purple-600/20 text-purple-300 border border-purple-500/30'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/5'
            }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </nav>

      {/* Content */}
      <main className="flex-1 p-6 overflow-y-auto">
        <div className="max-w-5xl">
          {activeTab === 'trends' && <div>Тренды — TODO</div>}
          {activeTab === 'analysis' && <div>Анализ — TODO</div>}
          {activeTab === 'projects' && <div>Проекты — TODO</div>}
          {activeTab === 'generate' && <div>Генерация — TODO</div>}
          {activeTab === 'export' && <div>Экспорт — TODO</div>}
        </div>
      </main>
    </div>
  );
}
```

Каждый таб будет отдельным компонентом — реализуется в последующих коммитах по мере готовности бэкенда.

- [ ] **Step 5: Проверить запуск**

```bash
cd frontend && npm run dev
# Открыть http://localhost:5173
```

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: React frontend skeleton — tabs, api client, Vite proxy"
```

---

### Контрольная точка

После Task 8 у тебя:
- ✅ FastAPI бэкенд со всеми модулями
- ✅ SQLite база данных
- ✅ TikTok сканер + yt-dlp загрузка
- ✅ GPT-4o Vision анализ видео
- ✅ AI генерация сценариев, хуков, копирайтинга
- ✅ TTS озвучка + микширование
- ✅ Рендер видео через moviepy
- ✅ React фронт со скелетом табов

**Дальше:** наполнение React компонентов (каждая вкладка), дополнительные шаблоны видео (SplitScreen, POVReaction, HookAndShow, Testimonial), VK Clips сканер. Это Task 9-14 — реализуются итеративно.
