from datetime import timedelta

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from fitness_backend.current_user import get_request_user
from apps.users.serializers import UserProfileSerializer
from apps.health.models import HealthRecord
from apps.plans.models import RecommendationPlan, CheckIn

try:
    from apps.discover.models import (
        ChallengeJoin,
        TopicCourseFavorite,
        KnowledgeArticleFavorite,
        CommunityPostLike,
    )
except Exception:  # pragma: no cover
    ChallengeJoin = None
    TopicCourseFavorite = None
    KnowledgeArticleFavorite = None
    CommunityPostLike = None


def api_ok(data=None, message='success'):
    return Response({'code': 0, 'message': message, 'data': data})


def _safe_count(model, user):
    if model is None:
        return 0
    try:
        return model.objects.filter(user=user).count()
    except Exception:
        return 0


def _recent_actions(user, limit=8):
    items = []
    model_specs = [
        (ChallengeJoin, '报名挑战', 'challenge'),
        (TopicCourseFavorite, '收藏课程', 'course'),
        (KnowledgeArticleFavorite, '收藏文章', 'article'),
        (CommunityPostLike, '点赞动态', 'post'),
    ]
    for model, label, attr in model_specs:
        if model is None:
            continue
        try:
            qs = model.objects.filter(user=user).order_by('-id')[:limit]
            for obj in qs:
                target = getattr(obj, attr, None)
                title = getattr(target, 'title', None) or getattr(target, 'nickname', '内容')
                when = getattr(obj, 'created_at', None) or getattr(obj, 'updated_at', None)
                items.append({
                    'type': label,
                    'title': title,
                    'time': when.isoformat() if when else '',
                })
        except Exception:
            continue
    items.sort(key=lambda x: x['time'], reverse=True)
    return items[:limit]


def _calculate_level(points):
    if points < 50:
        return 1, '新手启动'
    if points < 150:
        return 2, '持续打卡'
    if points < 300:
        return 3, '成长加速'
    if points < 500:
        return 4, '稳定进阶'
    return 5, '训练达人'


def _badges(summary):
    return [
        {
            'name': '打卡新星',
            'earned': summary['checkin_count'] >= 3,
            'desc': '完成 3 次打卡获得',
        },
        {
            'name': '挑战参与者',
            'earned': summary['challenge_joined_count'] >= 2,
            'desc': '报名 2 个挑战获得',
        },
        {
            'name': '课程收藏家',
            'earned': summary['course_favorite_count'] >= 3,
            'desc': '收藏 3 个课程获得',
        },
        {
            'name': '知识探索者',
            'earned': summary['article_favorite_count'] >= 3,
            'desc': '收藏 3 篇文章获得',
        },
        {
            'name': '社区观察员',
            'earned': summary['post_like_count'] >= 5,
            'desc': '点赞 5 条动态获得',
        },
        {
            'name': '推荐增强样本',
            'earned': summary['interaction_total'] >= 6,
            'desc': '累计互动 6 次获得',
        },
    ]


def _streak_days(user):
    try:
        dates = list(
            CheckIn.objects.filter(user=user)
            .order_by('-created_at')
            .values_list('created_at', flat=True)
        )
    except Exception:
        return 0
    if not dates:
        return 0
    days = []
    for dt in dates:
        local_day = timezone.localtime(dt).date() if timezone.is_aware(dt) else dt.date()
        if local_day not in days:
            days.append(local_day)
    days.sort(reverse=True)
    streak = 0
    cursor = timezone.localdate()
    for day in days:
        if day == cursor:
            streak += 1
            cursor = cursor - timedelta(days=1)
        elif day == timezone.localdate() - timedelta(days=1) and streak == 0:
            streak += 1
            cursor = day - timedelta(days=1)
        else:
            break
    return streak


def _growth_summary(user):
    challenge_joined_count = _safe_count(ChallengeJoin, user)
    course_favorite_count = _safe_count(TopicCourseFavorite, user)
    article_favorite_count = _safe_count(KnowledgeArticleFavorite, user)
    post_like_count = _safe_count(CommunityPostLike, user)
    checkin_count = CheckIn.objects.filter(user=user).count()

    interaction_total = (
        challenge_joined_count
        + course_favorite_count
        + article_favorite_count
        + post_like_count
    )

    points = (
        checkin_count * 5
        + challenge_joined_count * 3
        + course_favorite_count
        + article_favorite_count
        + post_like_count
    )

    level, level_name = _calculate_level(points)
    current_floor = 0 if level == 1 else [0, 50, 150, 300, 500][level - 1]
    next_ceiling = [50, 150, 300, 500, 800][level - 1]
    progress = min(100, int(((points - current_floor) / max(1, next_ceiling - current_floor)) * 100))
    stage = '内容推荐' if interaction_total < 6 else '内容推荐 + 协同过滤增强'

    summary = {
        'challenge_joined_count': challenge_joined_count,
        'course_favorite_count': course_favorite_count,
        'article_favorite_count': article_favorite_count,
        'post_like_count': post_like_count,
        'checkin_count': checkin_count,
        'interaction_total': interaction_total,
        'streak_days': _streak_days(user),
        'points': points,
        'level': level,
        'level_name': level_name,
        'progress': progress,
        'stage': stage,
        'recent_actions': _recent_actions(user),
    }
    summary['badges'] = _badges(summary)
    return summary


class MeProfileView(APIView):
    def get(self, request):
        user = get_request_user(request)
        profile = getattr(user, 'profile', None)
        if not profile:
            return api_ok({}, '未找到用户档案')
        return api_ok(UserProfileSerializer(profile).data)


class MeDashboardView(APIView):
    def get(self, request):
        user = get_request_user(request)
        profile = getattr(user, 'profile', None)
        latest_record = HealthRecord.objects.filter(user=user).order_by('-record_date', '-id').first()
        latest_plan = RecommendationPlan.objects.filter(user=user).order_by('-plan_date', '-id').first()
        growth = _growth_summary(user)

        goal_progress = 0
        quick_tags = []

        if profile:
            latest_weight = None
            if latest_record and latest_record.weight is not None:
                latest_weight = float(latest_record.weight)
            else:
                latest_weight = float(profile.current_weight or 0)

            target_weight = float(profile.target_weight or 0)

            if latest_weight and target_weight:
                diff = abs(latest_weight - target_weight)
                baseline = max(latest_weight, target_weight)
                goal_progress = max(0, min(100, round((1 - diff / baseline) * 100)))

            for part in [profile.exercise_preference, profile.diet_preference]:
                if not part:
                    continue
                quick_tags.extend([x.strip() for x in str(part).replace('，', ',').split(',') if x.strip()])

        data = {
            'profile': UserProfileSerializer(profile).data if profile else {},
            'latest_record': {
                'weight': latest_record.weight,
                'bmi': latest_record.bmi,
                'body_fat': latest_record.body_fat,
                'record_date': latest_record.record_date,
            } if latest_record else None,
            'latest_plan': {
                'id': latest_plan.id,
                'plan_date': latest_plan.plan_date,
                'exercise_text': latest_plan.exercise_text,
                'diet_text': latest_plan.diet_text,
                'suggestion': latest_plan.suggestion,
            } if latest_plan else None,
            'goal_progress': goal_progress,
            'current_weight_for_progress': latest_record.weight if latest_record else (profile.current_weight if profile else None),
            'streak_days': growth['streak_days'],
            'recent_record_count': HealthRecord.objects.filter(user=user).count(),
            'engine_stage': growth['stage'],
            'quick_tags': quick_tags[:8],
        }
        return api_ok(data)


class MeGrowthView(APIView):
    def get(self, request):
        user = get_request_user(request)
        profile = getattr(user, 'profile', None)
        growth = _growth_summary(user)
        payload = {
            'profile': UserProfileSerializer(profile).data if profile else {},
            'growth': growth,
        }
        return api_ok(payload)