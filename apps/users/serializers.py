from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from apps.users.models import OTP
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            role="customer",
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class CustomLoginSerializer(TokenObtainPairSerializer):
    username_field = "email"

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password")

        if not user.email_verified:
            raise serializers.ValidationError("Please verify email before login.")

        attrs["username"] = email

        data = super().validate(attrs)

        dashboard_map = {
            "customer": "/customer/home",
            "vendor": "/vendor/dashboard",
            "admin": "/admin/panel"
        }

        response = {
            "access": data["access"],
            "refresh": data["refresh"],
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
            },
            "dashboard": dashboard_map.get(user.role, "/")
        }

        if user.role == "vendor":
            response["status"] = user.vendor_profile.status

        return response





class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.CharField()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.CharField()
    otp = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(min_length=8)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)