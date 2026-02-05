import random
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Q
from .models import Task, Notification

def today_tasks_view(request):
    today = timezone.now().date()
    current_user = request.user


    tasks = Task.objects.filter(target_date=today, user=current_user)
    if not tasks.exists():
        tasks = create_today_tasks(today, current_user)


    create_notifications(today, current_user)

    notifications = Notification.objects.filter(is_read=False, user=current_user)

    return render(request, "tasks/today.html", {
        "tasks": tasks,
        "notifications": notifications,
    })

def create_today_tasks(today, current_user):
    tasks = []


    fixed_titles = ["部屋のカーテンを開ける", "水を飲む"]
    for title in fixed_titles:
        tasks.append(Task.objects.create(
            title=title,
            task_type="fixed",
            target_date=today,
            user=current_user,
        ))

    other_users_tasks = Task.objects.filter(
        ~Q(user=current_user),
        task_type="random"
    ).exclude(title__in=Task.objects.filter(user=current_user).values_list('title', flat=True))

    if other_users_tasks.exists():
        random_task = random.choice(list(other_users_tasks))
        tasks.append(Task.objects.create(
            title=random_task.title,
            task_type="random",
            target_date=today,
            user=current_user,
        ))
    else:
        # フォールバック
        tasks.append(Task.objects.create(
            title="ストレッチ1分",
            task_type="random",
            target_date=today,
            user=current_user,
        ))

    # 週1重い運動（今週すでに作っていない場合のみ）
    # 今週の月曜を計算
    monday = today - timezone.timedelta(days=today.weekday())
    weekly_exists = Task.objects.filter(
        user=current_user,
        task_type="weekly",
        target_date__gte=monday,
        target_date__lte=today
    ).exists()

    if not weekly_exists:
        tasks.append(Task.objects.create(
            title="腹筋10回",
            task_type="weekly",
            target_date=today,
            user=current_user,
        ))

    return tasks

def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.is_completed = True
    task.save()
    return redirect("today_tasks")

def create_notifications(today, current_user):
    incomplete_tasks = Task.objects.filter(target_date=today, is_completed=False, user=current_user)
    if incomplete_tasks.exists():
        Notification.objects.get_or_create(
            user=current_user,
            message="今日のタスクがまだ残っています 🌱"
        )

def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect("today_tasks")
