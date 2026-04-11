from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.views import APIView

from fitness_backend.api_response import api_error, api_success
from .models import CheckIn, Exercise, Food, RecommendationPlan
from .recommenders import build_dashboard, build_engine_preview, recommend_for_user
from .serializers import CheckInSerializer, ExerciseSerializer, FoodSerializer, RecommendationPlanSerializer


class ExerciseListView(generics.ListAPIView):
    queryset = Exercise.objects.all().order_by('id')
    serializer_class = ExerciseSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return api_success(self.get_serializer(queryset, many=True).data, message='动作库获取成功')


class FoodListView(generics.ListAPIView):
    queryset = Food.objects.all().order_by('id')
    serializer_class = FoodSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return api_success(self.get_serializer(queryset, many=True).data, message='食谱库获取成功')


class RecommendationEngineView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return api_error('请传入 user_id', status_code=400)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return api_error('用户不存在', status_code=404)
        if not hasattr(user, 'profile'):
            return api_error('用户尚未创建健康档案', status_code=400)

        return api_success(build_engine_preview(user), message='推荐引擎状态获取成功')


class RecommendPlanView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return api_error('请传入 user_id', status_code=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return api_error('用户不存在', status_code=404)

        if not hasattr(user, 'profile'):
            return api_error('用户尚未创建健康档案', status_code=400)

        try:
            rec = recommend_for_user(user)
        except ValueError as e:
            return api_error(str(e), status_code=400)

        suggestion = rec['suggestion'] + ' 推荐理由：' + '；'.join(rec['reason_list'])
        plan = RecommendationPlan.objects.create(
            user=user,
            exercise_text=rec['exercise_text'],
            diet_text=rec['diet_text'],
            suggestion=suggestion
        )
        data = RecommendationPlanSerializer(plan).data
        data.update({
            'algorithm_type': rec['algorithm_type'],
            'stage': rec['stage'],
            'reason_list': rec['reason_list'],
            'behavior_summary': rec['behavior_summary'],
            'exercise_title': rec['exercise'].title,
            'food_name': rec['food'].name,
            'exercise_candidates': rec['exercise_candidates'],
            'food_candidates': rec['food_candidates'],
        })
        return api_success(data, message='今日计划生成成功', status_code=201)


class RecommendationPlanUserListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return api_error('请传入 user_id', status_code=400)

        plans = RecommendationPlan.objects.select_related('user').filter(user_id=user_id).order_by('-plan_date', '-id')
        serializer = RecommendationPlanSerializer(plans, many=True)
        return api_success(serializer.data, message='计划列表获取成功')


class CheckInCreateView(generics.CreateAPIView):
    queryset = CheckIn.objects.select_related('user', 'plan').all().order_by('-id')
    serializer_class = CheckInSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_success(serializer.data, message='打卡成功', status_code=201)


class CheckInUserListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return api_error('请传入 user_id', status_code=400)

        checkins = CheckIn.objects.select_related('user', 'plan').filter(user_id=user_id).order_by('-created_at', '-id')
        serializer = CheckInSerializer(checkins, many=True)
        return api_success(serializer.data, message='打卡记录获取成功')


class DashboardView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return api_error('请传入 user_id', status_code=400)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return api_error('用户不存在', status_code=404)
        if not hasattr(user, 'profile'):
            return api_error('用户尚未创建健康档案', status_code=400)
        return api_success(build_dashboard(user), message='首页仪表盘获取成功')
