from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users.views import (
    RegisterView,
    CustomLoginView,
    SendOTPView,
    VerifyOTPView,
    SendResetOTPView,
    ResetPasswordView,
)
urlpattern = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("send-otp/", SendOTPView.as_view(), name="auth-send-otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="auth-verify-otp"),

    path("login/", CustomLoginView.as_view(), name="jwt-login"),
    path("refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("send-reset-otp/", SendResetOTPView.as_view(), name="auth-send-reset-otp"),
    path("reset-password/", ResetPasswordView.as_view(), name="auth-reset-password"),

]