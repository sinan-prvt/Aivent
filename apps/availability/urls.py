from django.urls import path
from apps.availability.views import (
    VendorAvailabilityListView,
    VendorAvailabilityCreateView,
    VendorAvailabilityDeleteView,
)

urlpatterns = [
    path("", VendorAvailabilityListView.as_view(), name="vendor-availability"),
    path("add/", VendorAvailabilityCreateView.as_view(), name="vendor-availability-add"),
    path("<int:pk>/delete/", VendorAvailabilityDeleteView.as_view(), name="vendor-availability-delete"),
]
