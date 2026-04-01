from django.contrib import admin
from .models import CheckIn, Exercise, Food, RecommendationPlan

admin.site.register(Exercise)
admin.site.register(Food)
admin.site.register(RecommendationPlan)
admin.site.register(CheckIn)
