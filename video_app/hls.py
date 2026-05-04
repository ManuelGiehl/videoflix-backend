from pathlib import Path

from django.conf import settings

from .models import Video


def get_manifest_path(video: Video, resolution: str) -> Path:
    return Path(settings.MEDIA_ROOT) / video.hls_root / resolution / "index.m3u8"


def get_segment_path(video: Video, resolution: str, segment: str) -> Path:
    return Path(settings.MEDIA_ROOT) / video.hls_root / resolution / segment


def is_safe_segment_name(segment: str) -> bool:
    if "/" in segment or "\\" in segment:
        return False
    if ".." in segment:
        return False
    return segment.endswith(".ts")

