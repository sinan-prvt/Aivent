from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.services.serializers import VendorServiceSerializer
from apps.services.models import VendorService
from apps.vendors.permissions import IsVendor


class VendorServiceCreateView(generics.CreateAPIView):
    serializer_class = VendorServiceSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def perform_create(self, serializer):
        vendor_profile = self.request.user.vendor_profile
        serializer.save(vendor=vendor_profile)


class VendorServiceListView(generics.ListAPIView):
    serializer_class = VendorServiceSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        return self.request.user.vendor_profile.services.all()


class VendorServiceUpdateView(generics.UpdateAPIView):
    serializer_class = VendorServiceSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        return self.request.user.vendor_profile.services.all()


class VendorServiceDeleteView(generics.DestroyAPIView):
    serializer_class = VendorServiceSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        return self.request.user.vendor_profile.services.all()
