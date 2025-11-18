from django.urls import path
from apps.events.views import (
    EventListView,
    EventCreateView,
    EventUpdateView,
    EventDeleteView,
)

urlpatterns = [
    path("", EventListView.as_view()),
    path("create/", EventCreateView.as_view()),
    path("<int:pk>/update/", EventUpdateView.as_view()),
    path("<int:pk>/delete/", EventDeleteView.as_view()),
]
