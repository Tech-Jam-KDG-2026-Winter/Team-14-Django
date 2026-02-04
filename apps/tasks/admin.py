from django.contrib import admin

# Register your models here.
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_fixed')
    list_filter = ('category', 'is_fixed')