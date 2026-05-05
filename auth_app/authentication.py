"""Custom authentication helpers for JWT cookie auth."""

from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate requests using the `access_token` HttpOnly cookie."""

    def authenticate(self, request: Request):
        token = request.COOKIES.get("access_token")
        if not token:
            return None
        try:
            validated = self.get_validated_token(token)
            return self.get_user(validated), validated
        except TokenError:
            return self._authenticate_via_refresh(request)

    def _authenticate_via_refresh(self, request: Request):
        """Issue a new access token when a valid refresh cookie exists."""
        refresh_cookie = request.COOKIES.get("refresh_token")
        if not refresh_cookie:
            raise
        refresh = RefreshToken(refresh_cookie)
        validated = refresh.access_token
        request._new_access_token = str(validated)
        return self.get_user(validated), validated

