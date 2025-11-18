from rest_framework import serializers
from apps.bookings.models import Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "customer",
            "vendor",
            "service",
            "event_date",
            "message",
            "status",
            "created_at"
        ]
        read_only_fields = ["customer", "vendor", "status", "created_at"]
