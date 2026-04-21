from typing import Callable
from moviepy import VideoClip, ImageClip
import numpy as np

def zoom_in_effect(clip: VideoClip, start_scale: float = 1.0, end_scale: float = 1.15) -> VideoClip:
    """Ken Burns zoom-in effect on a clip."""
    w, h = clip.size
    def make_frame(t):
        progress = t / max(clip.duration, 0.01)
        scale = start_scale + (end_scale - start_scale) * progress
        frame = clip.get_frame(t)
        # Resize
        new_w, new_h = int(w * scale), int(h * scale)
        from PIL import Image
        img = Image.fromarray(frame)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        arr = np.array(img)
        # Crop center
        x_off = (new_w - w) // 2
        y_off = (new_h - h) // 2
        return arr[y_off:y_off+h, x_off:x_off+w]
    return VideoClip(make_frame, duration=clip.duration).with_fps(clip.fps or 30)
