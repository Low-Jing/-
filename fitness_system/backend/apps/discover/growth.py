from datetime import date, timedelta

from apps.plans.models import CheckIn
from .models import (
    ChallengeJoin,
    TopicCourseFavorite,
    KnowledgeArticleFavorite,
    CommunityPostLike,
)


LEVEL_RULES = [
    {'level': 1, 'min_points': 0, 'max_points': 49, 'name': '新手起步'},
    {'level': 2, 'min_points': 50, 'max_points': 149, 'name': '稳定执行'},
    {'level': 3, 'min_points': 150, 'max_points': 299, 'name': '进阶成长'},
    {'level': 4, 'min_points': 300, 'max_points': 499, 'name': '高频活跃'},
    {'level': 5, 'min_points': 500, 'max_points': 999999, 'name': '推荐增强样本'},
]


def _count_qs(user):
    joined_qs = ChallengeJoin.objects.filter(user=user).select_related('challenge').order_by('-created_at', '-id')
    course_qs = TopicCourseFavorite.objects.filter(user=user).select_related('course').order_by('-created_at', '-id')
    article_qs = KnowledgeArticleFavorite.objects.filter(user=user).select_related('article').order_by('-created_at', '-id')
    liked_qs = CommunityPostLike.objects.filter(user=user).select_related('post').order_by('-created_at', '-id')
    checkin_qs = CheckIn.objects.filter(user=user).select_related('plan').order_by('-created_at', '-id')
    return joined_qs, course_qs, article_qs, liked_qs, checkin_qs


def _compute_streak_days(checkin_qs):
    dates = []
    for item in checkin_qs:
        d = item.created_at.date()
        if d not in dates:
            dates.append(d)
    if not dates:
        return 0
    streak = 1
    cursor = dates[0]
    for d in dates[1:]:
        if d == cursor - timedelta(days=1):
            streak += 1
            cursor = d
        else:
            break
    return streak


def _calc_points(joined_count, course_count, article_count, liked_count, checkin_count, streak_days):
    return (
        joined_count * 8
        + course_count * 5
        + article_count * 4
        + liked_count * 2
        + checkin_count * 6
        + min(streak_days, 7) * 3
    )


def _calc_level(points):
    for item in LEVEL_RULES:
        if item['min_points'] <= points <= item['max_points']:
            current = item
            break
    else:
        current = LEVEL_RULES[-1]

    level = current['level']
    current_min = current['min_points']
    current_max = current['max_points']
    if level == LEVEL_RULES[-1]['level']:
        next_gap = 0
        progress = 100
        next_level_points = current_max
    else:
        next_rule = LEVEL_RULES[level]
        next_level_points = next_rule['min_points']
        next_gap = max(0, next_level_points - points)
        denominator = max(1, next_level_points - current_min)
        progress = min(100, round((points - current_min) * 100 / denominator))

    return {
        'level': level,
        'level_name': current['name'],
        'points': points,
        'progress': progress,
        'next_gap': next_gap,
        'next_level_points': next_level_points,
    }


def _build_badges(joined_count, course_count, article_count, liked_count, checkin_count, streak_days, points):
    return [
        {
            'icon': '🔥',
            'name': '打卡新星',
            'desc': '累计打卡 3 次',
            'active': checkin_count >= 3,
        },
        {
            'icon': '🏃',
            'name': '挑战参与者',
            'desc': '报名至少 1 个挑战',
            'active': joined_count >= 1,
        },
        {
            'icon': '🎓',
            'name': '课程收藏家',
            'desc': '收藏课程达到 2 门',
            'active': course_count >= 2,
        },
        {
            'icon': '📚',
            'name': '知识探索者',
            'desc': '收藏文章达到 2 篇',
            'active': article_count >= 2,
        },
        {
            'icon': '💬',
            'name': '社区观察员',
            'desc': '点赞动态达到 3 条',
            'active': liked_count >= 3,
        },
        {
            'icon': '🧠',
            'name': '推荐增强样本',
            'desc': '成长积分达到 120 分',
            'active': points >= 120,
        },
    ]


def _build_recent_actions(joined_qs, course_qs, article_qs, liked_qs, checkin_qs):
    records = []
    for item in joined_qs[:3]:
        records.append({
            'created_at': item.created_at,
            'action': '已报名挑战',
            'target': item.challenge.title,
            'type': 'challenge',
            'desc': f'报名了挑战《{item.challenge.title}》',
        })
    for item in course_qs[:3]:
        records.append({
            'created_at': item.created_at,
            'action': '已收藏课程',
            'target': item.course.title,
            'type': 'course',
            'desc': f'收藏了课程《{item.course.title}》',
        })
    for item in article_qs[:3]:
        records.append({
            'created_at': item.created_at,
            'action': '已收藏文章',
            'target': item.article.title,
            'type': 'article',
            'desc': f'收藏了文章《{item.article.title}》',
        })
    for item in liked_qs[:3]:
        records.append({
            'created_at': item.created_at,
            'action': '已点赞动态',
            'target': item.post.nickname,
            'type': 'post',
            'desc': f'点赞了 {item.post.nickname} 的社区动态',
        })
    for item in checkin_qs[:3]:
        records.append({
            'created_at': item.created_at,
            'action': '完成打卡',
            'target': item.content or '训练反馈',
            'type': 'checkin',
            'desc': f'完成打卡：{item.content or "已提交反馈"}',
        })

    records.sort(key=lambda x: x['created_at'], reverse=True)
    result = []
    for item in records[:8]:
        created = item.pop('created_at')
        item['time_text'] = created.strftime('%m-%d %H:%M')
        result.append(item)
    return result


def _build_behavior_keywords(user, joined_count, course_count, article_count, liked_count):
    profile = getattr(user, 'profile', None)
    keywords = []
    if profile:
        exercise_pref = [x.strip() for x in (profile.exercise_preference or '').replace('、', '，').split('，') if x.strip()]
        diet_pref = [x.strip() for x in (profile.diet_preference or '').replace('、', '，').split('，') if x.strip()]
        keywords.extend(exercise_pref[:4])
        keywords.extend(diet_pref[:3])

    if joined_count:
        keywords.append('挑战报名')
    if course_count:
        keywords.append('课程收藏')
    if article_count:
        keywords.append('知识阅读')
    if liked_count:
        keywords.append('社区互动')

    seen = []
    for item in keywords:
        if item and item not in seen:
            seen.append(item)
    return seen[:10]


def build_growth_summary(user):
    joined_qs, course_qs, article_qs, liked_qs, checkin_qs = _count_qs(user)
    joined_count = joined_qs.count()
    course_count = course_qs.count()
    article_count = article_qs.count()
    liked_count = liked_qs.count()
    checkin_count = checkin_qs.count()
    streak_days = _compute_streak_days(checkin_qs)

    points = _calc_points(joined_count, course_count, article_count, liked_count, checkin_count, streak_days)
    level_info = _calc_level(points)
    badges = _build_badges(joined_count, course_count, article_count, liked_count, checkin_count, streak_days, points)
    recent_actions = _build_recent_actions(joined_qs, course_qs, article_qs, liked_qs, checkin_qs)
    behavior_keywords = _build_behavior_keywords(user, joined_count, course_count, article_count, liked_count)

    if joined_count + course_count + article_count + liked_count >= 4:
        recommendation_phase = '内容推荐+协同过滤增强'
    else:
        recommendation_phase = '内容推荐'

    return {
        'joined_challenges_count': joined_count,
        'favorite_courses_count': course_count,
        'favorite_articles_count': article_count,
        'liked_posts_count': liked_count,
        'challenge_count': joined_count,
        'course_favorite_count': course_count,
        'article_favorite_count': article_count,
        'feed_like_count': liked_count,
        'interaction_total': joined_count + course_count + article_count + liked_count,
        'checkin_count': checkin_count,
        'streak_days': streak_days,
        'points': level_info['points'],
        'level': level_info['level'],
        'level_name': level_info['level_name'],
        'progress': level_info['progress'],
        'next_gap': level_info['next_gap'],
        'next_level_points': level_info['next_level_points'],
        'badges': badges,
        'recent_actions': recent_actions,
        'behavior_keywords': behavior_keywords,
        'recommendation_phase': recommendation_phase,
        'stage': recommendation_phase,
    }
