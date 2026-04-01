from django.urls import path
from .views import HealthRecordListCreateView, HealthRecordUserListView

urlpatterns = [
    path('records/', HealthRecordListCreateView.as_view(), name='health-records'),
    path('records/list/', HealthRecordUserListView.as_view(), name='health-records-by-user'),
]