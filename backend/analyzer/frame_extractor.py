import subprocess
import json
import base64
from typing import List
from pathlib import Path


def extract_frames(video_path: str, num_frames: int = 6) -> List[str]:
    """Extract key frames from video, return list of base64 JPEGs."""
    video_path = Path(video_path)
    if not video_path.exists():
        return []

    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(video_path)],
            capture_output=True, text=True, timeout=10,
        )
        duration = float(json.loads(probe.stdout).get("format", {}).get("duration", 10))
    except Exception:
        duration = 10.0

    frames = []
    for i in range(num_frames):
        timestamp = (duration / (num_frames + 1)) * (i + 1)
        try:
            result = subprocess.run(
                ["ffmpeg", "-ss", str(timestamp), "-i", str(video_path),
                 "-vframes", "1", "-f", "image2pipe", "-vcodec", "mjpeg", "-q:v", "5", "-"],
                capture_output=True, timeout=10,
            )
            if result.returncode == 0 and result.stdout:
                b64 = base64.b64encode(result.stdout).decode()
                frames.append(b64)
        except Exception:
            continue

    return frames
