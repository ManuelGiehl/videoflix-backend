from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView

from ..utils import create_activation_token
from .serializers import RegisterSerializer, UserSerializer


User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = User(username=email, email=email, is_active=False)
        user.set_password(password)
        user.save()

        token = create_activation_token(user.id)
        self._send_activation_email(email=email, token=token)

        return Response(
            {"user": UserSerializer(user).data, "token": token},
            status=HTTP_201_CREATED,
        )

    def _send_activation_email(self, email: str, token: str) -> None:
        send_mail(
            subject="Videoflix – Activate your account",
            message=f"Please activate your account using this token: {token}",
            from_email=None,
            recipient_list=[email],
            fail_silently=True,
        )

