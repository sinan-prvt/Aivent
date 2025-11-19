from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone
import pyotp
from datetime import timedelta

class User(AbstractUser):
    ROLE_CHOICES = [
        ("customer", "Customer"),
        ("vendor", "Vendor"),
        ("admin", "Admin"),
    ]

    username = models.CharField(max_length=150, unique=False, blank=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")
    email_verified = models.BooleanField(default=False)

    totp_secret = models.CharField(max_length=64, blank=True, null=True)
    mfa_enabled = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def get_totp_uri(self):
        if not self.totp_secret:
            return None
        return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(
            name=self.email, issuer_name="AIVENT"
        )
    

    def __str__(self):
        return f"{self.email} ({self.role})"


class MFASession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mfa_sessions")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() >= self.expires_at

    @classmethod
    def create_for_user(cls, user, valid_seconds=180):
        expires = timezone.now() + timedelta(seconds=valid_seconds)
        return cls.objects.create(user=user, expires_at=expires)


class OTP(models.Model):
    PURPOSE_CHOICE = [
        ('email_verify', 'Email Verification'),
        ('reset_password', 'Password Reset'),
        ('mfa', 'MFA'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp_hash = models.CharField(max_length=128)
    salt = models.CharField(max_length=64)
    purpose = models.CharField(max_length=32, choices=PURPOSE_CHOICE)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() >= self.expires_at
