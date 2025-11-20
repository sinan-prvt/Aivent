from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from apps.availability.serializers import VendorAvailabilitySerializer
from apps.availability.models import VendorAvailability
from apps.vendors.permissions import IsVendor
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class VendorAvailabilityListView(generics.ListAPIView):
    serializer_class = VendorAvailabilitySerializer
    permission_classes = [IsAuthenticated, IsVendor]

    @swagger_auto_schema(
        operation_description="List vendor availability",
        tags=["Availability"]
    )

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return VendorAvailability.objects.none()

        user = self.request.user

        if not hasattr(user, "vendor_profile"):
            return VendorAvailability.objects.none()

        vendor = user.vendor_profile
        return vendor.availability.all().order_by("date")

class VendorAvailabilityCreateView(generics.CreateAPIView):
    serializer_class = VendorAvailabilitySerializer
    permission_classes = [IsAuthenticated, IsVendor]

    @swagger_auto_schema(
        operation_description="Add availability date",
        tags=["Availability"]
    )

    def perform_create(self, serializer):
        vendor = self.request.user.vendor_profile
        serializer.save(vendor=vendor)


class VendorAvailabilityDeleteView(generics.DestroyAPIView):
    serializer_class = VendorAvailabilitySerializer
    permission_classes = [IsAuthenticated, IsVendor]

    @swagger_auto_schema(
        operation_description="Delete vendor availability",
        tags=["Availability"]
    )

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return VendorAvailability.objects.none()

        user = self.request.user
        if not hasattr(user, "vendor_profile"):
            return VendorAvailability.objects.none()

        vendor = user.vendor_profile
        return vendor.availability.all()
