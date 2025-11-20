from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from apps.users.models import OTP
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.core.recaptcha import verify_recaptcha
from apps.core.captcha_utils import increment_failed_attempts, reset_failed_attempts, requires_captcha

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    recaptcha_token = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "recaptcha_token"]
        
    def validate(self, attrs):
        request = self.context.get('request')
        ip = request.META.get('REMOTE_ADDR') if request else None
        key = ip or attrs.get('email') or 'anon'

        if requires_captcha(key):
            token = attrs.get("recaptcha_token") or (request.data.get("recaptcha_token") if request else None)
            if not token:
                raise serializers.ValidationError({"recaptcha_token": ["reCAPTCHA required"]})
            resp = verify_recaptcha(token, remoteip=ip)
            if not resp.get("success") or (resp.get("score") or 0.0) < float(getattr(settings, "RECAPTCHA_MIN_SCORE", 0.5)):
                increment_failed_attempts(key)
                raise serializers.ValidationError({"recaptcha_token": ["reCAPTCHA validation failed"]})

        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop("recaptcha_token", None)
        user = super().create(validated_data)
        request = self.context.get('request')
        ip = request.META.get('REMOTE_ADDR') if request else None
        key = ip or user.email
        reset_failed_attempts(key)
        return user


class CustomLoginSerializer(TokenObtainPairSerializer):
    username_field = "email"

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError({
                "auth": ["Invalid email or password"]
            })

        if user.role != "admin" and not user.email_verified:
            raise serializers.ValidationError({
                "email": ["Please verify email first."]
            })
        
        self._validated_user = user

        if user.role == "vendor" and user.mfa_enabled:
            return {
                "mfa_required": True,
                "email": user.email
            }

        attrs["username"] = email
        data = super().validate(attrs)

        data["user"] = {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        }

        return data


class EnableMfaSerializer(serializers.Serializer):
    pass

class ConfirmEnableMfaSerializer(serializers.Serializer):
    secret = serializers.CharField()
    code = serializers.CharField()

class VerifyMFASerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    code = serializers.CharField()



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