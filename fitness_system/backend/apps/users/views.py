from django.contrib.auth import authenticate
from rest_framework import generics
from rest_framework.views import APIView

from fitness_backend.api_response import api_error, api_success
from .models import UserProfile
from .serializers import UserProfileSerializer, UserRegisterSerializer, UserLoginSerializer


class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return api_success({
                'user_id': user.id,
                'username': user.username,
            }, message='注册成功', status_code=201)
        return api_error('注册失败', status_code=400, data=serializer.errors)


class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return api_error('登录失败', status_code=400, data=serializer.errors)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)
        if not user:
            return api_error('用户名或密码错误', status_code=400)

        profile = getattr(user, 'profile', None)
        return api_success({
            'user_id': user.id,
            'profile_id': profile.id if profile else None,
            'username': user.username,
        }, message='登录成功')


class UserProfileListView(generics.ListAPIView):
    queryset = UserProfile.objects.select_related('user').all().order_by('-id')
    serializer_class = UserProfileSerializer


class UserProfileDetailView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return api_error('请传入 user_id', status_code=400)
        try:
            profile = UserProfile.objects.select_related('user').get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return api_error('未找到该用户档案', status_code=404)
        return api_success(UserProfileSerializer(profile).data, message='档案获取成功')
