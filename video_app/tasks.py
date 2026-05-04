import logging
import subprocess

from django_rq import job
from django.conf import settings

from .models import Video
from .utils import convert_to_hls, ffmpeg_stderr, generate_thumbnail, thumbnail_path


logger = logging.getLogger(__name__)


@job("default")
def process_video(video_id: int) -> None:
    video = Video.objects.filter(id=video_id).first()
    if not video or video.processing_done or not video.video_file:
        return
    video.hls_root = f"hls/{video.id}"
    source = video.video_file.path
    base_dir = settings.MEDIA_ROOT / video.hls_root
    try:
        for resolution in ["480p", "720p", "1080p"]:
            convert_to_hls(source, base_dir / resolution, resolution)
        thumb = thumbnail_path(settings.MEDIA_ROOT, video.id)
        generate_thumbnail(source, thumb)
    except subprocess.CalledProcessError as exc:
        logger.error("ffmpeg failed for video_id=%s: %s", video.id, ffmpeg_stderr(exc))
        return

    video.thumbnail.name = str(thumb.relative_to(settings.MEDIA_ROOT))
    video.processing_done = True
    video.save(update_fields=["hls_root", "thumbnail", "processing_done"])
   