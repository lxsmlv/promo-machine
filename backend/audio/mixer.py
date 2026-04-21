from typing import Optional
from pydub import AudioSegment
from pathlib import Path
import uuid

def mix_audio(voice_path: Optional[str] = None, music_path: Optional[str] = None, output_dir: str = "data/projects", voice_db: float = -6, music_db: float = -18, duration_ms: Optional[int] = None) -> str:
    output_path = Path(output_dir) / f"mixed_{uuid.uuid4().hex[:8]}.mp3"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if voice_path and music_path:
        voice = AudioSegment.from_file(voice_path) + voice_db
        music = AudioSegment.from_file(music_path) + music_db
        target_len = len(voice) if not duration_ms else duration_ms
        if len(music) < target_len:
            music = music * ((target_len // len(music)) + 1)
        music = music[:target_len]
        if len(voice) < len(music):
            voice = voice + AudioSegment.silent(duration=len(music) - len(voice))
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
