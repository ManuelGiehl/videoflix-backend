from email.mime.image import MIMEImage

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string


def _recipient(to_email: str) -> str:
    return getattr(settings, "EMAIL_TEST_RECIPIENT", "") or to_email


def _logo_bytes() -> bytes | None:
    logo_path = getattr(settings, "BASE_DIR", None) / "templates" / "Logo.png"
    try:
        return logo_path.read_bytes()
    except Exception:
        return None


def _render(template_name: str, context: dict) -> str | None:
    try:
        return render_to_string(template_name, context)
    except TemplateDoesNotExist:
        return None


def _attach_inline_logo(message: EmailMultiAlternatives) -> None:
    logo = _logo_bytes()
    if not logo:
        return
    image = MIMEImage(logo, _subtype="png")
    image.add_header("Content-ID", "<videoflix-logo>")
    image.add_header("Content-Disposition", "inline", filename="Logo.png")
    message.attach(image)


def _send_html_email(*, subject: str, text: str, html: str | None, to_email: str) -> None:
    message = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=[_recipient(to_email)],
    )
    if html:
        message.attach_alternative(html, "text/html")
        _attach_inline_logo(message)
    message.send(fail_silently=True)


def send_activation_email(*, to_email: str, uidb64: str, token: str) -> None:
    activation_url = f"{settings.FRONTEND_BASE_URL}/api/activate/{uidb64}/{token}/"
    context = {"activation_url": activation_url, "user_name": to_email}
    html_message = _render("emails/activation_email.html", context)
    _send_html_email(
        subject="Confirm your email",
        text=f"Please activate your account: {activation_url}",
        html=html_message,
        to_email=to_email,
    )


def send_password_reset_email(*, to_email: str, uidb64: str, token: str) -> None:
    reset_url = f"{settings.FRONTEND_BASE_URL}/reset-password/{uidb64}/{token}/"
    context = {"reset_url": reset_url, "user_name": to_email}
    html_message = _render("emails/password_reset.html", context)
    _send_html_email(
        subject="Reset your Password",
        text=f"Reset your password using this link: {reset_url}",
        html=html_message,
        to_email=to_email,
    )

