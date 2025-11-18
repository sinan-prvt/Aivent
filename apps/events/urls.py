from django.urls import path
from apps.events.views import (
    EventListView,
    EventCreateView,
    EventUpdateView,
    EventDeleteView,
)

urlpatterns = [
    path("events/", EventListView.as_view(), name="event-list"),
    path("events/create/", EventCreateView.as_view(), name="event-create"),
    path("events/<int:pk>/update/", EventUpdateView.as_view(), name="event-update"),
    path("events/<int:pk>/delete/", EventDeleteView.as_view(), name="event-delete"),
]