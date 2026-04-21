from typing import List, Dict
from backend.renderer.composer import render_video
import uuid

def render_single(args: Dict) -> Dict:
    try:
        output = render_video(
            template=args["template"],
            screenshots=args["screenshots"],
            hook_text=args["hook_text"],
            cta_text=args["cta_text"],
            audio_path=args.get("audio_path"),
            output_path=args["output_path"],
            duration=args.get("duration", 30),
        )
        return {"status": "done", "output": output, "id": args["id"]}
    except Exception as e:
        return {"status": "error", "error": str(e), "id": args["id"]}

def batch_render(jobs: List[Dict]) -> List[Dict]:
    results = []
    for job in jobs:
        results.append(render_single(job))
    return results
