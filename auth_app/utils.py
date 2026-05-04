"""Token helpers shared between activation and password reset flows."""

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


def create_activation_uidb64(user_id: int) -> str:
    """Create a URL-safe base64 encoded user id."""
    return urlsafe_base64_encode(force_bytes(user_id))


def create_activation_token(user) -> str:
    """Create a time-sensitive token for the given user."""
    return default_token_generator.make_token(user)


def parse_activation_uidb64(uidb64: str) -> int | None:
    """Parse a base64 user id and return int or None if invalid."""
    try:
        return int(urlsafe_base64_decode(uidb64).decode())
    except (TypeError, ValueError, UnicodeDecodeError):
        return None


def is_activation_token_valid(user, token: str) -> bool:
    """Validate the token for the given user."""
    return default_token_generator.check_token(user, token)

