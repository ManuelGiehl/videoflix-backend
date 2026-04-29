from django.urls import path

from .views import (
    ActivateView,
    LoginView,
    LogoutView,
    PasswordResetRequestView,
    RegisterView,
    TokenRefreshView,
)


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("activate/<str:uidb64>/<str:token>/", ActivateView.as_view(), name="activate"),
    path("login/", LoginView.as_view(), name="login"),
    path("password_reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]

