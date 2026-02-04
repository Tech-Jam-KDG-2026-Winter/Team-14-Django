from django.urls import path
from . import views

urlpatterns = [
    # --- HTML表示用 ---
    # 要件定義の「今日の実績 /home/」用
    path('home/', views.mypage_view, name='home'),
    path('mypage/', views.mypage_view, name='mypage'),
    
    # --- API（データ取得用） ---
    # 要件定義: 過去1週間の達成状況取得 /api/tasks/history/
    path('api/tasks/history/', views.StepHistoryView.as_view(), name='api_tasks_history'),
    
    # 古い形式の互換性維持（もし必要なら）
    path('api/step-history/', views.StepHistoryView.as_view(), name='api_step_history'),

    # Google Fit同期用
    # もし views.SyncStepsView が定義されているなら有効にしてください
    # path('steps/sync/', views.SyncStepsView.as_view(), name='sync_steps'),
]