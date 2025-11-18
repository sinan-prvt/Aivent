from django.urls import path
from apps.vendors.views import (
    VendorRegisterView,
    VendorProfileView,
    VendorProfileUpdateView,
    VendorListView,
    PendingVendorsView,
    ApproveVendorView,
    RejectVendorView,
    SuspendVendorView,
)

urlpattern = [    
    path("vendor/register/", VendorRegisterView.as_view(), name="vendor-register"),
    path("vendor/profile/", VendorProfileView.as_view(), name="vendor-profile"),
    path("vendor/profile/update/", VendorProfileUpdateView.as_view(), name="vendor-profile-update"),

    path("admin/vendors/", VendorListView.as_view()),
    path("admin/vendors/pending/", PendingVendorsView.as_view()),
    path("admin/vendors/<int:vendor_id>/approve/", ApproveVendorView.as_view()),
    path("admin/vendors/<int:vendor_id>/reject/", RejectVendorView.as_view()),
    path("admin/vendors/<int:vendor_id>/suspend/", SuspendVendorView.as_view()),
]