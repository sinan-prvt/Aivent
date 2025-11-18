from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.bookings.serializers import BookingSerializer
from apps.bookings.models import Booking
from apps.vendors.permissions import IsVendor
from apps.vendors.models import VendorProfile
from apps.availability.models import VendorAvailability


class CreateBookingView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        vendor_id = self.request.data.get("vendor_id")
        service_id = self.request.data.get("service_id")

        vendor_profile = get_object_or_404(VendorProfile, id=vendor_id)

        serializer.save(
            customer=self.request.user,
            vendor=vendor_profile,
            service_id=service_id
        )


class VendorBookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        vendor = self.request.user.vendor_profile
        return Booking.objects.filter(vendor=vendor).order_by("-created_at")
    

class CustomerBookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(customer=self.request.user).order_by("-created_at")


class AcceptBookingView(generics.UpdateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        return Booking.objects.filter(vendor=self.request.user.vendor_profile)

    def perform_update(self, serializer):
        serializer.save(status="accepted")


class RejectBookingView(generics.UpdateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        return Booking.objects.filter(vendor=self.request.user.vendor_profile)

    def perform_update(self, serializer):
        serializer.save(status="rejected")