from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile


from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    age = serializers.IntegerField(write_only=True)
    gender = serializers.CharField(write_only=True)
    height = serializers.FloatField(write_only=True)
    current_weight = serializers.FloatField(write_only=True)
    target_weight = serializers.FloatField(write_only=True)
    goal_type = serializers.CharField(write_only=True)
    exercise_preference = serializers.CharField(write_only=True, required=False, allow_blank=True)
    diet_preference = serializers.CharField(write_only=True, required=False, allow_blank=True)
    dislike_items = serializers.CharField(write_only=True, required=False, allow_blank=True)
    available_time = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'password',
            'age', 'gender', 'height', 'current_weight', 'target_weight',
            'goal_type', 'exercise_preference', 'diet_preference',
            'dislike_items', 'available_time'
        ]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('该用户名已存在，请更换用户名。')
        return value

    def validate_age(self, value):
        if value < 10 or value > 100:
            raise serializers.ValidationError('年龄应在 10 到 100 之间。')
        return value

    def validate_height(self, value):
        if value < 100 or value > 250:
            raise serializers.ValidationError('身高应在 100cm 到 250cm 之间。')
        return value

    def validate_current_weight(self, value):
        if value < 30 or value > 200:
            raise serializers.ValidationError('当前体重应在 30kg 到 200kg 之间。')
        return value

    def validate_target_weight(self, value):
        if value < 30 or value > 200:
            raise serializers.ValidationError('目标体重应在 30kg 到 200kg 之间。')
        return value

    def create(self, validated_data):
        profile_data = {
            'age': validated_data.pop('age'),
            'gender': validated_data.pop('gender'),
            'height': validated_data.pop('height'),
            'current_weight': validated_data.pop('current_weight'),
            'target_weight': validated_data.pop('target_weight'),
            'goal_type': validated_data.pop('goal_type'),
            'exercise_preference': validated_data.pop('exercise_preference', ''),
            'diet_preference': validated_data.pop('diet_preference', ''),
            'dislike_items': validated_data.pop('dislike_items', ''),
            'available_time': validated_data.pop('available_time', ''),
        }

        password = validated_data.pop('password')
        user = User(username=validated_data['username'])
        user.set_password(password)
        user.save()

        UserProfile.objects.create(user=user, **profile_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'