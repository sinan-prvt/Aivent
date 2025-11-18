from django.urls import path
from apps.services.views import (
    VendorServiceCreateView,
    VendorServiceListView,
    VendorServiceUpdateView,
    VendorServiceDeleteView,
)


urlpatterns = [
    path("vendor/services/", VendorServiceListView.as_view(), name="vendor-services"),
    path("vendor/services/create/", VendorServiceCreateView.as_view(), name="vendor-service-create"),
    path("vendor/services/<int:pk>/update/", VendorServiceUpdateView.as_view(), name="vendor-service-update"),
    path("vendor/services/<int:pk>/delete/", VendorServiceDeleteView.as_view(), name="vendor-service-delete"),
]