"""Database models for video metadata and categories."""

from django.db import models


class VideoCategory(models.Model):
    """Video category used for grouping on the dashboard."""

    name = models.CharField(max_length=64, unique=True)

    def __str__(self) -> str:
        return self.name


class Video(models.Model):
    """Video metadata plus processing state for HLS streaming."""

    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to="videos/", blank=True, null=True)
    thumbnail = models.FileField(upload_to="thumbnails/", blank=True, null=True)
    hls_root = models.CharField(max_length=255, blank=True)
    processing_done = models.BooleanField(default=False)
    category = models.ForeignKey(
        VideoCategory,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="videos",
    )

    def __str__(self) -> str:
        return self.title
