from django.db import models
from apps.vendors.models import VendorProfile
from apps.categories.models import Category, SubCategory


class VendorService(models.Model):
    PRICING_TYPES = [
        ("fixed", "Fixed Price"),
        ("per_day", "Per Day"),
        ("per_hour", "Per Hour"),
        ("package", "Package Based"),
    ]

    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name="services")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    pricing_type = models.CharField(max_length=20, choices=PRICING_TYPES, default="fixed")

    
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    min_booking_hours = models.PositiveIntegerField(null=True, blank=True)
    max_booking_hours = models.PositiveIntegerField(null=True, blank=True)

    min_booking_days_before_event = models.PositiveIntegerField(default=0)
    max_booking_duration_days = models.PositiveIntegerField(default=365)

    is_active = models.BooleanField(default=True)

    rating = models.FloatField(default=0)
    total_bookings = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.vendor.business_name})"


class ServiceAddon(models.Model):
    service = models.ForeignKey(VendorService, on_delete=models.CASCADE, related_name="addons")
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.service.name} - {self.name}"
    

class ServicePackage(models.Model):
    service = models.ForeignKey(VendorService, on_delete=models.CASCADE, related_name="packages")
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.service.name} - {self.title}"


class VendorServiceImage(models.Model):
    service = models.ForeignKey(VendorService, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="services/")

    def __str__(self):
        return f"Image for {self.service.name}"
