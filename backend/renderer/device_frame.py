from typing import Tuple
from moviepy import ImageClip
from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path

def create_device_frame_clip(
    screenshot_path: str,
    duration: float,
    size: Tuple[int, int] = (1080, 1920),
) -> ImageClip:
    """Place screenshot inside a phone-like frame on dark background."""
    screenshot = Image.open(screenshot_path).convert("RGBA")

    phone_w, phone_h = 380, 780
    screen_x = (size[0] - phone_w) // 2
    screen_y = (size[1] - phone_h) // 2
    inner_w, inner_h = phone_w - 20, phone_h - 20

    screenshot = screenshot.resize((inner_w, inner_h), Image.LANCZOS)

    canvas = Image.new("RGBA", size, (10, 10, 15, 255))
    draw = ImageDraw.Draw(canvas)

    # Phone frame
    draw.rounded_rectangle(
        [screen_x, screen_y, screen_x + phone_w, screen_y + phone_h],
        radius=35,
        fill=(30, 30, 40),
        outline=(139, 92, 246, 100),
        width=3,
    )

    canvas.paste(screenshot, (screen_x + 10, screen_y + 10), screenshot)
    arr = np.array(canvas.convert("RGB"))
    return ImageClip(arr).with_duration(duration)
