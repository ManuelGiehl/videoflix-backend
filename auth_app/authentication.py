"""Custom authentication helpers for JWT cookie auth."""

from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate requests using the `access_token` HttpOnly cookie."""

    def authenticate(self, request: Request):
        token = request.COOKIES.get("access_token")
        if not token:
            return None
        validated = self.get_validated_token(token)
        return self.get_user(validated), validated

