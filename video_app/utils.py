"""FFmpeg helpers for converting videos to HLS and generating thumbnails."""

import subprocess
from pathlib import Path


def ensure_dir(path: Path) -> None:
    """Create directory path if missing."""
    path.mkdir(parents=True, exist_ok=True)


def run_ffmpeg(args: list[str]) -> None:
    """Run ffmpeg with stderr captured for diagnostics."""
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def ffmpeg_stderr(exc: subprocess.CalledProcessError) -> str:
    """Return ffmpeg stderr content decoded as UTF-8."""
    if not exc.stderr:
        return ""
    try:
        return exc.stderr.decode("utf-8", errors="replace")
    except Exception:
        return str(exc.stderr)


def hls_variant_height(resolution: str) -> int:
    """Map a resolution label to output height."""
    if resolution == "480p":
        return 480
    if resolution == "720p":
        return 720
    return 1080


def build_hls_args(source: str, out_dir: Path, resolution: str) -> list[str]:
    """Build an ffmpeg command to create an HLS variant for a given resolution."""
    height = hls_variant_height(resolution)
    playlist = str(out_dir / "index.m3u8")
    segment = str(out_dir / "%05d.ts")
    return [
        "ffmpeg",
        "-y",
        "-i",
        source,
        "-vf",
        f"scale=w=-2:h={height}",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-f",
        "hls",
        "-hls_time",
        "4",
        "-hls_playlist_type",
        "vod",
        "-hls_segment_filename",
        segment,
        playlist,
    ]


def convert_to_hls(source: str, out_dir: Path, resolution: str) -> None:
    """Convert the source into an HLS variant under the given directory."""
    ensure_dir(out_dir)
    run_ffmpeg(build_hls_args(source, out_dir, resolution))


def thumbnail_path(out_dir: Path, video_id: int) -> Path:
    """Return the thumbnail output path for a video id."""
    return out_dir / "thumbnails" / f"{video_id}.jpg"


def generate_thumbnail(source: str, out_path: Path) -> None:
    """Generate a single-frame JPEG thumbnail at 3 seconds."""
    ensure_dir(out_path.parent)
    run_ffmpeg(["ffmpeg", "-y", "-ss", "3", "-i", source, "-frames:v", "1", str(out_path)])

