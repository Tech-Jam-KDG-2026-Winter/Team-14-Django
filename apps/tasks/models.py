from django.db import models

# Create your models here.
class Task(models.Model):
    CATEGORY_CHOICES = [
        ('exercise', '運動'),
        ('habit', '生活習慣'),
        ('heavy', '重め'),
    ]

    title = models.CharField(max_length=100)
    is_fixed = models.BooleanField(default=False)  # 固定タスクかどうか
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"