from django.urls import path
from . import views 

urlpatterns = [
    # 既存の同期用（もし views.SyncStepsView があるならそのままでOK）
    path('steps/sync/', views.SyncStepsView.as_view(), name='sync_steps'),
    
    # 履歴画面用（これ1行だけに絞ります！）
    path('history/', views.step_history, name='step_history'),
]