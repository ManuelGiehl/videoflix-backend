from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from ..utils import (
    create_activation_token,
    create_activation_uidb64,
    is_activation_token_valid,
    parse_activation_uidb64,
)
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

        uidb64 = create_activation_uidb64(user.id)
        token = create_activation_token(user)
        self._send_activation_email(email=email, uidb64=uidb64, token=token)

        return Response(
            {"user": UserSerializer(user).data, "token": token},
            status=HTTP_201_CREATED,
        )

    def _send_activation_email(self, email: str, uidb64: str, token: str) -> None:
        send_mail(
            subject="Videoflix – Activate your account",
            message=f"Please activate your account: /api/activate/{uidb64}/{token}/",
            from_email=None,
            recipient_list=[email],
            fail_silently=True,
        )


class ActivateView(APIView):
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

