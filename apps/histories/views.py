from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated 
from .models import StepCount
from .utils import get_google_fit_steps
import datetime

class SyncStepsView(APIView):
    # ログイン済みユーザーのみアクセス可能にする
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            
            # Google Fitから取得
            steps = get_google_fit_steps(user)
            
            # DBに保存または更新
            step_data, created = StepCount.objects.update_or_create(
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

class StepHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        today = datetime.date.today()
        seven_days_ago = today - datetime.timedelta(days=6)
        
        history = StepCount.objects.filter(
            user=user, 
            date__range=[seven_days_ago, today]
        ).order_by('date')
        
        data = [{
            "date": h.date.strftime('%m/%d'),
            "steps": h.step_count,
            "score": h.calculated_value
        } for h in history]
        
        return Response(data)