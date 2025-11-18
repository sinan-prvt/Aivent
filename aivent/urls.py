from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/auth/', include('apps.users.urls')),
    path('api/vendors/', include('apps.vendors.urls')),
    path('api/events/', include('apps.events.urls')),
    path('api/services/', include('apps.services.urls')),
    path('api/availability/', include('apps.availability.urls')),
    path('api/bookings/', include('apps.bookings.urls')),
    path('api/categories/', include('apps.categories.urls')),
]
