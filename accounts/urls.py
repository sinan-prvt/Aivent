from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    VendorRegisterView,
    CustomLoginView,
    VendorListView,
    PendingVendorsView,
    ApproveVendorView,
    RejectVendorView,
    SuspendVendorView,
    CustomLoginView,
    VendorProfileView,
    VendorProfileUpdateView,
    VendorServiceListView,
    VendorServiceCreateView,
    VendorServiceUpdateView,
    VendorServiceDeleteView,
    VendorAvailabilityListView,
    VendorAvailabilityCreateView,
    VendorAvailabilityDeleteView,
    CreateBookingView,
    CustomerBookingListView,
    VendorBookingListView,
    AcceptBookingView,
    RejectBookingView,
    EventListView,
    EventCreateView,
    EventUpdateView,
    EventDeleteView,
    CategoryListView,
    CategoryCreateView,
    SubCategoryListView,
    SubCategoryCreateView,
)

urlpatterns = [
    

    path("login/", CustomLoginView.as_view(), name="jwt-login"),
    path("refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),


    path("send-reset-otp/", views.SendResetOTPView.as_view(), name="auth-send-reset-otp"),
    path("reset-password/", views.ResetPasswordView.as_view(), name="auth-reset-password"),












]   
