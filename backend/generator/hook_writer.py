import yaml
from typing import List
from pathlib import Path
from openai import OpenAI
from backend.generator.prompts import HOOKS_USER


def _get_client() -> OpenAI:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return OpenAI(api_key=config["openai_api_key"])


def generate_hooks(app_name: str, description: str, count: int = 20) -> List[str]:
    client = _get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": HOOKS_USER.format(
                    app_name=app_name, description=description, count=count
                ),
            }
        ],
        max_tokens=1000,
        temperature=1.0,
    )
    text = response.choices[0].message.content or ""
    return [
        line.strip()
        for line in text.split("\n")
        if line.strip() and len(line.strip()) < 60
    ]
