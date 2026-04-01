from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CheckIn, Exercise, Food, RecommendationPlan
from .recommenders import build_dashboard, recommend_for_user
from .serializers import CheckInSerializer, ExerciseSerializer, FoodSerializer, RecommendationPlanSerializer


class ExerciseListView(generics.ListAPIView):
    queryset = Exercise.objects.all().order_by('id')
    serializer_class = ExerciseSerializer


class FoodListView(generics.ListAPIView):
    queryset = Food.objects.all().order_by('id')
    serializer_class = FoodSerializer


class RecommendPlanView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'message': '请传入 user_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        if not hasattr(user, 'profile'):
            return Response({'message': '用户尚未创建健康档案'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rec = recommend_for_user(user)
        except ValueError as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        plan = RecommendationPlan.objects.create(
            user=user,
            exercise_text=rec['exercise_text'],
            diet_text=rec['diet_text'],
            suggestion=rec['suggestion'] + ' 推荐理由：' + '；'.join(rec['reason_list'])
        )
        data = RecommendationPlanSerializer(plan).data
        data['algorithm_type'] = rec['algorithm_type']
        data['reason_list'] = rec['reason_list']
        data['exercise_title'] = rec['exercise'].title
        data['food_name'] = rec['food'].name
        return Response(data, status=status.HTTP_201_CREATED)


class RecommendationPlanUserListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'message': '请传入 user_id'}, status=status.HTTP_400_BAD_REQUEST)

        plans = RecommendationPlan.objects.select_related('user').filter(user_id=user_id).order_by('-plan_date', '-id')
        serializer = RecommendationPlanSerializer(plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CheckInCreateView(generics.CreateAPIView):
    queryset = CheckIn.objects.select_related('user', 'plan').all().order_by('-id')
    serializer_class = CheckInSerializer


class CheckInUserListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'message': '请传入 user_id'}, status=status.HTTP_400_BAD_REQUEST)

        checkins = CheckIn.objects.select_related('user', 'plan').filter(user_id=user_id).order_by('-created_at', '-id')
        serializer = CheckInSerializer(checkins, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DashboardView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'message': '请传入 user_id'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        if not hasattr(user, 'profile'):
            return Response({'message': '用户尚未创建健康档案'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(build_dashboard(user), status=status.HTTP_200_OK)
