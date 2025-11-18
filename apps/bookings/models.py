from django.db import models
from django.conf import settings
from apps.vendors.models import VendorProfile
from apps.services.models import VendorService


User = settings.AUTH_USER_MODEL


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_bookings")
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name="vendor_bookings")
    service = models.ForeignKey("VendorService", on_delete=models.SET_NULL, null=True, blank=True)

    event_date = models.DateField()
    message = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username} → {self.vendor.business_name} on {self.event_date}"