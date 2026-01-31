from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    google_fit_credentials = models.JSONField(
        blank=True, 
        null=True,
        help_text="GoogleFitの認証情報の保存用")
    
    weekly_heavy_goal = models.ForeignKey(
        'tasks.Task', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'category': 'heavy'},
        related_name='users_with_this_goal'
    )
    
    daily_step_goal = models.PositiveIntegerField(default=10000)  # 1日の歩数目標

    def __str__(self):
        return f"{self.user.username} Profile"
    
class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    notifications_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"Settings for {self.user.username}"