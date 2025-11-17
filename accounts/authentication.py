from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

class CustomLoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        if user.role == "vendor":
            profile = getattr(user, "vendor_profile", None)
            if profile.status != "approved":
                raise serializers.ValidationError(
                    {"detail": f"Vendor not approved. Current status: {profile.status}"}
                )

        return data
