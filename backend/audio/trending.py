from typing import List, Dict
from backend.db.database import get_db
from collections import Counter

async def get_trending_audio(limit: int = 10) -> List[Dict]:
    db = await get_db()
    rows = await db.execute_fetchall("SELECT audio_id, audio_name FROM trends WHERE audio_id IS NOT NULL")
    await db.close()
    audio_counts = Counter()
    audio_names = {}
    for r in rows:
        d = dict(r)
        aid = d["audio_id"]
        if aid:
            audio_counts[aid] += 1
            audio_names[aid] = d.get("audio_name", "Unknown")
    return [{"audio_id": aid, "name": audio_names.get(aid, "Unknown"), "count": count} for aid, count in audio_counts.most_common(limit)]
