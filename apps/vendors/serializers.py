from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.vendors.models import VendorProfile

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

        # Create user
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            role="vendor",
        )
        user.set_password(validated_data["password"])
        user.save()

        # Create vendor
        vendor = VendorProfile.objects.create(
            user=user,
            category_id=validated_data["category_id"],
            business_name=validated_data["business_name"],
            phone=validated_data["phone"],
            address=validated_data["address"]
        )

        # Add subcategories
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
