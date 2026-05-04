"""DRF API views for authentication and account lifecycle endpoints."""

from django.contrib.auth import authenticate, get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from ..emails import send_activation_email, send_password_reset_email
from ..utils import (
    create_activation_token,
    create_activation_uidb64,
    is_activation_token_valid,
    parse_activation_uidb64,
)
from .serializers import (
    LoginSerializer,
    PasswordConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserSerializer,
)


User = get_user_model()


class RegisterView(APIView):
    """Register a new user and trigger activation email."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = User(username=email, email=email, is_active=False)
        user.set_password(password)
        user.save()

        uidb64 = create_activation_uidb64(user.id)
        token = create_activation_token(user)
        send_activation_email(to_email=email, uidb64=uidb64, token=token)

        return Response(
            {"user": UserSerializer(user).data, "token": token},
            status=HTTP_201_CREATED,
        )


class ActivateView(APIView):
    """Activate a user account using uidb64 and token."""

    permission_classes = [AllowAny]

    def get(self, request, uidb64: str, token: str):
        user_id = parse_activation_uidb64(uidb64)
        if user_id is None:
            return Response({"message": "Activation failed."}, status=HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"message": "Activation failed."}, status=HTTP_400_BAD_REQUEST)

        if not is_activation_token_valid(user, token):
            return Response({"message": "Activation failed."}, status=HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save(update_fields=["is_active"])

        return Response({"message": "Account successfully activated."}, status=HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """Send password reset email if a user exists (no enumeration)."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = User.objects.filter(email__iexact=email).first()
        if user is not None:
            self._send_reset_email(user)
        return Response(
            {"detail": "An email has been sent to reset your password."},
            status=HTTP_200_OK,
        )

    def _send_reset_email(self, user) -> None:
        uidb64 = create_activation_uidb64(user.id)
        token = create_activation_token(user)
        send_password_reset_email(to_email=user.email, uidb64=uidb64, token=token)


class PasswordConfirmView(APIView):
    """Confirm password reset using uidb64 and token."""

    permission_classes = [AllowAny]

    def post(self, request, uidb64: str, token: str):
        serializer = PasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = parse_activation_uidb64(uidb64)
        user = User.objects.filter(id=user_id).first() if user_id else None
        if user is None or not is_activation_token_valid(user, token):
            return Response({"detail": "Password reset failed."}, status=HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        return Response(
            {"detail": "Your Password has been successfully reset."},
            status=HTTP_200_OK,
        )


class LoginView(APIView):
    """Authenticate user and set HttpOnly JWT cookies."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(request=request, username=email, password=password)
        if user is None or not getattr(user, "is_active", False):
            return Response(
                {"detail": "Please check your input and try again."},
                status=HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response(
            {"detail": "Login successful.", "user": UserSerializer(user).data},
            status=HTTP_200_OK,
        )

        self._set_auth_cookies(response, access_token=access_token, refresh_token=refresh_token)
        return response

    def _set_auth_cookies(self, response, access_token: str, refresh_token: str) -> None:
        cookie_kwargs = {
            "httponly": True,
            "secure": False,
            "samesite": "Lax",
            "path": "/",
        }

        response.set_cookie("access_token", access_token, **cookie_kwargs)
        response.set_cookie("refresh_token", refresh_token, **cookie_kwargs)


class LogoutView(APIView):
    """Invalidate refresh token (blacklist) and clear cookies."""

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"detail": "Refresh token missing."}, status=HTTP_400_BAD_REQUEST)

        try:
            RefreshToken(refresh_token).blacklist()
        except Exception:
            return Response({"detail": "Refresh token missing."}, status=HTTP_400_BAD_REQUEST)

        response = Response(
            {
                "detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."
            },
            status=HTTP_200_OK,
        )
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")
        return response


class TokenRefreshView(APIView):
    """Issue a new access token using the refresh_token cookie."""

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"detail": "Refresh token missing."}, status=HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
        except TokenError:
            return Response({"detail": "Invalid refresh token."}, status=HTTP_401_UNAUTHORIZED)

        response = Response(
            {"detail": "Token refreshed", "access": access_token},
            status=HTTP_200_OK,
        )
        response.set_cookie(
            "access_token",
            access_token,
            httponly=True,
            secure=False,
            samesite="Lax",
            path="/",
        )
        return response

