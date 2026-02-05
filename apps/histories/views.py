import random
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required

from .models import Task, Notification


@login_required
def today_tasks_view(request):
    today = timezone.now().date()
    current_user = request.user

    # 同時アクセス対策（ロック）
    with transaction.atomic():
        tasks = Task.objects.select_for_update().filter(
            user=current_user,
            target_date=today
        )

        if not tasks.exists():
            create_today_tasks(today, current_user)
            tasks = Task.objects.filter(
                user=current_user,
                target_date=today
            )

    create_notifications(today, current_user)

    notifications = Notification.objects.filter(
        user=current_user,
        target_date=today,
        is_read=False
    )

    return render(request, "tasks/today.html", {
        "tasks": tasks,
        "notifications": notifications,
    })


def create_today_tasks(today, current_user):
    tasks = []

    # 固定タスク
    fixed_titles = ["部屋のカーテンを開ける", "水を飲む"]
    for title in fixed_titles:
        task, _ = Task.objects.get_or_create(
            user=current_user,
            target_date=today,
            title=title,
            defaults={"task_type": "fixed"}
        )
        tasks.append(task)

    # ランダムタスク
    used_titles = Task.objects.filter(
        user=current_user
    ).values_list("title", flat=True)

    other_users_tasks = Task.objects.filter(
        ~Q(user=current_user),
        task_type="random"
    ).exclude(title__in=used_titles)

    title = (
        random.choice(list(other_users_tasks)).title
        if other_users_tasks.exists()
        else "ストレッチ1分"
    )

    task, _ = Task.objects.get_or_create(
        user=current_user,
        target_date=today,
        title=title,
        defaults={"task_type": "random"}
    )
    tasks.append(task)

    # 週1重い運動
    monday = today - timedelta(days=today.weekday())
    weekly_exists = Task.objects.filter(
        user=current_user,
        task_type="weekly",
        target_date__gte=monday,
        target_date__lte=today
    ).exists()

    if not weekly_exists:
        task, _ = Task.objects.get_or_create(
            user=current_user,
            target_date=today,
            title="腹筋10回",
            defaults={"task_type": "weekly"}
        )
        tasks.append(task)

    return tasks


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(
        Task,
        id=task_id,
        user=request.user
    )
    task.is_completed = True
    task.save()
    return redirect("today_tasks")


def create_notifications(today, current_user):
    incomplete_tasks = Task.objects.filter(
        user=current_user,
        target_date=today,
        is_completed=False
    )

    if incomplete_tasks.exists():
        Notification.objects.get_or_create(
            user=current_user,
            target_date=today,
            defaults={
                "message": "今日のタスクがまだ残っています 🌱"
            }
        )


@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )
    notification.is_read = True
    notification.save()
    return redirect("today_tasks")
