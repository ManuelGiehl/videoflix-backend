"""Path helpers for HLS manifest and segments under MEDIA_ROOT."""

from pathlib import Path

from django.conf import settings

from .models import Video


def get_manifest_path(video: Video, resolution: str) -> Path:
    """Return the expected manifest path for a video and resolution."""
    return Path(settings.MEDIA_ROOT) / video.hls_root / resolution / "index.m3u8"


def get_segment_path(video: Video, resolution: str, segment: str) -> Path:
    """Return the expected segment path for a video and resolution."""
    return Path(settings.MEDIA_ROOT) / video.hls_root / resolution / segment


def is_safe_segment_name(segment: str) -> bool:
    """Prevent path traversal and enforce TS segment naming."""
    if "/" in segment or "\\" in segment:
        return False
    if ".." in segment:
        return False
    return segment.endswith(".ts")

