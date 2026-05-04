"""AppConfig for video_app."""

from django.apps import AppConfig


class VideoAppConfig(AppConfig):
    """Video app configuration."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'video_app'

    def ready(self) -> None:
        """Load signal handlers on app startup."""
        from . import signals
