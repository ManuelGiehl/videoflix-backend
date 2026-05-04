from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Video


@receiver(post_save, sender=Video)
def trigger_video_processing(sender, instance: Video, created: bool, **kwargs) -> None:
    if not created or not instance.video_file or instance.processing_done:
        return
    from .tasks import process_video
    process_video.delay(instance.id)

