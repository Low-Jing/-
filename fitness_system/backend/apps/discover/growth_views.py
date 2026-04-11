from django.contrib.auth.models import User
from rest_framework.views import APIView

from fitness_backend.api_response import api_error, api_success
from .growth import build_growth_summary


class GrowthSummaryView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return api_error('请传入 user_id', status_code=400)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return api_error('用户不存在', status_code=404)

        return api_success(
            data=build_growth_summary(user),
            message='成长摘要获取成功',
            status_code=200,
        )
