import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import StepCount
from .utils import get_google_fit_steps

# --- 1. サインアップ用ビュー (新規追加) ---
def signup_view(request):
    """
    ユーザーが新規登録するためのビュー
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 登録後に自動でログイン
            return redirect('mypage')  # マイページへリダイレクト
    else:
        form = UserCreationForm()
    return render(request, 'signup_static.html', {'form': form})

# --- 2. マイページ表示用ビュー (HTMLを返す) ---
@login_required
def mypage_view(request):
    user = request.user
    today = datetime.date.today()

    # A. ページを開いたタイミングでGoogle Fit同期を試みる
    try:
        steps = get_google_fit_steps(user, target_date=today)
        StepCount.objects.update_or_create(
            user=user,
            date=today,
            defaults={'step_count': steps}
        )
    except Exception as e:
        print(f"Sync Error: {e}")

    # B. DBから表示用データを集計
    today_data = StepCount.objects.filter(user=user, date=today).first()
    today_steps = today_data.step_count if today_data else 0
    today_score = today_data.calculated_value if today_data else 0.0
    
    week_start = today - datetime.timedelta(days=6)
    weekly_logs = StepCount.objects.filter(user=user, date__range=[week_start, today])
    
    weekly_steps = sum(log.step_count for log in weekly_logs)
    weekly_score = sum(log.calculated_value for log in weekly_logs)

    context = {
        'today_steps': today_steps,
        'today_score': today_score,
        'weekly_steps': weekly_steps,
        'weekly_score': weekly_score,
        'today_count': 0, 
        'weekly_count': 0,
    }
    return render(request, 'histories/mypage.html', context)


# --- 3. グラフ用データAPI (JSONを返す) ---
class StepHistoryView(APIView):
    """
    Chart.jsで描画するための履歴データを返すAPI
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=19)
        
        history = StepCount.objects.filter(
            user=user, 
            date__range=[start_date, today]
        ).order_by('date')
        
        data_list = []
        for i in range(20):
            d = today - datetime.timedelta(days=i)
            log = next((h for h in history if h.date == d), None)
            
            data_list.append({
                "date": d.strftime('%m/%d'),
                "steps": log.step_count if log else 0,
                "score": log.calculated_value if log else 0
            })

        data_list.reverse() # 過去から未来の順に並び替え

        return Response({
            "labels": [d['date'] for d in data_list],
            "scores": [d['score'] for d in data_list],
            "steps": [d['steps'] for d in data_list]
        })