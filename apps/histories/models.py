from django.db import models
from django.conf import settings

class StepCount(models.Model):
    # レートを定数として定義
    HABIT_SCORE_RATE = 0.04
    STEP_GOAL = 8000

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    step_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')

    @property
    def calculated_value(self):
        """歩数から習慣化スコアを動的に算出"""
        return round(self.step_count * self.HABIT_SCORE_RATE, 2)

    @property
    def achievement_rate(self):
        """履歴画面で使う達成率（目標8000歩の場合）"""
        return min(int((self.step_count / self.STEP_GOAL) * 100), 100)

    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.step_count} steps"