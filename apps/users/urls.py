from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from .views import UserMeView, GoogleFitAuthView, UserCreateView, CustomLogoutView, UserDeleteView,outer_home_view, SignupView, LoginView, LoginSuccessRedirectView, GoogleFitLinkView, GoogleFitCallbackView, TaskSelectView

app_name = 'users'

urlpatterns = [
    path('', outer_home_view, name='outer_home'),
    path('me/', UserMeView.as_view(), name='user_me'),
    path('signup/', UserCreateView.as_view(), name='signup'),
    path('signup-page/', SignupView.as_view(), name='signup_page'),
    path('signup-success/', TemplateView.as_view(template_name='registration/signup_success.html'), name='signup_success'),
    path('login-page/', auth_views.LoginView.as_view(), name='login_page'),
    path('logout/', CustomLogoutView.as_view(), name='custom_logout'), 
    path('delete/', UserDeleteView.as_view(), name='user_delete'),

    # パスワードリセット関連
    # 1. メールアドレス入力画面
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',          # すでにあるこのファイルを使う
        email_template_name='registration/password_reset_email.html',    # 内部処理用
        subject_template_name='registration/password_reset_subject.txt', # 内部処理用
        success_url='/api/users/password_reset/done/'       # 送信後に手順2へ飛ばす
    ), name='password_reset'),

    # 2. メール送信完了画面
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'            # これから作る(または名前を合わせる)
    ), name='password_reset_done'),

    # 3. 新しいパスワード入力画面 (メールのリンクから飛ぶ)
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',         # 新パスワード入力用
        success_url='/reset/done/'
    ), name='password_reset_confirm'),

    # 4. パスワードリセット完了画面
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'        # 最終完了画面
    ), name='password_reset_complete'),

    # ログイン後の振り分け
    path('login-redirect/', LoginSuccessRedirectView.as_view(), name='login_success_redirect'),
    
    # Fit連携画面
    # TemplateViewの方は削除して、作成した GoogleFitLinkView に一本化します
    path('fit-link/', GoogleFitLinkView.as_view(), name='fit_link'),
    path('google-fit/auth/', GoogleFitAuthView.as_view(), name='google_fit_auth'),
    path('google-fit/callback/', GoogleFitCallbackView.as_view(), name='google_fit_callback'),

    # タスク選択・ホーム
    path('task-select/', TaskSelectView.as_view(), name='task_select'),
    path('home/', TemplateView.as_view(template_name='home.html'), name='home'), # テンプレート名を指定   
]