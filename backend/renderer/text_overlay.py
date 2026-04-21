from typing import Tuple, Optional
from moviepy import TextClip
from pathlib import Path

FONT_PATH = str(Path(__file__).parent.parent.parent / "assets" / "fonts" / "Montserrat-Bold.ttf")

def _get_font() -> str:
    if Path(FONT_PATH).exists():
        return FONT_PATH
    return "Arial-Bold"

def create_text_clip(
    text: str,
    duration: float,
    fontsize: int = 60,
    color: str = "white",
    stroke_color: str = "black",
    stroke_width: int = 3,
    position: str = "center",
    size: Tuple[int, int] = (1080, 1920),
) -> TextClip:
    max_width = int(size[0] * 0.85)
    font = _get_font()

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
