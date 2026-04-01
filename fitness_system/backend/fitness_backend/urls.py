from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def api_home(request):
    return Response({
        'message': '健康体重管理健身系统 API 运行成功',
        'endpoints': {
            'register': '/api/users/register/',
            'profiles': '/api/users/profiles/',
            'health_records': '/api/health/records/',
            'exercises': '/api/plans/exercises/',
            'foods': '/api/plans/foods/',
            'recommend': '/api/plans/recommend/',
            'checkins': '/api/plans/checkins/',
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_home),
    path('api/users/', include('apps.users.urls')),
    path('api/health/', include('apps.health.urls')),
    path('api/plans/', include('apps.plans.urls')),
    path('api/discover/', include('apps.discover.urls')),
]
