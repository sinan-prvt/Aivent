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

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            raise

        user = getattr(serializer, "_validated_user", None)
        if user and user.mfa_enabled:
            mfa_session = MFASession.create_for_user(user, valid_seconds=180)
            return Response({
                "mfa_required": True,
                "session_id": str(mfa_session.id),
                "detail": "MFA required. Provide TOTP code to /api/auth/verify-mfa/"
            }, status=200)

        return super().post(request, *args, **kwargs)



class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer



class SendOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SendOTPSerializer

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

    def post(self, request, *args, **kwargs):
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
        tokens = OutstandingToken.objects.filter(user=request.user)

        for t in tokens:
            BlacklistedToken.objects.get_or_create(token=t)
        return Response({"detail": "All tokens revoked"}, status=status.HTTP_200_OK)
    
class ChangePasswordView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

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
    permission_classes = [permissions.IsAuthenticated, IsVendor]

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

    def post(self, request):
        user = request.user
        user.totp_secret = None
        user.mfa_enabled = False
        user.save()
        return Response({"detail": "MFA disabled"}, status=200)


