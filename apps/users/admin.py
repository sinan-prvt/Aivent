from django.contrib import admin
from apps.users.models import User, OTP, MFASession

admin.site.register(User)
admin.site.register(OTP)
admin.site.register(MFASession)
