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
)
from apps.users.models import OTP
from apps.users.utils import create_otp_for_user, verify_otp_entry
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from apps.users.permissions import IsVendor, IsAdmin, IsCustomer



User = get_user_model()



class CustomLoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomLoginSerializer



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
        serializers = LogoutSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        refresh_token = serializers.validated_data("refresh")

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        
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