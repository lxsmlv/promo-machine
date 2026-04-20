import json
import yaml
from typing import Optional, Dict
from pathlib import Path
from openai import OpenAI
from backend.analyzer.frame_extractor import extract_frames


def _get_client() -> OpenAI:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return OpenAI(api_key=config["openai_api_key"])


ANALYSIS_PROMPT = """Проанализируй эти кадры из короткого промо-видео для мобильного приложения.

Определи и верни ТОЛЬКО валидный JSON (без markdown, без ```):
{
  "hook_type": "question|shock|pattern_interrupt|curiosity|pain_point",
  "hook_text": "текст хука если виден на экране или пустая строка",
  "structure": "краткое описание структуры видео",
  "estimated_cuts": 5,
  "cta_type": "download|link_in_bio|swipe_up|none",
  "cta_text": "текст CTA или пустая строка",
  "text_style": "bold_overlay|subtitles|minimal|none",
  "text_placement": "top|center|bottom",
  "has_face": false,
  "has_screen_recording": false,
  "has_device_frame": false,
  "mood": "energetic|calm|dramatic|funny|shocking",
  "virality_factors": ["фактор1", "фактор2"],
  "score": 7
}"""


def analyze_video(video_path: str) -> Optional[Dict]:
    frames = extract_frames(video_path, num_frames=6)
    if not frames:
        return None

    client = _get_client()

    content = [{"type": "text", "text": ANALYSIS_PROMPT}]
    for f in frames:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{f}", "detail": "low"}})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content}],
        max_tokens=800,
        temperature=0.3,
    )

    text = response.choices[0].message.content or ""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text, "error": "parse_failed"}
