from rest_framework import serializers
from apps.services.models import VendorService


class VendorServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorService
        fields = ["id", "title", "price", "description", "created_at"]