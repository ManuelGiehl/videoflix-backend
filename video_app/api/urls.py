from django.urls import path

from .views import VideoApiHealthView


urlpatterns = [
    path("health/", VideoApiHealthView.as_view(), name="video-api-health"),
]

