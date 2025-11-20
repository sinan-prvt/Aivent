from django.contrib import admin
from apps.services.models import VendorService, ServiceAddon, ServicePackage, VendorServiceImage

admin.site.register(VendorService)
admin.site.register(ServiceAddon)
admin.site.register(ServicePackage)
admin.site.register(VendorServiceImage)
