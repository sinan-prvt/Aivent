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
    path("register/", views.RegisterView.as_view(), name="auth-register"),

    path("vendor/register/", VendorRegisterView.as_view(), name="vendor-register"),
    path("login/", CustomLoginView.as_view(), name="jwt-login"),
    path("refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),

    path("send-otp/", views.SendOTPView.as_view(), name="auth-send-otp"),
    path("verify-otp/", views.VerifyOTPView.as_view(), name="auth-verify-otp"),
    path("send-reset-otp/", views.SendResetOTPView.as_view(), name="auth-send-reset-otp"),
    path("reset-password/", views.ResetPasswordView.as_view(), name="auth-reset-password"),

    path("admin/vendors/", VendorListView.as_view()),
    path("admin/vendors/pending/", PendingVendorsView.as_view()),
    path("admin/vendors/<int:vendor_id>/approve/", ApproveVendorView.as_view()),
    path("admin/vendors/<int:vendor_id>/reject/", RejectVendorView.as_view()),
    path("admin/vendors/<int:vendor_id>/suspend/", SuspendVendorView.as_view()),

    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("categories/create/", CategoryCreateView.as_view(), name="category-create"),

    path("categories/<int:category_id>/subcategories/", SubCategoryListView.as_view(), name="subcategory-list"),
    path("subcategories/create/", SubCategoryCreateView.as_view(), name="subcategory-create"),


    path("vendor/profile/", VendorProfileView.as_view(), name="vendor-profile"),
    path("vendor/profile/update/", VendorProfileUpdateView.as_view(), name="vendor-profile-update"),

    path("vendor/services/", VendorServiceListView.as_view(), name="vendor-services"),
    path("vendor/services/create/", VendorServiceCreateView.as_view(), name="vendor-service-create"),
    path("vendor/services/<int:pk>/update/", VendorServiceUpdateView.as_view(), name="vendor-service-update"),
    path("vendor/services/<int:pk>/delete/", VendorServiceDeleteView.as_view(), name="vendor-service-delete"),

    path("vendor/availability/", VendorAvailabilityListView.as_view(), name="vendor-availability"),
    path("vendor/availability/add/", VendorAvailabilityCreateView.as_view(), name="vendor-availability-add"),
    path("vendor/availability/<int:pk>/delete/", VendorAvailabilityDeleteView.as_view(), name="vendor-availability-delete"),


    path("bookings/create/", CreateBookingView.as_view(), name="booking-create"),
    path("bookings/customer/", CustomerBookingListView.as_view(), name="customer-bookings"),

    path("bookings/vendor/", VendorBookingListView.as_view(), name="vendor-bookings"),
    path("bookings/<int:pk>/accept/", AcceptBookingView.as_view(), name="booking-accept"),
    path("bookings/<int:pk>/reject/", RejectBookingView.as_view(), name="booking-reject"),

    path("events/", EventListView.as_view(), name="event-list"),
    path("events/create/", EventCreateView.as_view(), name="event-create"),
    path("events/<int:pk>/update/", EventUpdateView.as_view(), name="event-update"),
    path("events/<int:pk>/delete/", EventDeleteView.as_view(), name="event-delete"),
]   
