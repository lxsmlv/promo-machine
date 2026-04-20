from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from contextlib import asynccontextmanager
from backend.db.database import get_db
from backend.db.models import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    Path("data/downloads/tiktok").mkdir(parents=True, exist_ok=True)
    Path("data/downloads/vk").mkdir(parents=True, exist_ok=True)
    Path("data/projects").mkdir(parents=True, exist_ok=True)
    db = await get_db()
    await init_db(db)
    await db.close()
    yield

app = FastAPI(title="Promo Machine", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    return {"status": "ok"}
