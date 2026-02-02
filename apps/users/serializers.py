from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import EmailValidator
from django.db import IntegrityError, transaction
from rest_framework import serializers
from .models import User, UserProfile, UserSettings
import json
import re

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('daily_step_goal', 'weekly_heavy_goal')

    def validate_daily_step_goal(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("歩数目標は0以上である必要があります。")
        if value is not None and value > 100000:
            raise serializers.ValidationError("歩数目標が大きすぎます。")
        return value
    
class GoogleFitCredentialSerializer(serializers.Serializer):
    google_fit_credentials = serializers.JSONField(write_only=True)
    
    def validate_google_fit_credentials(self, value):
        if value is not None and not value:
            raise serializers.ValidationError(
                "Google Fitの認証情報が正しく取得できませんでした。"
            )
        
        required_keys = ['refresh_token', 'token_uri', 'client_id']
        
        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(
                    f"{key} が認証情報に含まれていません。"
                )

        return value
        
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
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')
    
    def validate_username(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("ユーザー名を入力してください。")
        
        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError("ユーザー名は3文字以上である必要があります。")
        
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError(
                "ユーザー名には特殊文字を使用できません。"
            )
        return value
    
    def validate_email(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("メールアドレスを入力してください。")
        
        value = value.strip().lower()

        email_validator = EmailValidator()
        try:
            email_validator(value)

        except DjangoValidationError:
            raise serializers.ValidationError("有効なメールアドレスを入力してください。")
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("このメールアドレスは既に登録されています。")
        return value
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                "password_confirm": "パスワードが一致しません。"
            })
        
        try:
            validate_password(data['password'], user=None)

        except DjangoValidationError as e:
            custom_messages = []
            error_mapping = {
                "too short": "パスワードが短すぎます（8文字以上必要です）。",
                "too common": "このパスワードは一般的すぎます。",
                "entirely numeric": "パスワードは数字だけでは登録できません。",
                "too similar": "パスワードがユーザー情報と似すぎています。",
            }
            
            for msg in e.messages:
                matched = False
                for key, custom_msg in error_mapping.items():
                    if key in msg.lower():
                        custom_messages.append(custom_msg)
                        matched = True
                        break

                if not matched:
                    custom_messages.append(msg)
            
            raise serializers.ValidationError({"password": custom_messages})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=validated_data['username'],
                    email=validated_data.get('email', ''),
                    password=validated_data['password'],
                )
            return user
        
        except Exception as e:
            raise serializers.ValidationError({
                'detail': "システムエラーが発生しました。しばらくしてから再度お試しください"
            })