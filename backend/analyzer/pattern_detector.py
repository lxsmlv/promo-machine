from typing import List, Dict
from collections import Counter


def detect_patterns(analyses: List[Dict]) -> Dict:
    if not analyses:
        return {"error": "no analyses", "total_analyzed": 0}

    valid = [a for a in analyses if "error" not in a]
    if not valid:
        return {"error": "no valid analyses", "total_analyzed": 0}

    hook_types = Counter(a.get("hook_type", "unknown") for a in valid)
    cta_types = Counter(a.get("cta_type", "none") for a in valid)
    moods = Counter(a.get("mood", "unknown") for a in valid)
    text_styles = Counter(a.get("text_style", "none") for a in valid)

    all_factors = []
    for a in valid:
        all_factors.extend(a.get("virality_factors", []))
    top_factors = Counter(all_factors).most_common(5)

    n = len(valid)
    avg_cuts = sum(a.get("estimated_cuts", 0) for a in valid) / n
    avg_score = sum(a.get("score", 0) for a in valid) / n
    face_pct = sum(1 for a in valid if a.get("has_face")) / n * 100
    screen_pct = sum(1 for a in valid if a.get("has_screen_recording")) / n * 100

    return {
        "total_analyzed": n,
        "top_hook_types": hook_types.most_common(3),
        "top_cta_types": cta_types.most_common(3),
        "top_moods": moods.most_common(3),
        "top_text_styles": text_styles.most_common(3),
        "top_virality_factors": top_factors,
        "avg_cuts": round(avg_cuts, 1),
        "avg_score": round(avg_score, 1),
        "face_percentage": round(face_pct),
        "screen_recording_percentage": round(screen_pct),
        "recommendation": {
            "hook": hook_types.most_common(1)[0][0] if hook_types else "curiosity",
            "cta": cta_types.most_common(1)[0][0] if cta_types else "link_in_bio",
            "mood": moods.most_common(1)[0][0] if moods else "energetic",
            "use_face": face_pct > 50,
            "use_screen_recording": screen_pct > 50,
        },
    }
