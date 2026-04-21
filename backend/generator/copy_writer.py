import json
import yaml
from typing import Dict
from pathlib import Path
from openai import OpenAI
from backend.generator.prompts import COPY_USER


def _get_client() -> OpenAI:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return OpenAI(api_key=config["openai_api_key"])


def generate_copy(app_name: str, description: str, features: str) -> Dict:
    client = _get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": COPY_USER.format(
                    app_name=app_name, description=description, features=features
                ),
            }
        ],
        max_tokens=1500,
        temperature=0.8,
    )
    text = response.choices[0].message.content or "{}"
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"error": "parse_failed", "raw": text}
