from django.db import models
import uuid
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser

User = settings.AUTH_USER_MODEL


class User(AbstractUser):
    ROLE_CHOICES = [
        ("customer", "Customer"),
        ("vendor", "Vendor"),
        ("admin", "Admin"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")

    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    
class VendorProfile(models.Model):
    CATEGORY_CHOICES = [
        ("catering", "Catering"),
        ("photography", "Photography"),
        ("decoration", "Decoration"),
        ("stage", "Stage"),
        ("lighting", "Lighting"),
        ("sound", "Sound"),
        ("venue", "Venue"),
        ("dj", "DJ"),
        ("mehendi", "Mehendi"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("suspended", "Suspended"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="vendor_profile")

    business_name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=500)
    gst_number = models.CharField(max_length=30, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.business_name} ({self.category})"
    

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

    class Meta:
        indexes = [
            models.Index(fields=['user', 'purpose']),
            models.Index(fields=['expires_at']),
        ]

    def is_expired(self):
        return timezone.now() >= self.expires_at