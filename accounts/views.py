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

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        data = {
            "id": str(user.id),
            "email": user.email,
            "message": "User registered successfully. Verify email (if implemented)."
        }

        return Response(data, status=status.HTTP_201_CREATED)


class SendOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SendOTPSerializer

    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)

        email = s.validated_data['email']
        purpose = s.validated_data['purpose']

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "User with this email not found."}, status=status.HTTP_404_NOT_FOUND)

        raw_otp, otp_obj = create_otp_for_user(user, purpose=purpose)

        print("DEBUG OTP =", raw_otp)

        subject = "Your AIVENT OTP code"
        message = f"Your OTP is {raw_otp} (expires in 10 minutes)."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)

        return Response({"detail": "OTP sent to email."}, status=status.HTTP_200_OK)


class VerifyOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        email = s.validated_data['email']
        purpose = s.validated_data['purpose']
        otp_value = s.validated_data['otp']

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        now = timezone.now()

        otp_qs = OTP.objects.filter(
            user=user,
            purpose=purpose,
            used=False,
            expires_at__gt=now
        ).order_by('-created_at')

        if not otp_qs.exists():
            return Response({"detail": "No valid OTP found or expired."}, status=status.HTTP_400_BAD_REQUEST)

        otp_obj = otp_qs.first()
        if verify_otp_entry(otp_obj, otp_value):
            otp_obj.used = True
            otp_obj.save()

            if purpose == 'email_verify':
                pass

            return Response({"detail": "OTP verified."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)


class SendResetOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SendOTPSerializer

    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)

        email = s.validated_data['email']
        user = User.objects.filter(email=email).first()

        if not user:
            return Response({"detail": "No user found with this email."}, status=404)

        raw_otp, otp_obj = create_otp_for_user(user, purpose="reset_password")

        print("RESET PASSWORD OTP =", raw_otp)

        send_mail(
            "AIVENT Password Reset OTP",
            f"Your OTP is {raw_otp}. It expires in 10 minutes.",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False
        )

        return Response({"detail": "Password reset OTP sent."}, status=200)


class ResetPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)

        email = s.validated_data["email"]
        new_password = s.validated_data["new_password"]

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "User not found."}, status=404)

        otp_obj = OTP.objects.filter(
            user=user,
            purpose="reset_password",
            used=True,
        ).order_by("-created_at").first()

        if not otp_obj:
            return Response({"detail": "OTP not verified yet."}, status=400)

        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password reset successfully."}, status=200)


class CategoryCreateView(generics.CreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [AllowAny]

class SubCategoryCreateView(generics.CreateAPIView):
    serializer_class = SubCategorySerializer
    permission_classes = [IsAuthenticated, IsAdmin]

class SubCategoryListView(generics.ListAPIView):
    serializer_class = SubCategorySerializer

    def get_queryset(self):
        category_id = self.kwargs["category_id"]
        return SubCategory.objects.filter(category_id=category_id)




class VendorRegisterView(generics.CreateAPIView):
    serializer_class = VendorProfileSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "Vendor registered successfully. Awaiting admin verification.",
            "vendor_id": vendor.id
        }, status=status.HTTP_201_CREATED)

# class CustomLoginView(TokenObtainPairView):
#     serializer_class = CustomLoginSerializer

class VendorListView(generics.ListAPIView):
    queryset = VendorProfile.objects.all()
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class PendingVendorsView(generics.ListAPIView):
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return VendorProfile.objects.filter(status="pending")

class ApproveVendorView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, vendor_id):
        vendor = get_object_or_404(VendorProfile, user__id=vendor_id)
        vendor.status = "approved"
        vendor.save()
        return Response({"message": "Vendor approved"}, status=status.HTTP_200_OK)

class RejectVendorView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, vendor_id):
        vendor = get_object_or_404(VendorProfile, user__id=vendor_id)
        vendor.status = "rejected"
        vendor.save()
        return Response({"message": "Vendor rejected"}, status=status.HTTP_200_OK)

class SuspendVendorView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, vendor_id):
        vendor = get_object_or_404(VendorProfile, user__id=vendor_id)
        vendor.status = "suspended"
        vendor.save()
        return Response({"message": "Vendor suspended"}, status=status.HTTP_200_OK)

class VendorProfileView(generics.RetrieveAPIView):
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_object(self):
        return self.request.user.vendor_profile
    

class VendorProfileUpdateView(generics.UpdateAPIView):
    serializer_class = VendorProfileUpdateSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_object(self):
        return self.request.user.vendor_profile

class VendorServiceCreateView(generics.CreateAPIView):
    serializer_class = VendorServiceSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def perform_create(self, serializer):
        vendor_profile = self.request.user.vendor_profile
        serializer.save(vendor=vendor_profile)

class VendorServiceListView(generics.ListAPIView):
    serializer_class = VendorServiceSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        return self.request.user.vendor_profile.services.all()


class VendorServiceUpdateView(generics.UpdateAPIView):
    serializer_class = VendorServiceSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        return self.request.user.vendor_profile.services.all()


class VendorServiceDeleteView(generics.DestroyAPIView):
    serializer_class = VendorServiceSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        return self.request.user.vendor_profile.services.all()

class VendorAvailabilityCreateView(generics.CreateAPIView):
    serializer_class = VendorAvailabilitySerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def perform_create(self, serializer):
        vendor = self.request.user.vendor_profile
        serializer.save(vendor=vendor)

class VendorAvailabilityListView(generics.ListAPIView):
    serializer_class = VendorAvailabilitySerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        vendor = self.request.user.vendor_profile
        return vendor.availability.all().order_by("date")

class VendorAvailabilityDeleteView(generics.DestroyAPIView):
    serializer_class = VendorAvailabilitySerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        vendor = self.request.user.vendor_profile
        return vendor.availability.all()


class CreateBookingView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        vendor_id = self.request.data.get("vendor_id")
        service_id = self.request.data.get("service_id")

        vendor_profile = get_object_or_404(VendorProfile, id=vendor_id)

        serializer.save(
            customer=self.request.user,
            vendor=vendor_profile,
            service_id=service_id
        )


class VendorBookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        vendor = self.request.user.vendor_profile
        return Booking.objects.filter(vendor=vendor).order_by("-created_at")


class AcceptBookingView(generics.UpdateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        return Booking.objects.filter(vendor=self.request.user.vendor_profile)

    def perform_update(self, serializer):
        serializer.save(status="accepted")


class RejectBookingView(generics.UpdateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def get_queryset(self):
        return Booking.objects.filter(vendor=self.request.user.vendor_profile)

    def perform_update(self, serializer):
        serializer.save(status="rejected")


class CustomerBookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(customer=self.request.user).order_by("-created_at")

class EventCreateView(generics.CreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

class EventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(customer=self.request.user).order_by("-created_at")


class EventUpdateView(generics.UpdateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(customer=self.request.user)

class EventDeleteView(generics.DestroyAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(customer=self.request.user)

