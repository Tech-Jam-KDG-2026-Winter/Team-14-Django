from django.db import models
from django.conf import settings

class StepCount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # どのユーザーか
    date = models.DateField() # 記録日
    step_count = models.PositiveIntegerField(default=0) # 取得した歩数
    
    # 【ロジック担当分】歩数から算出する習慣化スコアや消費カロリー
    calculated_value = models.FloatField(default=0.0) 

    class Meta:
        unique_together = ('user', 'date') # 重複防止

    def save(self, *args, **kwargs):
        # 保存時に自動計算（歩数 × 0.04）
        self.calculated_value = self.step_count * 0.04 
        super().save(*args, **kwargs)

    def achievement_rate(self):
        # 履歴画面で使う達成率（目標8000歩の場合）
        goal = 8000
        return min(int((self.step_count / goal) * 100), 100)