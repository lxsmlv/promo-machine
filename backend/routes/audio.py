from typing import List
from fastapi import APIRouter
from backend.audio.tts import generate_tts, RUSSIAN_VOICES
from backend.audio.trending import get_trending_audio
from backend.audio.mixer import mix_audio
from pathlib import Path

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
    path = mix_audio(voice_path=voice_path or None, music_path=music_path or None, output_dir=output_dir, duration_ms=duration_ms)
    return {"path": path}
