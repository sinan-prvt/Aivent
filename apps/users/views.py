from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.users.serializers import (
    RegisterSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer,
    CustomLoginSerializer,
    LogoutSerializer,
    ChangePasswordSerializer,
    VerifyMFASerializer,
    ConfirmEnableMfaSerializer,
    serializers,
    EnableMfaSerializer,
)
from apps.users.models import OTP
from apps.users.utils import create_otp_for_user, verify_otp_entry
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from apps.users.permissions import IsVendor, IsAdmin, IsCustomer
import pyotp
import qrcode
import io
import base64
from rest_framework import permissions
from .models import MFASession
from django.conf import settings
from apps.core.recaptcha import verify_recaptcha
from apps.core.captcha_utils import (
    requires_captcha,
    increment_failed_attempts,
    reset_failed_attempts
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()


def qrcode_base64_from_uri(uri):
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return "data:image/png;base64," + b64



class CustomLoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomLoginSerializer

    @swagger_auto_schema(
        operation_description="Login with email + password + reCAPTCHA + optional MFA",
        tags=["Authentication"]
    )

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        ip = request.META.get("REMOTE_ADDR")
        key = f"{email}:{ip}" if email else ip

        if requires_captcha(key):
            token = request.data.get("recaptcha_token")
            if not token:
                return Response({
                    "success": False,
                    "message": "reCAPTCHA required",
                    "errors": {"recaptcha": ["This action requires reCAPTCHA verification"]}
                }, status=status.HTTP_400_BAD_REQUEST)

            resp = verify_recaptcha(token, remoteip=ip)
            score = resp.get("score") or 0

            if not resp.get("success") or score < float(settings.RECAPTCHA_MIN_SCORE):
                increment_failed_attempts(key)
                return Response({
                    "success": False,
                    "message": "reCAPTCHA validation failed",
                    "errors": {"recaptcha": ["validation failed"], "score": [score]}
                }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            increment_failed_attempts(key)

            if requires_captcha(key):
                return Response({
                    "success": False,
                    "message": "Invalid credentials, reCAPTCHA is now required",
                    "errors": {"auth": ["invalid"], "captcha_required": True}
                }, status=status.HTTP_401_UNAUTHORIZED)

            return Response({
                "success": False,
                "message": "Invalid credentials",
                "errors": {"auth": ["invalid credentials"]}
            }, status=status.HTTP_401_UNAUTHORIZED)

        user = getattr(serializer, "_validated_user", None)
        reset_failed_attempts(key)

        if user and user.mfa_enabled:
            mfa_session = MFASession.create_for_user(user, valid_seconds=180)
            return Response({
                "success": True,
                "mfa_required": True,
                "session_id": str(mfa_session.id),
                "message": "MFA required. Submit TOTP to /api/auth/verify-mfa/"
            })

        tokens = super().post(request, *args, **kwargs)
        return Response({
            "success": True,
            "message": "Logged in",
            "data": tokens.data
        }, status=200)



class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
        operation_description="Register a new user with email + password + OTP verification",
        tags=["Authentication"]
    )

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class SendOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SendOTPSerializer

    @swagger_auto_schema(
        operation_description="Send OTP for email verification or password reset",
        tags=["OTP"]
    )

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        purpose = serializer.validated_data["purpose"]

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "User not found"}, status=404)

        raw_otp, otp_obj = create_otp_for_user(user, purpose)

        from django.core.mail import send_mail
        from django.conf import settings

        send_mail(
            subject="AIVENT OTP Verification",
            message=f"Your OTP is: {raw_otp}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"detail": "OTP sent"}, status=200)



class VerifyOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer

    @swagger_auto_schema(
        operation_description="Verify OTP for email verification or actions",
        tags=["OTP"]
    )

    def post(self, request):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)

        email = s.validated_data["email"]
        otp_value = s.validated_data["otp"]
        purpose = s.validated_data["purpose"]

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "User not found"}, status=404)

        otp_obj = OTP.objects.filter(
            user=user, purpose=purpose, used=False, expires_at__gt=timezone.now()
        ).order_by("-created_at").first()

        if not otp_obj:
            return Response({"detail": "Invalid or expired OTP"}, status=400)

        if not verify_otp_entry(otp_obj, otp_value):
            return Response({"detail": "Invalid OTP"}, status=400)

        otp_obj.used = True
        otp_obj.save()

        if purpose == "email_verify":
            user.email_verified = True
            user.save()

        return Response({"detail": "OTP verified successfully"}, status=200)




class SendResetOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SendOTPSerializer

    @swagger_auto_schema(
        operation_description="Send OTP for resetting password",
        tags=["Password Reset"]
    )

    def post(self, request):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)

        email = s.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if not user:
            return Response({"detail": "User not found"}, status=404)

        raw_otp, otp_obj = create_otp_for_user(user, "reset_password")

        return Response({"detail": "Reset OTP sent"}, status=200)



class ResetPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    @swagger_auto_schema(
        operation_description="Reset password using verified OTP",
        tags=["Password Reset"]
    )

    def post(self, request):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)

        email = s.validated_data["email"]
        new_password = s.validated_data["new_password"]

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "User not found"}, status=404)

        otp_obj = OTP.objects.filter(
            user=user, purpose="reset_password", used=True
        ).order_by("-created_at").first()

        if not otp_obj:
            return Response({"detail": "OTP not verified"}, status=400)

        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password reset successful"}, status=200)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout by blacklisting refresh token",
        tags=["Authentication"]
    )

    def post(self, request, *args, **kwargs):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"detail": "Could not blacklist token"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Logged out successfully"}, status=status.HTTP_200_OK)


class LogoutAllView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout from all devices by blacklisting all tokens",
        tags=["Authentication"]
    )

    def post(self, request, *args, **kwargs):
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
        tokens = OutstandingToken.objects.filter(user=request.user)

        for t in tokens:
            BlacklistedToken.objects.get_or_create(token=t)
        return Response({"detail": "All tokens revoked"}, status=status.HTTP_200_OK)


class ChangePasswordView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    @swagger_auto_schema(
        operation_description="Change user password",
        tags=["Authentication"]
    )

    def post(self, request):
        user = request.user
        s =  self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)

        old = s.validated_data["old_password"]
        new = s.validated_data["new_password"]

        if not user.check_password(old):
            return Response({"detail": "Old password is incorrect"}, status=400)
        
        user.set_password(new)
        user.save()

        return Response({"detail": "Password changed successfully"}, status=200)
    

class VendorDashboardView(APIView):
    permission_classes = [IsVendor]

    def get(self, request):
        return Response({"message": "Vendor dashboard"})
    

class AdminPanelView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({"message": "Admin Panel"})
    

class CustomerHistoryView(APIView):
    permission_classes = [IsCustomer]

    def get(self, request):
        return Response({"orders": []})
    

class VerifyMFAView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyMFASerializer

    @swagger_auto_schema(
        operation_description="Verify MFA TOTP and return JWT tokens",
        tags=["MFA"]
    )

    def post(self, request):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        session_id = s.validated_data["session_id"]
        code = s.validated_data["code"]

        mfs = MFASession.objects.filter(id=session_id, used=False).first()
        if not mfs or mfs.is_expired():
            return Response({"detail": "Invalid or expired MFA session"}, status=400)

        user = mfs.user
        if not user.totp_secret:
            return Response({"detail": "User has no TOTP configured"}, status=400)

        totp = pyotp.TOTP(user.totp_secret)
        if not totp.verify(code, valid_window=1):
            return Response({"detail": "Invalid TOTP code"}, status=400)

        mfs.used = True
        mfs.save()

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response({
            "access": access,
            "refresh": refresh_token,
        }, status=200)


class EnableMFAView(generics.GenericAPIView):
    serializer_class = EnableMfaSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendor]

    @swagger_auto_schema(
        operation_description="Generate TOTP QR and secret for enabling MFA",
        tags=["MFA"]
    )

    def get(self, request):
        user = request.user
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        otpauth = totp.provisioning_uri(name=user.email, issuer_name="AIVENT")
        qr_b64 = qrcode_base64_from_uri(otpauth)
        return Response({"secret": secret, "otpauth_url": otpauth, "qr": qr_b64})


class ConfirmEnableMFAView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsVendor]
    serializer_class = ConfirmEnableMfaSerializer

    @swagger_auto_schema(
        operation_description="Verify TOTP code to enable MFA",
        tags=["MFA"]
    )

    def post(self, request):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)

        secret = s.validated_data["secret"]
        code = s.validated_data["code"]

        totp = pyotp.TOTP(secret)
        if not totp.verify(code, valid_window=1):
            return Response({"detail": "Invalid TOTP code"}, status=400)

        user = request.user
        user.totp_secret = secret
        user.mfa_enabled = True
        user.save()

        return Response({"detail": "MFA enabled"}, status=200)


class DisableMFAView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsVendor]
    serializer_class = serializers.Serializer

    @swagger_auto_schema(
        operation_description="Disable MFA for vendor",
        tags=["MFA"]
    )

    def post(self, request):
        user = request.user
        user.totp_secret = None
        user.mfa_enabled = False
        user.save()
        return Response({"detail": "MFA disabled"}, status=200)


