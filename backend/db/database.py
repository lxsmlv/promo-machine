import aiosqlite
import yaml
from pathlib import Path
from typing import Optional

_db_path: Optional[str] = None

def get_db_path() -> str:
    global _db_path
    if _db_path is None:
        config_path = Path(__file__).parent.parent.parent / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        _db_path = config.get("db_path", "./data/promo.db")
    return _db_path

async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(get_db_path())
    db.row_factory = aiosqlite.Row
    return db
