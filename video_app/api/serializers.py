from rest_framework import serializers

from ..models import Video


class VideoSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ("id", "created_at", "title", "description", "thumbnail_url", "category")

    def get_thumbnail_url(self, obj: Video) -> str:
        if not obj.thumbnail:
            return ""
        request = self.context.get("request")
        if request is None:
            return obj.thumbnail.url
        return request.build_absolute_uri(obj.thumbnail.url)

    def get_category(self, obj: Video) -> str:
        if not obj.category:
            return ""
        return obj.category.name

