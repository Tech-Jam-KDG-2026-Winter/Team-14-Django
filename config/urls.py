from django.contrib import admin
from django.urls import path, include
from apps.common.api.health import healthz

urlpatterns = [
    path("", include('apps.users.urls')),
    path("admin/", admin.site.urls),

    # ログイン関連
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),

    # User情報
    path('api/users/', include('apps.users.urls')),

    path("healthz/", healthz),
    path('api/', include('apps.histories.urls')),
]