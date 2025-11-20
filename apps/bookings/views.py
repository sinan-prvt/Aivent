from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.bookings.serializers import BookingSerializer
from apps.bookings.models import Booking
from apps.vendors.permissions import IsVendor
from apps.vendors.models import VendorProfile
from apps.availability.models import VendorAvailability
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class CreateBookingView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create booking for an event",
        tags=["Bookings"]
    )

    def perform_create(self, serializer):
        vendor_id = self.request.data.get("vendor_id")
        service_id = self.request.data.get("service_id")
        event_date = self.request.data.get("event_date")

        vendor = get_object_or_404(VendorProfile, id=vendor_id)

        if VendorAvailability.objects.filter(vendor=vendor, date=event_date).exists():
            raise ValueError("Vendor is unavailable for this date")

        serializer.save(
            customer=self.request.user,
            vendor=vendor,
            service_id=service_id
        )


class VendorBookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    @swagger_auto_schema(
        operation_description="List bookings for vendor",
        tags=["Bookings"]
    )

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Booking.objects.none()

        user = self.request.user
        if not hasattr(user, "vendor_profile"):
            return Booking.objects.none()

        return Booking.objects.filter(vendor=user.vendor_profile).order_by("-created_at")


class CustomerBookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List bookings for customer",
        tags=["Bookings"]
    )

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Booking.objects.none()

        user = self.request.user
        if user.is_anonymous:
            return Booking.objects.none()

        return Booking.objects.filter(customer=user).order_by("-created_at")


class AcceptBookingView(generics.UpdateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    @swagger_auto_schema(
        operation_description="Vendor accepts booking",
        tags=["Bookings"]
    )

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Booking.objects.none()

        user = self.request.user
        if not hasattr(user, "vendor_profile"):
            return Booking.objects.none()

        return Booking.objects.filter(vendor=user.vendor_profile)

    def perform_update(self, serializer):
        serializer.save(status="accepted")



class RejectBookingView(generics.UpdateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    @swagger_auto_schema(
        operation_description="Vendor rejects booking",
        tags=["Bookings"]
    )

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Booking.objects.none()

        user = self.request.user
        if not hasattr(user, "vendor_profile"):
            return Booking.objects.none()

        return Booking.objects.filter(vendor=user.vendor_profile)

    def perform_update(self, serializer):
        serializer.save(status="rejected")
