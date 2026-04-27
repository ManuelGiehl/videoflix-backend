from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email")


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirmed_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        generic_error = "Please check your input and try again."

        password = attrs.get("password")
        confirmed_password = attrs.get("confirmed_password")
        if password != confirmed_password:
            raise serializers.ValidationError(generic_error)

        email = attrs.get("email", "").strip().lower()
        if not email:
            raise serializers.ValidationError(generic_error)

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(generic_error)

        attrs["email"] = email
        return attrs


