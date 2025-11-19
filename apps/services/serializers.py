from rest_framework import serializers
from apps.services.models import VendorService


class VendorServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorService
        fields = ["id", "name", "price"]
        read_only_fields = ["id", "created_at"]
