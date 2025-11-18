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
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.shortcuts import get_object_or_404



class VendorRegisterView(generics.CreateAPIView):
    serializer_class = VendorProfileSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "Vendor registered successfully. Awaiting admin verification.",
            "vendor_id": vendor.id
        }, status=status.HTTP_201_CREATED)



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



class VendorListView(generics.ListAPIView):
    queryset = VendorProfile.objects.all()
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticated, IsAdmin]



class PendingVendorsView(generics.ListAPIView):
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return VendorProfile.objects.filter(status="pending")



class ApproveVendorView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, vendor_id):
        vendor = get_object_or_404(VendorProfile, user__id=vendor_id)
        vendor.status = "approved"
        vendor.save()
        return Response({"message": "Vendor approved"}, status=status.HTTP_200_OK)



class RejectVendorView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, vendor_id):
        vendor = get_object_or_404(VendorProfile, user__id=vendor_id)
        vendor.status = "rejected"
        vendor.save()
        return Response({"message": "Vendor rejected"}, status=status.HTTP_200_OK)



class SuspendVendorView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, vendor_id):
        vendor = get_object_or_404(VendorProfile, user__id=vendor_id)
        vendor.status = "suspended"
        vendor.save()
        return Response({"message": "Vendor suspended"}, status=status.HTTP_200_OK)