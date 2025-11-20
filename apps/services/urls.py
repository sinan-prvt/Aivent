from django.urls import path
from apps.services.views import (
    VendorServiceCreateView,
    VendorServiceListView,
    VendorServiceDetailView,
)

urlpatterns = [
    path("", VendorServiceListView.as_view(), name="vendor-services"),
    path("create/", VendorServiceCreateView.as_view(), name="vendor-service-create"),
    path("<int:pk>/", VendorServiceDetailView.as_view(), name="vendor-service-detail"),
]