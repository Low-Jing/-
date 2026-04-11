from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.views import APIView

from fitness_backend.api_response import api_error, api_success
from .models import HealthRecord
from .serializers import HealthRecordSerializer


class HealthRecordListCreateView(generics.ListCreateAPIView):
    queryset = HealthRecord.objects.select_related('user').all().order_by('-record_date', '-id')
    serializer_class = HealthRecordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_success(serializer.data, message='健康记录保存成功', status_code=201)

    def perform_create(self, serializer):
        user_id = self.request.data.get('user')
        user = User.objects.get(id=user_id)
        serializer.save(user=user)


class HealthRecordUserListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return api_error('请传入 user_id', status_code=400)

        records = HealthRecord.objects.select_related('user').filter(
            user_id=user_id
        ).order_by('-record_date', '-id')
        serializer = HealthRecordSerializer(records, many=True)
        return api_success(serializer.data, message='健康记录获取成功')
