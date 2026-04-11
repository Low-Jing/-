from django.urls import path
from .me_views import MeProfileView, MeDashboardView, MeGrowthView
from .views import RegisterView, LoginView, UserProfileListView, UserProfileDetailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profiles/', UserProfileListView.as_view(), name='profiles'),
    path('profile/', UserProfileDetailView.as_view(), name='profile-detail'),
    path('me/profile/', MeProfileView.as_view(), name='me-profile'),
    path('me/dashboard/', MeDashboardView.as_view(), name='me-dashboard'),
    path('me/growth/', MeGrowthView.as_view(), name='me-growth'),
]