from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.conf.urls.static import static


schema_view = get_schema_view(
    openapi.Info(
        title = "AIVENT API",
        default_version = "v1",
        description = "API documentation for AIVENT",
        terms_of_services = "https://www.google.com/policies/terms/",
        contact = openapi.Contact(email="aiventhelp@gmail.com"),
        license = openapi.License(name="MIT License"),
    ),
    public = True,
    permission_classes = (AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),

    path("api/auth/", include("apps.users.urls")),
    path("api/vendors/", include("apps.vendors.urls")),
    path("api/categories/", include("apps.categories.urls")),
    path("api/services/", include("apps.services.urls")),
    path("api/availability/", include("apps.availability.urls")),
    path("api/bookings/", include("apps.bookings.urls")),
    path("api/events/", include("apps.events.urls")),

    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc-ui'),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='swagger-schema'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
