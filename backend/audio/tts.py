import edge_tts
import asyncio
from typing import List, Dict
from pathlib import Path
import uuid

RUSSIAN_VOICES = [
    {"id": "ru-RU-DmitryNeural", "name": "Дмитрий", "gender": "male"},
    {"id": "ru-RU-SvetlanaNeural", "name": "Светлана", "gender": "female"},
]

async def generate_tts(text: str, voice: str = "ru-RU-DmitryNeural", output_dir: str = "data/projects") -> str:
    output_path = Path(output_dir) / f"tts_{uuid.uuid4().hex[:8]}.mp3"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))
    return str(output_path)
