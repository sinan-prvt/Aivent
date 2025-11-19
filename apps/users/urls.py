from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users.views import (
    RegisterView,
    SendOTPView,
    VerifyOTPView,
    CustomLoginView,
    SendResetOTPView,
    ResetPasswordView,
    LogoutView,
    LogoutAllView,
    ChangePasswordView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("send-otp/", SendOTPView.as_view(), name="auth-send-otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="auth-verify-otp"),

    path("login/", CustomLoginView.as_view(), name="jwt-login"),
    path("refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    
    path("send-reset-otp/", SendResetOTPView.as_view(), name="auth-send-reset-otp"),
    path("reset-password/", ResetPasswordView.as_view(), name="auth-reset-password"),
    
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("logout-all/", LogoutAllView.as_view(), name="auth-logout-all"),
    
    path("change-password/", ChangePasswordView.as_view(), name="auth-change-password"),
]
