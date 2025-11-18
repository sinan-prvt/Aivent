from django.urls import path
from apps.bookings.views import (
    CreateBookingView,
    CustomerBookingListView,
    VendorBookingListView,
    AcceptBookingView,
    RejectBookingView,
)

urlpatterns = [
    path("create/", CreateBookingView.as_view()),
    path("customer/", CustomerBookingListView.as_view()),
    path("vendor/", VendorBookingListView.as_view()),

    path("<int:pk>/accept/", AcceptBookingView.as_view()),
    path("<int:pk>/reject/", RejectBookingView.as_view()),
]
