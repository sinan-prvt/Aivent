from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import VendorProfile

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
    category = serializers.CharField()
    phone = serializers.CharField()
    address = serializers.CharField()

    def create(self, validated_data):

        user_data = {
            "username": validated_data["username"],
            "email": validated_data["email"],
            "role": "vendor"
        }
        password = validated_data["password"]

        user = User.objects.create(**user_data)
        user.set_password(password)
        user.save()

        VendorProfile.objects.create(
            user=user,
            business_name=validated_data["business_name"],
            category=validated_data["category"],
            phone=validated_data["phone"],
            address=validated_data["address"],
        )

        return user