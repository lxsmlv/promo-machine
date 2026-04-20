import subprocess
import json
from typing import Optional, Dict, List
from pathlib import Path


def download_video(url: str, output_dir: str) -> Optional[Dict]:
    """Download a video from TikTok or VK using yt-dlp and extract metadata.

    Args:
        url - Video URL (TikTok or VK)
        output_dir - Directory to save downloaded videos

    Returns:
        Dictionary with video metadata and file path, or None if download failed
    """
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    output_template = str(output_dir_path / "%(id)s.%(ext)s")

    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-download", url],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return None
        meta = json.loads(result.stdout)

        subprocess.run(
            ["yt-dlp", "-o", output_template, "--no-check-certificate", url],
            capture_output=True, timeout=120,
        )

        video_id = meta.get("id", "unknown")
        ext = meta.get("ext", "mp4")
        file_path = output_dir_path / f"{video_id}.{ext}"

        return {
            "id": video_id,
            "url": url,
            "description": meta.get("description", ""),
            "views": meta.get("view_count", 0) or 0,
            "likes": meta.get("like_count", 0) or 0,
            "comments": meta.get("comment_count", 0) or 0,
            "shares": meta.get("repost_count", 0) or 0,
            "duration": meta.get("duration", 0) or 0,
            "uploader": meta.get("uploader", ""),
            "tags": meta.get("tags", []) or [],
            "file_path": str(file_path) if file_path.exists() else None,
        }
    except Exception as e:
        print(f"Download error for {url}: {e}")
        return None


def search_and_download(urls: List[str], output_dir: str = "data/downloads/tiktok") -> List[Dict]:
    """Download multiple videos.

    Args:
        urls - List of video URLs
        output_dir - Directory to save videos

    Returns:
        List of download results with metadata
    """
    results = []
    for url in urls:
        meta = download_video(url, output_dir)
        if meta:
            results.append(meta)
    return results
