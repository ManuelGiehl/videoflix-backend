"""DRF serializers for video endpoints."""

from django.core.files.storage import default_storage
from rest_framework import serializers

from ..models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serialize video metadata for the dashboard."""

    thumbnail_url = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ("id", "created_at", "title", "description", "thumbnail_url", "category")

    def get_thumbnail_url(self, obj: Video) -> str:
        """Return an absolute URL for the thumbnail when possible."""
        if not obj.thumbnail:
            fallback_name = f"thumbnails/{obj.id}.jpg"
            if not default_storage.exists(fallback_name):
                return ""
            url = default_storage.url(fallback_name)
        else:
            url = obj.thumbnail.url
        request = self.context.get("request")
        if request is None:
            return url
        return request.build_absolute_uri(url)

    def get_category(self, obj: Video) -> str:
        """Return the category name (fallback to `newest` when unset)."""
        if not obj.category:
            return "newest"
        return obj.category.name

