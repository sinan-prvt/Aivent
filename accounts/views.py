from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import (
    RegisterSerializer,
    VendorRegisterSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer,
    VendorProfileSerializer,
    VendorProfileUpdateSerializer,
    VendorServiceSerializer,
    VendorAvailabilitySerializer,
    BookingSerializer,
    EventSerializer,
    CategorySerializer,
    SubCategorySerializer,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .utils import create_otp_for_user, verify_otp_entry
from rest_framework_simplejwt.views import TokenObtainPairView
from .authentication import CustomLoginSerializer
from .permissions import IsAdmin
from .permissions import IsVendor
from .models import OTP, VendorProfile, Booking, Event, Category, SubCategory


























