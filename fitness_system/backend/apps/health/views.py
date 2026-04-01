from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import HealthRecord
from .serializers import HealthRecordSerializer


class HealthRecordListCreateView(generics.ListCreateAPIView):
    queryset = HealthRecord.objects.select_related('user').all().order_by('-record_date', '-id')
    serializer_class = HealthRecordSerializer


class HealthRecordUserListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({
                'message': '请传入 user_id'
            }, status=status.HTTP_400_BAD_REQUEST)

        records = HealthRecord.objects.select_related('user').filter(
            user_id=user_id
        ).order_by('-record_date', '-id')

        serializer = HealthRecordSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)