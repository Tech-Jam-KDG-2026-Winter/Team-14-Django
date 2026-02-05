from django.shortcuts import render

# Create your views here.
from django.contrib.auth import get_user_model
from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomUserDetailsSerializer, UserProfileSerializer, UserCreateSerializer, GoogleFitCredentialSerializer, PasswordChangeSerializer
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from .models import UserProfile
import google_auth_oauthlib.flow
import random
from apps.tasks.models import Task

User = get_user_model()

def outer_home_view(request):
    return render(request, 'registration/outer_home.html')

class SignupView(TemplateView):
    template_name = 'registration/signup.html'

class LoginView(TemplateView):
    template_name = 'registration/login.html'

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
    
class LoginSuccessRedirectView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # シグナルによりProfileは必ず存在するので直接参照可能
        profile = request.user.profile
        
        # 判定1: Google Fit 連携がまだ（トークンが空）なら連携画面へ
        if not profile.google_fit_credentials:
            return redirect('users:fit_link')

        # 判定2: 今週の目標（weekly_heavy_goal）が未設定ならタスク選択画面へ
        if not profile.weekly_heavy_goal:
            return redirect('users:task_select')

        # 判定3: 全て揃っていればホーム画面へ
        return redirect('users:home')
    
class GoogleFitLinkView(LoginRequiredMixin, TemplateView):
    """1. 連携ボタンを表示する画面"""
    template_name = 'registration/fit_link.html'

class GoogleFitAuthView(LoginRequiredMixin, View):
    """2. Googleの認証画面へリダイレクトさせるView"""
    def get(self, request):
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            settings.GOOGLE_FIT_CLIENT_CONFIG, # settingsに保存したClient ID等の設定
            scopes=['https://www.googleapis.com/auth/fitness.activity.read']
        )
        flow.redirect_uri = request.build_absolute_uri(reverse('users:google_fit_callback'))
        
        authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
        request.session['oauth_state'] = state
        return redirect(authorization_url)

class GoogleFitCallbackView(LoginRequiredMixin, View):
    """3. Googleから戻ってきた後の処理（トークン保存）"""
    def get(self, request):
        state = request.session.get('oauth_state')
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            settings.GOOGLE_FIT_CLIENT_CONFIG,
            scopes=['https://www.googleapis.com/auth/fitness.activity.read'],
            state=state
        )
        flow.redirect_uri = request.build_absolute_uri(reverse('users:google_fit_callback'))
        
        # 認可コードをトークンに交換
        flow.fetch_token(authorization_response=request.build_absolute_uri(request.get_full_path()))
        
        # トークン（JSON）を保存
        profile = request.user.profile
        profile.google_fit_credentials = flow.credentials.to_json()
        profile.save()
        
        # 次のステップ（タスク選択）へ飛ばす
        return redirect('users:task_select')
    
class TaskSelectView(LoginRequiredMixin, View):
    def get(self, request):
        heavy_tasks = list(Task.objects.filter(category='heavy'))
        
        num_tasks = min(len(heavy_tasks), 3)
        display_tasks = random.sample(heavy_tasks, num_tasks) if heavy_tasks else []

        return render(request, 'registration/task_select.html', {
            'tasks': display_tasks
        })
    
    def post(self, request):
        task_id = request.POST.get('task_choice')

        if not task_id:
            return redirect('users:task_select')
        
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        serializer = UserProfileSerializer(
            profile, 
            data={'weekly_heavy_goal': task_id}, 
            partial=True
        )
        
        if serializer.is_valid():
            UserProfile.objects.filter(user=request.user).update(
                weekly_heavy_goal_id=serializer.validated_data['weekly_heavy_goal'].id
            )
            return redirect('users:home')
        
        return redirect('users:task_select')