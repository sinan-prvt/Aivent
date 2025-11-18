from rest_framework import serializers
from apps.events.models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "event_type",
            "date",
            "location",
            "budget",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
