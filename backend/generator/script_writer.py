import json
import yaml
from typing import List, Dict
from pathlib import Path
from openai import OpenAI
from backend.generator.prompts import SCRIPT_SYSTEM, SCRIPT_USER


def _get_client() -> OpenAI:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return OpenAI(api_key=config["openai_api_key"])


def generate_scripts(
    app_name: str,
    description: str,
    features: str,
    target_audience: str,
    patterns: Dict,
    count: int = 5,
    duration: int = 30,
) -> List[Dict]:
    client = _get_client()
    rec = patterns.get("recommendation", {})
    end_sec = duration - 5

    system = SCRIPT_SYSTEM.format(end_sec=end_sec)
    user = SCRIPT_USER.format(
        app_name=app_name,
        description=description,
        features=features,
        target_audience=target_audience,
        hook_type=rec.get("hook", "curiosity"),
        cta_type=rec.get("cta", "link_in_bio"),
        mood=rec.get("mood", "energetic"),
        use_face=rec.get("use_face", False),
        use_screen=rec.get("use_screen_recording", True),
        count=count,
        duration=duration,
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=3000,
        temperature=0.9,
    )

    text = response.choices[0].message.content or "[]"
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return [{"error": "parse_failed", "raw": text}]
