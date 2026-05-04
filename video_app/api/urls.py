"""URL routing for the video API."""

from django.urls import path

from .views import VideoListView, VideoManifestView, VideoSegmentView


urlpatterns = [
    path("", VideoListView.as_view(), name="video-list"),
    path(
        "<int:movie_id>/<str:resolution>/index.m3u8",
        VideoManifestView.as_view(),
        name="video-manifest",
    ),
    path(
        "<int:movie_id>/<str:resolution>/<str:segment>",
        VideoSegmentView.as_view(),
        name="video-segment",
    ),
]

