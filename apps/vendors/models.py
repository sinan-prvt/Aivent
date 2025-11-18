from django.db import models
from django.conf import settings
from apps.categories.models import Category, SubCategory
from django.contrib.auth import get_user_model


User = get_user_model()

class VendorProfile(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("suspended", "Suspended"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="vendor_profile")

    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    subcategories = models.ManyToManyField(SubCategory, blank=True)

    business_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=500)
    gst_number = models.CharField(max_length=30, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.business_name


class VendorService(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name="services")
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.vendor.business_name}"

class VendorAvailability(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name="availability")
    date = models.DateField()

    class Meta:
        unique_together = ("vendor", "date")

    def __str__(self):
        return f"{self.vendor.business_name} unavailable on {self.date}"
