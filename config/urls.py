from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from apps.common.api.health import healthz
# 必要なViewをインポート（views.pyの場所に合わせて調整してください）
from apps.histories.views import (
    mypage_view, 
    signup_view, 
    # django.contrib.authの標準Viewを使う場合
)
from django.contrib.auth import views as auth_views 

def root(request):
    return JsonResponse({"service": "django-starter", "status": "ok"})

urlpatterns = [
    path("", root),
    path("admin/", admin.site.urls),
    path("healthz/", healthz),
    
    # 1. API（グラフデータなど）
    path('api/', include('apps.histories.urls')),

    # 2. 認証系（HTML画面）
    path('signup/', signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # 3. パスワードリセット系
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),

    # 4. メイン画面
    path('mypage/', mypage_view, name='mypage'),
]