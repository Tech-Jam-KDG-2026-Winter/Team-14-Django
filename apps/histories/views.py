import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from .models import StepCount
from .utils import get_google_fit_steps
from django.shortcuts import render

User = get_user_model()

# --- 歩数同期API (ブラウザで開くだけで同期するようにGETに設定) ---
class SyncStepsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # デモ用：ログインしていなければ最初のユーザーを使用
            user = request.user if request.user.is_authenticated else User.objects.first()
            if not user:
                return Response({"status": "error", "message": "ユーザーが登録されていません。"}, status=400)
            
            # Google Fitから取得
            # 修正ポイント：左側のスペースを上の行と揃えました
            steps = get_google_fit_steps(user)
            
            # DBに保存または更新
            # 修正ポイント：ここも左側のスペースを揃えました
            step_data, _ = StepCount.objects.update_or_create(
                user=user,
                date=datetime.date.today(),
                defaults={'step_count': steps}
            )
            
            return Response({
                "status": "success",
                "steps": step_data.step_count,
                "score": step_data.calculated_value,
                "user": user.username
            })
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=400)

# --- 履歴表示用API ---
class StepHistoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user if request.user.is_authenticated else User.objects.first()
        
        # 直近7日間のデータを取得
        today = datetime.date.today()
        seven_days_ago = today - datetime.timedelta(days=6)
        
        history = StepCount.objects.filter(
            user=user, 
            date__range=[seven_days_ago, today]
        ).order_by('date')
        
        if not history.exists():
            # データがない場合の仮データ
            return Response([
                {"date": "01/30", "steps": 5000, "score": 50},
                {"date": "01/31", "steps": 2347, "score": 23}
            ])
            
        data = [{
            "date": h.date.strftime('%m/%d'),
            "steps": h.step_count,
            "score": h.calculated_value
        } for h in history]
        
        
        return Response(data)