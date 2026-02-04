from django.contrib import admin
from django.urls import path, include
from apps.common.api.health import healthz
from apps.histories.views import mypage_view, signup_view
from django.contrib.auth import views as auth_views 

urlpatterns = [
    # トップページ（まずはサインアップかユーザー系へ飛ばす）
    path("", include('apps.users.urls')),
    path("admin/", admin.site.urls),

    # ログイン関連 (API用)
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),

    # User情報
    path('api/users/', include('apps.users.urls')),

    path("healthz/", healthz),
    
    # 履歴・グラフAPI
    path('api/', include('apps.histories.urls')),

    # --- HTML画面系 ---
    path('signup/', signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # メイン画面（要件定義の /home/ と /mypage/ 両方に対応）
    path('home/', mypage_view, name='home'),
    path('mypage/', mypage_view, name='mypage'),

    # パスワードリセット
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
]