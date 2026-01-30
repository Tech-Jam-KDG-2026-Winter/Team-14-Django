from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import StepCount
import datetime

# 歩数同期API (Android/iPhone共通)
class SyncStepsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        steps = request.data.get('steps')
        # その日の歩数を更新または新規作成
        step_data, created = StepCount.objects.update_or_create(
            user=request.user,
            date=datetime.date.today(),
            defaults={'step_count': steps}
        )
        return Response({"status": "success", "steps": step_data.step_count})

# 履歴表示用API
class StepHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 過去7日間のデータを取得
        today = datetime.date.today()
        seven_days_ago = today - datetime.timedelta(days=7)
        history = StepCount.objects.filter(
            user=request.user, 
            date__range=[seven_days_ago, today]
        ).order_by('date')
        
        # 習慣化が見れる画面用のデータ構造
        data = [{
            "date": h.date,
            "steps": h.step_count,
            "burned_calories": h.calculated_value
        } for h in history]
        
        return Response(data)