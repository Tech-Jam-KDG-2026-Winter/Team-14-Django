from django.urls import path
from .views import mypage_view, StepHistoryView

urlpatterns = [
    # HTML表示用
    path('mypage/', mypage_view, name='mypage'),
    
    # グラフデータ取得用API
    path('api/step-history/', StepHistoryView.as_view(), name='api_step_history'),
]