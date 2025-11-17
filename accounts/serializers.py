from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import VendorProfile, VendorService, VendorAvailability, Booking, Event
from .serializers import CategorySerializer, SubCategorySerializer


User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(choices=['email_verify','reset_password'], default='email_verify')

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(choices=['email_verify','reset_password'])
    otp = serializers.CharField(max_length=10)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(min_length=8)

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


class VendorServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorService
        fields = ["id", "title", "price", "description", "created_at"]

class VendorAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorAvailability
        fields = ["id", "date"]

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
        read_only_fields = ["customer", "status", "vendor", "created_at"]

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "event_type",
            "date",
            "location",
            "budget",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
