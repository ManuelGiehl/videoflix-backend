from django.conf import settings
from django.core.mail import send_mail
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string


def send_activation_email(*, to_email: str, uidb64: str, token: str) -> None:
    recipient = getattr(settings, "EMAIL_TEST_RECIPIENT", "") or to_email
    activation_url = f"{settings.FRONTEND_BASE_URL}/api/activate/{uidb64}/{token}/"
    try:
        html_message = render_to_string(
            "emails/activation_email.html",
            {"activation_url": activation_url},
        )
    except TemplateDoesNotExist:
        html_message = None

    send_mail(
        subject="Videoflix – Activate your account",
        message=f"Please activate your account: {activation_url}",
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=[recipient],
        html_message=html_message,
        fail_silently=True,
    )

