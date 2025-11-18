from django.urls import path
from apps.services.views import (
    VendorServiceCreateView,
    VendorServiceListView,
    VendorServiceUpdateView,
    VendorServiceDeleteView,
)

urlpatterns = [
    path("", VendorServiceListView.as_view(), name="vendor-services"),
    path("create/", VendorServiceCreateView.as_view(), name="vendor-service-create"),
    path("<int:pk>/update/", VendorServiceUpdateView.as_view(), name="vendor-service-update"),
    path("<int:pk>/delete/", VendorServiceDeleteView.as_view(), name="vendor-service-delete"),
]
