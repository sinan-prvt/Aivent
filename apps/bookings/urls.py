from django.urls import path
from apps.bookings.views import (
    CreateBookingView,
    CustomerBookingListView,
    VendorBookingListView,
    AcceptBookingView,
    RejectBookingView,
)

urlpatterns = [
    path("bookings/create/", CreateBookingView.as_view(), name="booking-create"),
    path("bookings/customer/", CustomerBookingListView.as_view(), name="customer-bookings"),

    path("bookings/vendor/", VendorBookingListView.as_view(), name="vendor-bookings"),
    path("bookings/<int:pk>/accept/", AcceptBookingView.as_view(), name="booking-accept"),
    path("bookings/<int:pk>/reject/", RejectBookingView.as_view(), name="booking-reject"),

]