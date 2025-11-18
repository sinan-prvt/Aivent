from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone

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

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} ({self.role})"



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
