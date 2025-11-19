from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.vendors.models import VendorProfile
from django.db import transaction


User = get_user_model()



class VendorRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    business_name = serializers.CharField()
    category_id = serializers.IntegerField()
    subcategory_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    phone = serializers.CharField()
    address = serializers.CharField()

    def create(self, validated_data):
        with transaction.atomic():
            user = User(
                username=validated_data["username"],
                email=validated_data["email"],
                role="vendor",
                email_verified=False,
            )
            user.set_password(validated_data["password"])
            user.save()

            vendor = VendorProfile.objects.create(
                user=user,
                category_id=validated_data["category_id"],
                business_name=validated_data["business_name"],
                phone=validated_data["phone"],
                address=validated_data["address"]
            )

            subs = validated_data.get("subcategory_ids", [])
            if subs:
                vendor.subcategories.set(subs)

        return vendor


class VendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = [
            "business_name",
            "category",
            "phone",
            "address",
            "gst_number",
            "status"
        ]
        read_only_fields = ["status"]


class VendorProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = [
            "business_name",
            "category",
            "phone",
            "address",
            "gst_number",
        ]


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
