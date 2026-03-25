"""YouTube video/stream extraction utilities."""

import re
from typing import Optional
from urllib.parse import parse_qs, urlparse

import yt_dlp


def extract_video_id(url: str) -> str:
    """Extract video ID from various YouTube URL formats.

    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - VIDEO_ID directly
    """
    # If it's already a video ID format
    if re.match(r"^[a-zA-Z0-9_-]{11}$", url):
        return url

    parsed = urlparse(url)

    # youtu.be short format
    if parsed.netloc in ("youtu.be", "www.youtu.be"):
        return parsed.path.lstrip("/").split("?")[0]

    # youtube.com format
    if parsed.netloc in ("youtube.com", "www.youtube.com"):
        query = parse_qs(parsed.query)
        if "v" in query:
            return query["v"][0]

    raise ValueError(f"Invalid YouTube URL: {url}")


def get_video_info(url: str) -> dict:
    """Get video metadata and check if it's a live stream.

    Returns:
        dict with keys:
        - video_id: str
        - title: str
        - duration: Optional[int] in seconds
        - is_live: bool
        - is_upcoming: bool
    """
    video_id = extract_video_id(url)

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)

    return {
        "video_id": video_id,
        "title": info.get("title", "Unknown"),
        "duration": info.get("duration"),
        "is_live": info.get("is_live", False),
        "is_upcoming": info.get("is_upcoming", False),
    }


def is_live_stream(url: str) -> bool:
    """Check if URL points to a live stream."""
    info = get_video_info(url)
    return info["is_live"]


def is_upcoming_stream(url: str) -> bool:
    """Check if URL points to an upcoming stream."""
    info = get_video_info(url)
    return info["is_upcoming"]
