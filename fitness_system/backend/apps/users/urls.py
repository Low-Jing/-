from django.urls import path
from .views import RegisterView, LoginView, UserProfileListView, UserProfileDetailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profiles/', UserProfileListView.as_view(), name='profiles'),
    path('profile/', UserProfileDetailView.as_view(), name='profile-detail'),
]