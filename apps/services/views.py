from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.services.models import VendorService
from apps.services.serializers import (
    VendorServiceSerializer,
    VendorServiceCreateUpdateSerializer,
)
from apps.vendors.permissions import IsVendor
from drf_yasg.utils import swagger_auto_schema


class VendorServiceCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsVendor]
    serializer_class = VendorServiceCreateUpdateSerializer

    @swagger_auto_schema(
        operation_description="Create a vendor service with nested addons/packages/images",
        request_body=VendorServiceCreateUpdateSerializer,
        tags=["Services"]
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.data

        if request.FILES:
            files = request.FILES.getlist("images")
            data = data.copy()
            data.setlist("images", [{"image": f} for f in files])

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        service = serializer.save()

        return Response({
            "success": True,
            "data": VendorServiceSerializer(service, context={"request": request}).data
        }, status=status.HTTP_201_CREATED)


class VendorServiceListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsVendor]
    serializer_class = VendorServiceSerializer

    @swagger_auto_schema(
        operation_description="List all services of logged-in vendor",
        tags=["Services"]
    )
    def get_queryset(self):
        return self.request.user.vendor_profile.services.all()


class VendorServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsVendor]
    lookup_field = "pk"

    def get_queryset(self):
        return VendorService.objects.filter(vendor=self.request.user.vendor_profile)

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return VendorServiceCreateUpdateSerializer
        return VendorServiceSerializer

    @swagger_auto_schema(tags=["Services"])
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    @swagger_auto_schema(tags=["Services"])
    def put(self, *args, **kwargs):
        return super().put(*args, **kwargs)

    @swagger_auto_schema(tags=["Services"])
    def patch(self, *args, **kwargs):
        return super().patch(*args, **kwargs)

    @swagger_auto_schema(tags=["Services"])
    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)
