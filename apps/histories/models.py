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
        # 要件定義に基づいた計算ロジック（例：歩数に係数を掛ける）
        self.calculated_value = self.step_count * 0.04 
        super().save(*args, **kwargs)