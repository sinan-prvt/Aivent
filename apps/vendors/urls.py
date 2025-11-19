from django.urls import path
from apps.vendors.views import (
    VendorRegisterView,
    VendorProfileView,
    VendorProfileUpdateView,
    PendingVendorsView,
    ApproveVendorView,
    RejectVendorView,
    SuspendVendorView,
    VendorResendOTPView,    
)

urlpatterns = [
    path("register/", VendorRegisterView.as_view()),
    path("resend-otp/", VendorResendOTPView.as_view()),

    path("profile/", VendorProfileView.as_view()),
    path("profile/update/", VendorProfileUpdateView.as_view()),

    path("admin/pending/", PendingVendorsView.as_view()),
    path("admin/<int:vendor_id>/approve/", ApproveVendorView.as_view()),
    path("admin/<int:vendor_id>/reject/", RejectVendorView.as_view()),
    path("admin/<int:vendor_id>/suspend/", SuspendVendorView.as_view()),
]
