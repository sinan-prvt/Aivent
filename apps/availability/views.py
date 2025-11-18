from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.availability.serializers import VendorAvailabilitySerializer
from apps.availability.models import VendorAvailability
from apps.vendors.permissions import IsVendor


class VendorAvailabilityListView(generics.ListAPIView):
    serializer_class = VendorAvailabilitySerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        vendor = self.request.user.vendor_profile
        return vendor.availability.all().order_by("date")


class VendorAvailabilityCreateView(generics.CreateAPIView):
    serializer_class = VendorAvailabilitySerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def perform_create(self, serializer):
        vendor = self.request.user.vendor_profile
        serializer.save(vendor=vendor)


class VendorAvailabilityDeleteView(generics.DestroyAPIView):
    serializer_class = VendorAvailabilitySerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        vendor = self.request.user.vendor_profile
        return vendor.availability.all()
