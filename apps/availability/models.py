from django.db import models
from apps.vendors.models import VendorProfile


class VendorAvailability(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name="availability")
    date = models.DateField()

    class Meta:
        unique_together = ("vendor", "date")

    def __str__(self):
        return f"{self.vendor.business_name} unavailable on {self.date}"