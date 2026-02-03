from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from apps.common.api.health import healthz

def root(request):
    return JsonResponse({"service": "django-starter", "status": "ok"})

urlpatterns = [
    path("",root),
    path("admin/", admin.site.urls),

    # ログイン関連
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),

    # User情報
    path('api/users/', include('apps.users.urls')),

    path("healthz/", healthz),
    path('api/', include('apps.histories.urls')),
]
