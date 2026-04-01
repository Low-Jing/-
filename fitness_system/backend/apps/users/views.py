from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import UserProfile
from .serializers import UserProfileSerializer, UserRegisterSerializer, UserLoginSerializer


class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': '注册成功',
                'user_id': user.id,
                'username': user.username,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)
            if not user:
                return Response({
                    'message': '用户名或密码错误'
                }, status=status.HTTP_400_BAD_REQUEST)

            profile = getattr(user, 'profile', None)

            return Response({
                'message': '登录成功',
                'user_id': user.id,
                'profile_id': profile.id if profile else None,
                'username': user.username,
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileListView(generics.ListAPIView):
    queryset = UserProfile.objects.select_related('user').all().order_by('-id')
    serializer_class = UserProfileSerializer


class UserProfileDetailView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({
                'message': '请传入 user_id'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = UserProfile.objects.select_related('user').get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return Response({
                'message': '未找到该用户档案'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)