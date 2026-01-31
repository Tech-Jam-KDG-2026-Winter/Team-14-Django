from django.contrib import admin

# Register your models here.
from .models import Task

# 管理画面に Task モデルを表示させるための登録
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_fixed')  # 一覧に表示する項目
    list_filter = ('category', 'is_fixed')