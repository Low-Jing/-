from django.contrib.auth.models import User
from django.db import models


class Exercise(models.Model):
    GOAL_CHOICES = (
        ('lose_weight', '减脂'),
        ('gain_muscle', '增肌'),
        ('maintain', '保持健康'),
    )
    title = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default='有氧')
    fit_goal = models.CharField(max_length=20, choices=GOAL_CHOICES, default='lose_weight')
    duration_minutes = models.PositiveIntegerField(default=30)
    calories = models.PositiveIntegerField(default=200)
    difficulty = models.CharField(max_length=20, default='中等')
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return self.title


class Food(models.Model):
    GOAL_CHOICES = (
        ('lose_weight', '减脂'),
        ('gain_muscle', '增肌'),
        ('maintain', '保持健康'),
    )
    name = models.CharField(max_length=50)
    fit_goal = models.CharField(max_length=20, choices=GOAL_CHOICES, default='lose_weight')
    calories = models.PositiveIntegerField(default=300)
    protein = models.FloatField(default=20)
    preference_tag = models.CharField(max_length=50, default='清淡')
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name


class RecommendationPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plans')
    plan_date = models.DateField(auto_now_add=True)
    exercise_text = models.TextField()
    diet_text = models.TextField()
    suggestion = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.plan_date}'


class CheckIn(models.Model):
    CHECKIN_TYPE_CHOICES = (
        ('exercise', '运动打卡'),
        ('diet', '饮食打卡'),
        ('weight', '体重打卡'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkins')
    plan = models.ForeignKey(RecommendationPlan, on_delete=models.SET_NULL, null=True, blank=True)
    checkin_type = models.CharField(max_length=20, choices=CHECKIN_TYPE_CHOICES)
    content = models.CharField(max_length=200)
    feeling = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}-{self.checkin_type}'
