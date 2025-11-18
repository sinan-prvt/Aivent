from django.urls import path
from apps.users.views import RegisterView, SendOTPView, VerifyOTPView, SendResetOTPView, ResetPasswordView, CustomLoginView


urlpattern = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("send-otp/", SendOTPView.as_view(), name="auth-send-otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="auth-verify-otp"),

    path("send-reset-otp/", SendResetOTPView.as_view(), name="auth-send-reset-otp"),
    path("reset-password/", ResetPasswordView.as_view(), name="auth-reset-password"),

]