from rest_framework import serializers
from .models import User, UserProfile, UserSettings

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('daily_step_goal', 'weekly_heavy_goal', 'google_fit_credentials')

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ('notifications_enabled',)

class CustomUserDetailsSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    settings = UserSettingsSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile', 'settings')

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        return user