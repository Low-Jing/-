from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound, ValidationError


def get_request_user_id(request):
    """优先从请求头 X-User-Id 获取当前用户；兼容旧版 query 参数 user_id。"""
    raw = request.headers.get('X-User-Id') or request.META.get('HTTP_X_USER_ID')
    if not raw and hasattr(request, 'query_params'):
        raw = request.query_params.get('user_id')
    if not raw:
        raise ValidationError({'message': '缺少用户标识，请重新登录后再试。'})
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise ValidationError({'message': '用户标识格式错误。'})



def get_request_user(request):
    user_id = get_request_user_id(request)
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise NotFound('未找到对应用户。')
