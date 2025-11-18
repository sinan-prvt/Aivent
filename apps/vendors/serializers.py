from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.vendors.models import VendorProfile
from .serializers import CategorySerializer, SubCategorySerializer


User = get_user_model()


class VendorRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    business_name = serializers.CharField()
    category_id = serializers.IntegerField()
    subcategory_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    phone = serializers.CharField()
    address = serializers.CharField()

    def create(self, validated_data):

        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            role="vendor"
        )
        user.set_password(validated_data["password"])
        user.save()

        category_id = validated_data["category_id"]
        subcategories = validated_data.get("subcategory_ids", [])

        vendor = VendorProfile.objects.create(
            user=user,
            category_id=category_id,
            business_name=validated_data["business_name"],
            phone=validated_data["phone"],
            address=validated_data["address"]
        )

        if subcategories:
            vendor.subcategories.set(subcategories)

        return vendor

    
class VendorProfileSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    subcategories = SubCategorySerializer(many=True)

    class Meta:
        model = VendorProfile
        fields = [
            "business_name",
            "category",
            "subcategories",
            "phone",
            "address",
            "gst_number",
            "status",
        ]


class VendorProfileUpdateSerializer(serializers.ModelSerializer):
    subcategory_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )

    class Meta:
        model = VendorProfile
        fields = [
            "business_name",
            "category",
            "subcategory_ids",
            "phone",
            "address",
            "gst_number",
        ]

    def update(self, instance, validated_data):
        sub_ids = validated_data.pop("subcategory_ids", None)

        vendor = super().update(instance, validated_data)

        if sub_ids is not None:
            vendor.subcategories.set(sub_ids)

        vendor.save()
        return vendor