from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, UserSettings

admin.site.register(User, UserAdmin)
admin.site.register(UserProfile)
admin.site.register(UserSettings)