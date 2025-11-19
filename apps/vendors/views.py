from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.vendors.serializers import (
    VendorRegisterSerializer,
    VendorProfileSerializer,
    VendorProfileUpdateSerializer
)
from apps.vendors.models import VendorProfile
from apps.vendors.permissions import IsVendor
from apps.users.permissions import IsAdmin
from apps.users.utils import create_otp_for_user
from django.shortcuts import get_object_or_404


class VendorRegisterView(generics.CreateAPIView):
    serializer_class = VendorRegisterSerializer

    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        vendor = s.save()

        raw_otp, otp_obj = create_otp_for_user(vendor.user, "email_verify")

        return Response({
            "message": "Vendor registered successfully. Awaiting admin approval.",
            "vendor_id": vendor.id
        }, status=201)


class VendorProfileView(generics.RetrieveAPIView):
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_object(self):
        return self.request.user.vendor_profile


class VendorProfileUpdateView(generics.UpdateAPIView):
    serializer_class = VendorProfileUpdateSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_object(self):
        return self.request.user.vendor_profile


class PendingVendorsView(generics.ListAPIView):
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return VendorProfile.objects.filter(status="pending")


class ApproveVendorView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, vendor_id):
        vendor = get_object_or_404(VendorProfile, id=vendor_id)
        vendor.status = "approved"
        vendor.save()
        return Response({"message": "Vendor approved"})


class RejectVendorView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, vendor_id):
        vendor = get_object_or_404(VendorProfile, id=vendor_id)
        vendor.status = "rejected"
        vendor.save()
        return Response({"message": "Vendor rejected"})


class SuspendVendorView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, vendor_id):
        vendor = get_object_or_404(VendorProfile, id=vendor_id)
        vendor.status = "suspended"
        vendor.save()
        return Response({"message": "Vendor suspended"})
