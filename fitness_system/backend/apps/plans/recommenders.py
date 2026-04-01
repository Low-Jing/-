import re
from collections import defaultdict
from django.contrib.auth.models import User
from apps.health.models import HealthRecord
from apps.plans.models import CheckIn, Exercise, Food, RecommendationPlan

NEGATIVE_WORDS = ['太累', '太难', '难坚持', '不舒服', '疼', '痛', '不喜欢', '讨厌']
POSITIVE_WORDS = ['完成', '不错', '喜欢', '轻松', '舒服', '很好', '坚持', '有成就']


def split_tokens(text):
    if not text:
        return []
    text = re.sub(r'[，、/\|]+', ',', str(text))
    arr = [item.strip() for item in text.split(',') if item.strip()]
    return arr


def extract_minutes(text):
    if not text:
        return 30
    match = re.search(r'(\d+)', str(text))
    if match:
        return int(match.group(1))
    return 30


def latest_health_record(user):
    return HealthRecord.objects.filter(user=user).order_by('-created_at', '-id').first()


def build_profile_context(user):
    profile = user.profile
    record = latest_health_record(user)
    bmi = record.bmi if record else 0
    return {
        'profile': profile,
        'bmi': bmi,
        'minutes': extract_minutes(profile.available_time),
        'exercise_tokens': split_tokens(profile.exercise_preference),
        'diet_tokens': split_tokens(profile.diet_preference),
        'dislike_tokens': split_tokens(profile.dislike_items),
    }


def score_exercise(item, context):
    profile = context['profile']
    exercise_tokens = context['exercise_tokens']
    minutes = context['minutes']
    bmi = context['bmi']
    score = 0
    reasons = []

    if item.fit_goal == profile.goal_type:
        score += 45
        reasons.append('目标类型匹配')

    item_text = f"{item.title} {item.category} {item.description}"
    for token in exercise_tokens:
        if token and token in item_text:
            score += 20
            reasons.append('命中运动偏好')
            break

    diff = abs((item.duration_minutes or 30) - minutes)
    if diff <= 10:
        score += 15
        reasons.append('时长与可用时间接近')
    elif diff <= 20:
        score += 8

    if profile.goal_type == 'lose_weight':
        burn_score = min(int((item.calories or 0) / 20), 15)
        score += burn_score
        if burn_score >= 10:
            reasons.append('热量消耗适合减脂')
    elif profile.goal_type == 'gain_muscle':
        if '力量' in item.category or '抗阻' in item.description or '核心' in item.description:
            score += 15
            reasons.append('训练类型适合增肌')
    else:
        if item.difficulty in ['低', '中等']:
            score += 10
            reasons.append('训练强度适合健康保持')

    if bmi and bmi >= 24 and item.difficulty == '高':
        score -= 5

    return {
        'item': item,
        'score': score,
        'reasons': reasons[:3]
    }


def score_food(item, context):
    profile = context['profile']
    diet_tokens = context['diet_tokens']
    dislike_tokens = context['dislike_tokens']
    score = 0
    reasons = []

    if item.fit_goal == profile.goal_type:
        score += 45
        reasons.append('饮食目标匹配')

    tag_text = f"{item.name} {item.preference_tag} {item.description}"
    for token in diet_tokens:
        if token and token in tag_text:
            score += 20
            reasons.append('命中饮食偏好')
            break

    disliked = False
    for token in dislike_tokens:
        if token and token in tag_text:
            score -= 100
            disliked = True
            reasons.append('命中厌恶项，强制降权')
            break
    if disliked:
        return {
            'item': item,
            'score': score,
            'reasons': reasons[:3]
        }

    if profile.goal_type == 'lose_weight':
        if (item.calories or 0) <= 380:
            score += 15
            reasons.append('热量控制更适合减脂')
        if (item.protein or 0) >= 20:
            score += 10
    elif profile.goal_type == 'gain_muscle':
        if (item.protein or 0) >= 28:
            score += 15
            reasons.append('蛋白质更适合增肌')
        if 350 <= (item.calories or 0) <= 550:
            score += 10
    else:
        if 250 <= (item.calories or 0) <= 450:
            score += 10
            reasons.append('热量较均衡')

    return {
        'item': item,
        'score': score,
        'reasons': reasons[:3]
    }


def similar_users(current_user):
    profile = current_user.profile
    current_ex = set(split_tokens(profile.exercise_preference))
    current_food = set(split_tokens(profile.diet_preference))
    candidates = User.objects.exclude(id=current_user.id).filter(profile__goal_type=profile.goal_type).select_related('profile')
    result = []
    for user in candidates:
        score = 40
        ex = set(split_tokens(user.profile.exercise_preference))
        fd = set(split_tokens(user.profile.diet_preference))
        if current_ex and ex:
            score += len(current_ex & ex) * 15
        if current_food and fd:
            score += len(current_food & fd) * 10
        if user.profile.available_time == profile.available_time:
            score += 10
        if score >= 50:
            result.append((user, score))
    result.sort(key=lambda x: x[1], reverse=True)
    return result[:5]


def checkin_sentiment(text):
    text = text or ''
    for word in NEGATIVE_WORDS:
        if word in text:
            return -1
    for word in POSITIVE_WORDS:
        if word in text:
            return 1
    return 0


def collaborative_boost(exercise, food, current_user):
    users = similar_users(current_user)
    if not users:
        return 0, 0, []

    exercise_boost = 0
    food_boost = 0
    reasons = []
    for user, sim in users:
        checkins = CheckIn.objects.filter(user=user, plan__isnull=False).select_related('plan').order_by('-created_at')[:20]
        local_hit = False
        for checkin in checkins:
            plan = checkin.plan
            sentiment = checkin_sentiment(checkin.feeling)
            weight = 6 if sentiment >= 0 else -4
            if exercise.title in (plan.exercise_text or ''):
                exercise_boost += max(0, int(sim / 10) + weight)
                local_hit = True
            if food.name in (plan.diet_text or ''):
                food_boost += max(0, int(sim / 10) + weight)
                local_hit = True
        if local_hit:
            reasons.append(f'相似用户 {user.username} 的成功执行记录提供了增强信号')
    return exercise_boost, food_boost, reasons[:3]


def recommend_for_user(user):
    context = build_profile_context(user)
    exercises = list(Exercise.objects.all())
    foods = list(Food.objects.all())
    if not exercises or not foods:
        raise ValueError('请先初始化动作库和食谱库数据')

    exercise_scores = [score_exercise(item, context) for item in exercises]
    food_scores = [score_food(item, context) for item in foods]
    exercise_scores.sort(key=lambda x: x['score'], reverse=True)
    food_scores.sort(key=lambda x: x['score'], reverse=True)

    best_ex = exercise_scores[0]
    best_food = food_scores[0]
    ex_cf, food_cf, cf_reasons = collaborative_boost(best_ex['item'], best_food['item'], user)

    algorithm_type = 'content_based'
    if ex_cf > 0 or food_cf > 0:
        algorithm_type = 'hybrid_cf'
        best_ex['score'] += ex_cf
        best_food['score'] += food_cf

    final_reason = []
    final_reason.extend(best_ex['reasons'])
    final_reason.extend(best_food['reasons'])
    final_reason.extend(cf_reasons)
    final_reason = list(dict.fromkeys([item for item in final_reason if item]))[:5]

    exercise = best_ex['item']
    food = best_food['item']
    suggestion = '建议连续执行 7 天后，根据体重变化、主观反馈与完成率对计划进行微调。'
    if algorithm_type == 'hybrid_cf':
        suggestion += ' 当前阶段已叠加相似用户成功打卡信号，属于“内容推荐 + 协同过滤增强”模式。'
    else:
        suggestion += ' 当前阶段以内容推荐为主，更适合冷启动和样本较少的系统。'

    return {
        'exercise': exercise,
        'food': food,
        'algorithm_type': algorithm_type,
        'reason_list': final_reason,
        'exercise_text': f'今日训练：{exercise.title}，分类 {exercise.category}，时长 {exercise.duration_minutes} 分钟，预计消耗 {exercise.calories} 千卡，难度 {exercise.difficulty}。',
        'diet_text': f'今日饮食：推荐 {food.name}，约 {food.calories} 千卡，蛋白质 {food.protein}g，标签 {food.preference_tag}。',
        'suggestion': suggestion,
    }


def build_dashboard(user):
    profile = user.profile
    records = list(HealthRecord.objects.filter(user=user).order_by('-record_date', '-id')[:7].values('id', 'weight', 'body_fat', 'bmi', 'bmr', 'record_date', 'note'))
    plans = list(RecommendationPlan.objects.filter(user=user).order_by('-created_at', '-id')[:5].values('id', 'plan_date', 'exercise_text', 'diet_text', 'suggestion', 'created_at'))
    checkins = list(CheckIn.objects.filter(user=user).order_by('-created_at', '-id')[:10].values('id', 'checkin_type', 'content', 'feeling', 'created_at', 'plan_id'))

    date_map = defaultdict(bool)
    for item in checkins:
        date_key = str(item['created_at'])[:10]
        if date_key:
            date_map[date_key] = True

    streak = 0
    import datetime
    day = datetime.date.today()
    for _ in range(30):
        key = str(day)
        if date_map.get(key):
            streak += 1
            day -= datetime.timedelta(days=1)
        else:
            break

    recommendation_phase = '内容推荐'
    if len(User.objects.exclude(id=user.id)) >= 2 and len(checkins) >= 1:
        recommendation_phase = '内容推荐 + 协同过滤增强'

    return {
        'user': {
            'username': user.username,
            'goal_type': profile.goal_type,
            'current_weight': profile.current_weight,
            'target_weight': profile.target_weight,
            'available_time': profile.available_time,
            'exercise_preference': profile.exercise_preference,
            'diet_preference': profile.diet_preference,
        },
        'streak': streak,
        'recommendation_phase': recommendation_phase,
        'latest_record': records[0] if records else None,
        'latest_plan': plans[0] if plans else None,
        'recent_records': records,
        'recent_checkins': checkins,
    }
