from django.db import models
from django.contrib.auth.models import AbstractUser
from fernet_fields import EncryptedTextField 

# Create your models here.

class User(AbstractUser):
    pass

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    google_fit_credentials = EncryptedTextField(
        blank=True, 
        null=True,
        help_text="GoogleFitの認証情報(暗号化済み)")
    
    weekly_heavy_goal = models.ForeignKey(
        'tasks.Task', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'category': 'heavy'},
        related_name='users_with_this_goal'
    )
    
    daily_step_goal = models.IntegerField(default=10000)  # 1日の歩数目標

    def __str__(self):
        return f"{self.user.username} Profile"
    
class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    notifications_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"Settings for {self.user.username}"