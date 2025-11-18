from django.urls import path
from apps.users.views import (
    RegisterView,
    SendOTPView,
    VerifyOTPView,
    SendResetOTPView,
    ResetPasswordView,
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("send-otp/", SendOTPView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),
    path("send-reset-otp/", SendResetOTPView.as_view()),
    path("reset-password/", ResetPasswordView.as_view()),
]
