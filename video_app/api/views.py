"""Video API endpoints: list videos and serve HLS artifacts."""

from django.http import FileResponse, Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from ..models import Video
from ..hls import get_manifest_path, get_segment_path, is_safe_segment_name
from .serializers import VideoSerializer


def unique_by_id(videos):
    """Return a stable list of videos deduplicated by primary key."""
    seen = set()
    unique = []
    for video in videos:
        if video.id in seen:
            continue
        seen.add(video.id)
        unique.append(video)
    return unique


class VideoListView(APIView):
    """List all available videos (JWT required)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        videos = Video.objects.order_by("-created_at")
        data = VideoSerializer(
            unique_by_id(videos),
            many=True,
            context={"request": request},
        ).data
        return Response(data, status=HTTP_200_OK)


class VideoManifestView(APIView):
    """Serve a per-resolution HLS manifest (index.m3u8)."""

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id: int, resolution: str):
        video = Video.objects.filter(id=movie_id).first()
        if not video or not video.hls_root:
            raise Http404()

        manifest_path = get_manifest_path(video, resolution)
        if not manifest_path.exists():
            raise Http404()

        return FileResponse(
            manifest_path.open("rb"),
            content_type="application/vnd.apple.mpegurl",
        )


class VideoSegmentView(APIView):
    """Serve a single HLS transport stream segment (video/MP2T)."""

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id: int, resolution: str, segment: str):
        if not is_safe_segment_name(segment):
            raise Http404()

        video = Video.objects.filter(id=movie_id).first()
        if not video or not video.hls_root:
            raise Http404()

        segment_path = get_segment_path(video, resolution, segment)
        if not segment_path.exists():
            raise Http404()

        return FileResponse(
            segment_path.open("rb"),
            content_type="video/MP2T",
        )

