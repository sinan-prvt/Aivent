from django.db import models
from apps.vendors.models import VendorProfile



class VendorAvailability(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name="availability")
    date = models.DateField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.vendor.business_name} - {self.date}"
