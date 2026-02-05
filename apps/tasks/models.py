from django.db import models
from django.conf import settings
from django.utils import timezone


class Task(models.Model):
    TASK_TYPE_CHOICES = (
        ("fixed", "固定"),
        ("random", "ランダム"),
        ("weekly", "週1重い運動"),
    )

    title = models.CharField(max_length=100)
    task_type = models.CharField(max_length=10, choices=TASK_TYPE_CHOICES)
    is_completed = models.BooleanField(default=False)
    target_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)


    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    message = models.CharField(max_length=200)

    target_date = models.DateField()

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
