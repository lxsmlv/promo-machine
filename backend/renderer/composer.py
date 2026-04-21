import shutil
from typing import Optional, List, Tuple
from pathlib import Path
from moviepy import (
    VideoClip, ImageClip, ColorClip, TextClip,
    CompositeVideoClip, AudioFileClip, concatenate_videoclips
)
from backend.renderer.text_overlay import create_text_clip
from backend.renderer.device_frame import create_device_frame_clip
import numpy as np

SIZE = (1080, 1920)
FPS = 30
BG_COLOR = (10, 10, 15)

def _check_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None

def black_bg(duration: float) -> ColorClip:
    return ColorClip(SIZE, color=BG_COLOR).with_duration(duration)

def compose_app_reveal(
    screenshots: List[str],
    hook_text: str,
    cta_text: str,
    audio_path: Optional[str] = None,
    duration: float = 30,
) -> VideoClip:
    clips = []

    # Phase 1: Hook (3 sec)
    hook_bg = black_bg(3)
    hook_txt = create_text_clip(hook_text, 3, fontsize=72, position="center")
    clips.append(CompositeVideoClip([hook_bg, hook_txt]))

    # Phase 2: Screenshots
    if screenshots:
        screen_dur = max((duration - 6) / len(screenshots), 1)
        for ss in screenshots:
            try:
                frame_clip = create_device_frame_clip(ss, screen_dur)
                clips.append(frame_clip)
            except Exception as e:
                print(f"Error with screenshot {ss}: {e}")

    # Phase 3: CTA (3 sec)
    cta_bg = black_bg(3)
    cta_txt = create_text_clip(cta_text, 3, fontsize=48, position="center")
    clips.append(CompositeVideoClip([cta_bg, cta_txt]))

    final = concatenate_videoclips(clips, method="compose")

    if audio_path and Path(audio_path).exists():
        try:
            audio = AudioFileClip(audio_path)
            if audio.duration < final.duration:
                audio = audio.loop(duration=final.duration)
            else:
                audio = audio.subclipped(0, final.duration)
            final = final.with_audio(audio)
        except Exception as e:
            print(f"Audio error: {e}")

    return final

def render_video(
    template: str,
    screenshots: List[str],
    hook_text: str,
    cta_text: str,
    audio_path: Optional[str],
    output_path: str,
    duration: float = 30,
) -> str:
    if not _check_ffmpeg():
        raise RuntimeError("FFmpeg not installed. Run: brew install ffmpeg")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

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
    video.close()
    return output_path
