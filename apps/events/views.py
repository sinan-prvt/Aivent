from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from apps.events.serializers import EventSerializer
from apps.events.models import Event
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class EventCreateView(generics.CreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create event",
        tags=["Events"]
    )

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class EventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all events of customer",
        tags=["Events"]
    )

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Event.objects.none()

        user = self.request.user
        if user.is_anonymous:
            return Event.objects.none()

        return Event.objects.filter(customer=user).order_by("-created_at")



class EventUpdateView(generics.UpdateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update event",
        tags=["Events"]
    )

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Event.objects.none()

        user = self.request.user
        if user.is_anonymous:
            return Event.objects.none()

        return Event.objects.filter(customer=user)


class EventDeleteView(generics.DestroyAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Delete event",
        tags=["Events"]
    )

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Event.objects.none()

        user = self.request.user
        if user.is_anonymous:
            return Event.objects.none()

        return Event.objects.filter(customer=user)