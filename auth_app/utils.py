from django.core.signing import TimestampSigner


def create_activation_token(user_id: int) -> str:
    return TimestampSigner().sign(str(user_id))

