from django.urls import path
from . import views

urlpatterns = [
    path("", views.today_tasks_view, name="today_tasks"),
    path("complete/<int:task_id>/", views.complete_task, name="complete_task"),
    path(
        "notification/read/<int:notification_id>/",
        views.mark_notification_read,
        name="notification_read"
    ),
]
