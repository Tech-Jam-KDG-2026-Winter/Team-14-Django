from django.shortcuts import render

# Create your views here.
from django.contrib.auth import get_user_model
from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomUserDetailsSerializer, UserProfileSerializer, UserCreateSerializer, GoogleFitCredentialSerializer, PasswordChangeSerializer
import json

User = get_user_model()

class UserMeView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserDetailsSerializer

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        profile = self.request.user.profile
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(CustomUserDetailsSerializer(self.request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GoogleFitAuthView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GoogleFitCredentialSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = request.user.profile
        profile.google_fit_credentials = serializer.validated_data["google_fit_credentials"]
        profile.save()

        return Response(
            {"detail": "Google Fit認証情報を保存しました"},
            status=status.HTTP_200_OK
        )
    
class StepSyncView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        return Response({"detail": "Google Fitから歩数を取得"})
    
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

class CustomLogoutView(APIView):
    permission_classes = []

    def post(self, request):
        try:
            # リフレッシュトークンをクッキーから取得
            refresh_token = request.COOKIES.get('my-refresh-token')
            
            if refresh_token:
                # リフレッシュトークンをブラックリストに追加
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            response = Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_200_OK
            )
            
            # クッキーをクリア
            response.delete_cookie('my-app-auth')
            response.delete_cookie('my-refresh-token')
            
            return response
            
        except Exception as e:
            return Response(
                {"detail": "ログアウトに成功しましたが、トークンの無効化に失敗しました。"},
                status=status.HTTP_200_OK
            )
        
class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"detail": "パスワードを変更しました。"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.soft_delete()
        response = Response(
            {"detail": "退会しました。"}, 
            status=status.HTTP_200_OK
        )
        response.delete_cookie('my-app-auth')
        response.delete_cookie('my-refresh-token')

        return response