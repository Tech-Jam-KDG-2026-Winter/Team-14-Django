from dotenv import load_dotenv  
from pathlib import Path
from datetime import timedelta
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# config/settings/base.py
# BASE_DIR は manage.py があるディレクトリを指すのが都合が良い
BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ.get("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set")

DEBUG = os.environ.get("DEBUG", "False") == "True"

FERNET_KEY = os.environ.get("FERNET_KEY")

if not FERNET_KEY:
    raise ValueError("FERNET_KEY is not set")

FERNET_KEYS = [FERNET_KEY]

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # 外部ライブラリ(API用)
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "dj_rest_auth",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "dj_rest_auth.registration",

    # starter apps
    "apps.common",
    'apps.users',
    'apps.tasks',
    'apps.histories',
]

SITE_ID = 1

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# チーム開発ならここは日本に寄せておくのが事故りにくい
LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 追記
# REST Framework の基本設定
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# JWT の詳細設定
REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_HTTPONLY': True,
    'JWT_AUTH_COOKIE': 'my-app-auth',
    'JWT_AUTH_REFRESH_COOKIE': 'my-refresh-token',

    'USER_DETAILS_SERIALIZER': 'apps.users.serializers.CustomUserDetailsSerializer',
    
    'OLD_PASSWORD_FIELD_ENABLED': True,
    'LOGOUT_ON_PASSWORD_CHANGE': True,

    'TOKEN_MODEL': None,

    'SESSION_LOGIN': False,
}

# 開発用：ログイン/サインアップの挙動
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_LOGIN_METHODS = {'username'}

# CORS許可設定 (開発用: 全て許可)
CORS_ALLOW_ALL_ORIGINS = True

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,                   # リフレッシュ時に新しいリフレッシュトークンを発行
    'BLACKLIST_AFTER_ROTATION': True,                # 古いリフレッシュトークンをブラックリストへ
    'AUTH_HEADER_TYPES': ('Bearer',),
}

AUTH_USER_MODEL = 'users.User'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Looking to send emails in production? Check out our Email API/SMTP product!
EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_HOST_USER = '79fde8d894021d'
EMAIL_PORT = 2525
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
from dotenv import main
env_vars = main.dotenv_values(BASE_DIR / '.env')
EMAIL_HOST_PASSWORD = env_vars.get("EMAIL_HOST_PASSWORD")

# もし読み込めていなければ、起動時にターミナルにエラーを出して止めます
if not EMAIL_HOST_PASSWORD:
    raise ValueError(f".envファイルからパスワードを読み込めませんでした。場所を確認してください: {BASE_DIR / '.env'}")

if not EMAIL_HOST_PASSWORD:
    raise ValueError("EMAIL_HOST_PASSWORD is not set in .env")
DEFAULT_FROM_EMAIL = 'admin@example.com'

DOMAIN = '127.0.0.1:8000'
SITE_NAME = 'Habitree'
LOGIN_URL = 'users:login_page'
LOGIN_REDIRECT_URL = 'users:login_success_redirect'

GOOGLE_FIT_CLIENT_CONFIG = {
    "web": {
        "client_id": env_vars.get("GOOGLE_CLIENT_ID"),
        "project_id": "habitree-486408",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": env_vars.get("GOOGLE_CLIENT_SECRET"),
        "redirect_uris": ["http://127.0.0.1:8000/google-fit/callback/"],
    }
}