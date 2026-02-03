from django.urls import path
from .views import SyncStepsView, StepHistoryView  # クラスをインポート

urlpatterns = [
    # クラスベースビューの場合は .as_view() が必要です
    path('steps/sync/', SyncStepsView.as_view(), name='sync_steps'),
    path('history/', StepHistoryView.as_view(), name='step_history'),
]