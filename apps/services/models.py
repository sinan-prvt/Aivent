from django.db import models
from apps.vendors.models import VendorProfile



class VendorService(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

