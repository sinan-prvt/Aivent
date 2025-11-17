from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import VendorRegisterView


urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="auth-register"),
    path("vendor/register/", VendorRegisterView.as_view(), name="vendor-register"),
    path("send-otp/", views.SendOTPView.as_view(), name="auth-send-otp"),
    path("verify-otp/", views.VerifyOTPView.as_view(), name="auth-verify-otp"),

    path("login/", TokenObtainPairView.as_view(), name="jwt-login"),
    path("refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),

    path("send-reset-otp/", views.SendResetOTPView.as_view(), name="auth-send-reset-otp"),
    path("reset-password/", views.ResetPasswordView.as_view(), name="auth-reset-password"),

]
