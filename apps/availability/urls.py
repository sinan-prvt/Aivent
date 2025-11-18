from django.urls import path
from apps.availability.views import (
    VendorAvailabilityListView,
    VendorAvailabilityCreateView,
    VendorAvailabilityDeleteView,
)


urlpatterns = [
    path("vendor/availability/", VendorAvailabilityListView.as_view(), name="vendor-availability"),
    path("vendor/availability/add/", VendorAvailabilityCreateView.as_view(), name="vendor-availability-add"),
    path("vendor/availability/<int:pk>/delete/", VendorAvailabilityDeleteView.as_view(), name="vendor-availability-delete"),
]