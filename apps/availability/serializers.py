from rest_framework import serializers
from apps.availability.models import VendorAvailability


class VendorAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorAvailability
        fields = ["id", "date"]
        read_only_fields = ["id"]