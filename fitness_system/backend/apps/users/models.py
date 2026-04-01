from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女'),
    )
    GOAL_CHOICES = (
        ('lose_weight', '减脂'),
        ('gain_muscle', '增肌'),
        ('maintain', '保持健康'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.PositiveIntegerField(default=18)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    height = models.FloatField(help_text='身高，单位 cm', default=170)
    current_weight = models.FloatField(help_text='当前体重，单位 kg', default=60)
    target_weight = models.FloatField(help_text='目标体重，单位 kg', default=55)
    goal_type = models.CharField(max_length=20, choices=GOAL_CHOICES, default='lose_weight')
    exercise_preference = models.CharField(max_length=100, blank=True, default='跑步,快走')
    diet_preference = models.CharField(max_length=100, blank=True, default='高蛋白,清淡')
    dislike_items = models.CharField(max_length=100, blank=True, default='油炸食品')
    available_time = models.CharField(max_length=50, blank=True, default='晚上 30 分钟')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} 的健康档案'
