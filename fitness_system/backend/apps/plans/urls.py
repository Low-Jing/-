from django.urls import path
from .views import (
    CheckInCreateView,
    CheckInUserListView,
    DashboardView,
    ExerciseListView,
    FoodListView,
    RecommendationPlanUserListView,
    RecommendPlanView,
)

urlpatterns = [
    path('exercises/', ExerciseListView.as_view(), name='exercises'),
    path('foods/', FoodListView.as_view(), name='foods'),
    path('recommend/', RecommendPlanView.as_view(), name='recommend'),
    path('list/', RecommendationPlanUserListView.as_view(), name='plan-list'),
    path('checkins/', CheckInCreateView.as_view(), name='checkins'),
    path('checkins/list/', CheckInUserListView.as_view(), name='checkins-list'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
