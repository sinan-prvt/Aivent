from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class Event(models.Model):
    EVENT_TYPES = [
        ("wedding", "Wedding"),
        ("birthday", "Birthday"),
        ("engagement", "Engagement"),
        ("corporate", "Corporate Event"),
        ("concert", "Concert"),
        ("festival", "Festival"),
        ("baby_shower", "Baby Shower"),
        ("private_party", "Private Party"),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")

    name = models.CharField(max_length=255)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    date = models.DateField()
    location = models.CharField(max_length=500, blank=True, null=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.event_type})"