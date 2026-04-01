from rest_framework import serializers
from .models import CheckIn, Exercise, Food, RecommendationPlan


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = '__all__'


class RecommendationPlanSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = RecommendationPlan
        fields = '__all__'


class CheckInSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = CheckIn
        fields = '__all__'
