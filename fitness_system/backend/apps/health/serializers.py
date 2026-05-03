from rest_framework import serializers
from .models import HealthRecord


from rest_framework import serializers
from .models import HealthRecord


class HealthRecordSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = HealthRecord
        fields = '__all__'
        read_only_fields = ('bmi', 'bmr', 'record_date', 'created_at')

    def validate_weight(self, value):
        if value < 30 or value > 200:
            raise serializers.ValidationError('体重应在 30kg 到 200kg 之间。')
        return value

    def create(self, validated_data):
        user = validated_data['user']

        if not hasattr(user, 'profile'):
            raise serializers.ValidationError({
                'user': '该用户没有健康档案，请先使用注册接口创建用户。'
            })

        profile = user.profile
        weight = float(validated_data['weight'])
        height_cm = float(profile.height or 0)
        height_m = height_cm / 100 if height_cm else 0
        bmi = round(weight / (height_m * height_m), 2) if height_m > 0 else 0

        if profile.gender == 'male':
            bmr = round(10 * weight + 6.25 * height_cm - 5 * profile.age + 5, 2)
            sex_flag = 1
        else:
            bmr = round(10 * weight + 6.25 * height_cm - 5 * profile.age - 161, 2)
            sex_flag = 0

        estimated_body_fat = round((1.20 * bmi) + (0.23 * profile.age) - (10.8 * sex_flag) - 5.4, 2)
        if estimated_body_fat < 5:
            estimated_body_fat = 5.0
        if estimated_body_fat > 60:
            estimated_body_fat = 60.0

        validated_data['body_fat'] = estimated_body_fat
        validated_data['bmi'] = bmi
        validated_data['bmr'] = bmr

        instance = super().create(validated_data)

        profile.current_weight = weight
        profile.save(update_fields=['current_weight', 'updated_at'])

        return instance