from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.vendors.serializers import (
    VendorRegisterSerializer,
    VendorProfileSerializer,
    VendorProfileUpdateSerializer,
    ResendOTPSerializer,
)
from apps.vendors.models import VendorProfile
from apps.vendors.permissions import IsVendor
from apps.users.permissions import IsAdmin
from apps.users.utils import create_otp_for_user
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class VendorRegisterView(generics.CreateAPIView):
    serializer_class = VendorRegisterSerializer

    @swagger_auto_schema(
        operation_description="Vendor registration",
        tags=["Vendors"]
    )

    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        vendor = s.save()

        raw_otp, otp_obj = create_otp_for_user(vendor.user, "email_verify")

        send_mail(
            subject="AIVENT Vendor Registration - Verify Email",
            message=f"Your OTP is: {raw_otp}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[vendor.user.email],
            fail_silently=False,
        )

        return Response({
            "message": "Vendor registered successfully. Awaiting admin approval. Verify your email using OTP sent.",
            "vendor_id": vendor.id
        }, status=201)


class VendorProfileView(generics.RetrieveAPIView):
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    @swagger_auto_schema(
        operation_description="Get vendor profile",
        tags=["Vendors"]
    )

    def get_object(self):
        if getattr(self, "swagger_fake_view", False):
            return VendorProfile()
        return self.request.user.vendor_profile

class VendorProfileUpdateView(generics.UpdateAPIView):
    serializer_class = VendorProfileUpdateSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    @swagger_auto_schema(
        operation_description="Update vendor profile",
        tags=["Vendors"]
    )

    def get_object(self):
        if getattr(self, "swagger_fake_view", False):
            return VendorProfile()
        return self.request.user.vendor_profile


class PendingVendorsView(generics.ListAPIView):
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        operation_description="Admin: List pending vendor approvals",
        tags=["Vendor Admin"]
    )

    def get_queryset(self):
        return VendorProfile.objects.filter(status="pending")


class ApproveVendorView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        operation_description="Admin: Approve vendor",
        tags=["Vendor Admin"]
    )
    
    def post(self, request, vendor_id):
        vendor = get_object_or_404(VendorProfile, id=vendor_id)
        user = vendor.user

        if not user.email_verified:
            return Response(
                {"detail": "Vendor email not verified. Cannot approve."},
                status=400
            )

        if vendor.status != "pending":
            return Response(
                {"detail": f"Vendor already {vendor.status}."},
                status=400
            )

        vendor.status = "approved"
        vendor.save()

        from django.core.mail import send_mail
        from django.conf import settings

        send_mail(
            subject="AIVENT Vendor Approval",
            message=(
                f"Hello {user.email},\n\n"
                f"Your vendor account has been approved!\n"
                f"You can now log in and start managing your services.\n\n"
                f"Welcome to AIVENT"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({"message": "Vendor approved and email sent."}, status=200)


class RejectVendorView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        operation_description="Admin: Reject vendor",
        tags=["Vendor Admin"]
    )

    def post(self, request, vendor_id):
        vendor = get_object_or_404(VendorProfile, id=vendor_id)
        vendor.status = "rejected"
        vendor.save()
        return Response({"message": "Vendor rejected"})


class SuspendVendorView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        operation_description="Admin: Suspend vendor",
        tags=["Vendor Admin"]
    )

    def post(self, request, vendor_id):
        vendor = get_object_or_404(VendorProfile, id=vendor_id)
        vendor.status = "suspended"
        vendor.save()
        return Response({"message": "Vendor suspended"})


class VendorResendOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResendOTPSerializer

    def post(self, request):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)

        email = s.validated_data["email"]

        user = User.objects.filter(email=email, role="vendor").first()
        if not user:
            return Response({"detail": "Vendor not found"}, status=404)

        if user.email_verified:
            return Response({"detail": "Vendor email already verified"}, status=400)

        raw_otp, otp_obj = create_otp_for_user(user, "email_verify")

        send_mail(
            subject="AIVENT Vendor Email Verification",
            message=f"Your OTP is: {raw_otp}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"detail": "OTP sent again"}, status=200)
