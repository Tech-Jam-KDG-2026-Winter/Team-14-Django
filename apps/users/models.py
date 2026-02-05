from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models
from django.utils import timezone
from apps.common.fields import EncryptedJSONField
import uuid

class UserManager(DjangoUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class User(AbstractUser):
    deleted_at = models.DateTimeField(null=True, blank=True)
    original_email = models.EmailField(blank=True)
    original_username = models.CharField(max_length=150, blank=True)
    
    objects = UserManager()
    all_objects = models.Manager()
    
    def soft_delete(self):
        if self.deleted_at:
            return
            
        self.deleted_at = timezone.now()
        self.is_active = False
        
        self.original_email = self.email
        self.original_username = self.username
        
        unique_suffix = f"_del_{uuid.uuid4().hex[:8]}"
        self.email = f"{self.email}{unique_suffix}"
        self.username = f"{self.username}{unique_suffix}"
        
        self.save()
        
        # 関連データも論理削除
        if hasattr(self, 'profile'):
            self.profile.deleted_at = self.deleted_at
            self.profile.save()
        
        if hasattr(self, 'settings'):
            self.settings.deleted_at = self.deleted_at
            self.settings.save()

class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile'
    )
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    google_fit_credentials = EncryptedJSONField(
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
    
    daily_step_goal = models.IntegerField(default=10000)

    # 念の為
    def save(self, *args, **kwargs):
        if self.google_fit_credentials and isinstance(self.google_fit_credentials, dict):
            if 'access_token' in self.google_fit_credentials:
                self.google_fit_credentials['token'] = self.google_fit_credentials.pop('access_token')

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} Profile"
    
class UserSettings(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='settings'
    )
    deleted_at = models.DateTimeField(null=True, blank=True)
    notifications_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"Settings for {self.user.username}"