from django.contrib.auth.models import User
from django.db import models


class HealthRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_records')
    weight = models.FloatField(help_text='体重 kg')
    body_fat = models.FloatField(help_text='体脂率 %', null=True, blank=True)
    bmi = models.FloatField(default=0)
    bmr = models.FloatField(default=0)
    note = models.CharField(max_length=200, blank=True, default='')
    record_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.record_date}'
