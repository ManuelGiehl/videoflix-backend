"""Middleware that renews the access token cookie when needed."""


class TokenRenewalMiddleware:
    """Set a renewed access cookie created during authentication."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        token = getattr(request, "_new_access_token", "")
        if token:
            response.set_cookie(
                "access_token",
                token,
                httponly=True,
                secure=False,
                samesite="Lax",
                path="/",
            )
        return response

