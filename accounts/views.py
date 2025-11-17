from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import (
    RegisterSerializer,
    VendorRegisterSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer
)
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .utils import create_otp_for_user, verify_otp_entry
from .models import OTP, VendorProfile

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        data = {
            "id": str(user.id),
            "email": user.email,
            "message": "User registered successfully. Verify email (if implemented)."
        }

        return Response(data, status=status.HTTP_201_CREATED)

class VendorRegisterView(generics.CreateAPIView):
    serializer_class = VendorRegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "Vendor registered successfully. Awaiting admin verification.",
            "vendor_id": user.id
        }, status=status.HTTP_201_CREATED)


class SendOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SendOTPSerializer

    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)

        email = s.validated_data['email']
        purpose = s.validated_data['purpose']

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "User with this email not found."}, status=status.HTTP_404_NOT_FOUND)

        raw_otp, otp_obj = create_otp_for_user(user, purpose=purpose)

        print("DEBUG OTP =", raw_otp)

        subject = "Your AIVENT OTP code"
        message = f"Your OTP is {raw_otp} (expires in 10 minutes)."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)

        return Response({"detail": "OTP sent to email."}, status=status.HTTP_200_OK)


class VerifyOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        email = s.validated_data['email']
        purpose = s.validated_data['purpose']
        otp_value = s.validated_data['otp']

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        now = timezone.now()

        otp_qs = OTP.objects.filter(
            user=user,
            purpose=purpose,
            used=False,
            expires_at__gt=now
        ).order_by('-created_at')

        if not otp_qs.exists():
            return Response({"detail": "No valid OTP found or expired."}, status=status.HTTP_400_BAD_REQUEST)

        otp_obj = otp_qs.first()
        if verify_otp_entry(otp_obj, otp_value):
            otp_obj.used = True
            otp_obj.save()

            if purpose == 'email_verify':
                pass

            return Response({"detail": "OTP verified."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)


class SendResetOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SendOTPSerializer

    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)

        email = s.validated_data['email']
        user = User.objects.filter(email=email).first()

        if not user:
            return Response({"detail": "No user found with this email."}, status=404)

        raw_otp, otp_obj = create_otp_for_user(user, purpose="reset_password")

        print("RESET PASSWORD OTP =", raw_otp)

        send_mail(
            "AIVENT Password Reset OTP",
            f"Your OTP is {raw_otp}. It expires in 10 minutes.",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False
        )

        return Response({"detail": "Password reset OTP sent."}, status=200)


class ResetPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)

        email = s.validated_data["email"]
        new_password = s.validated_data["new_password"]

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "User not found."}, status=404)

        otp_obj = OTP.objects.filter(
            user=user,
            purpose="reset_password",
            used=True,
        ).order_by("-created_at").first()

        if not otp_obj:
            return Response({"detail": "OTP not verified yet."}, status=400)

        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password reset successfully."}, status=200)


