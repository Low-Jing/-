from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer

from fitness_backend.api_response import api_error, api_success
from .models import (
    Challenge,
    TopicCourse,
    KnowledgeArticle,
    CommunityPost,
    ChallengeJoin,
    TopicCourseFavorite,
    KnowledgeArticleFavorite,
    CommunityPostLike,
)
from .serializers import (
    ChallengeSerializer,
    TopicCourseSerializer,
    KnowledgeArticleSerializer,
    CommunityPostSerializer,
)

CHANNELS = [
    {'icon': '🔥', 'text': '挑战赛', 'anchor': 'challenge'},
    {'icon': '🎬', 'text': '课程', 'anchor': 'course'},
    {'icon': '📚', 'text': '知识', 'anchor': 'article'},
    {'icon': '👥', 'text': '社区', 'anchor': 'community'},
]

BANNERS = [
    {'image_key': 'banner1', 'title': '春季轻断食与快走周', 'subtitle': '挑战、课程、知识与社区内容整合在一个页面', 'badge': '内容运营位'},
    {'image_key': 'banner2', 'title': '一周燃脂训练专栏', 'subtitle': '围绕跑步、快走、HIIT 与轻食方案做连续推荐', 'badge': '训练专题'},
    {'image_key': 'banner3', 'title': '轻食与高蛋白组合', 'subtitle': '更贴近减脂塑形用户的饮食内容入口', 'badge': '饮食专题'},
]


def get_user_by_id(user_id):
    if not user_id:
        return None
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None


def build_user_context(user):
    if not user:
        return {'joined_ids': set(), 'course_favorite_ids': set(), 'article_favorite_ids': set(), 'post_liked_ids': set()}
    return {
        'joined_ids': set(ChallengeJoin.objects.filter(user=user).values_list('challenge_id', flat=True)),
        'course_favorite_ids': set(TopicCourseFavorite.objects.filter(user=user).values_list('course_id', flat=True)),
        'article_favorite_ids': set(KnowledgeArticleFavorite.objects.filter(user=user).values_list('article_id', flat=True)),
        'post_liked_ids': set(CommunityPostLike.objects.filter(user=user).values_list('post_id', flat=True)),
    }


def goal_text(user):
    profile = getattr(user, 'profile', None) if user else None
    if not profile:
        return '健康保持'
    mapping = {'lose_weight': '减脂塑形', 'gain_muscle': '增肌提升', 'keep_fit': '健康保持'}
    return mapping.get(profile.goal_type, '健康保持')


def enrich_challenge(item, data, user):
    gtext = goal_text(user)
    data['cover_title'] = f"{item.title} · {gtext}专题"
    data['detail_intro'] = item.description or '通过连续挑战建立规律训练与饮食执行习惯。'
    data['detail_sections'] = [
        {'title': '适合人群', 'content': f'适合当前处于{gtext}阶段，希望通过连续 {item.days} 天建立节奏的用户。'},
        {'title': '完成规则', 'content': f'每天完成 1 次计划训练，并记录至少 1 条打卡反馈，连续坚持 {item.days} 天。'},
        {'title': '收获目标', 'content': '强化执行感、积累行为样本，并为后续推荐增强提供更稳定的兴趣信号。'},
    ]
    data['task_list'] = ['完成当天训练计划', '记录体重变化与主观感受', '完成饮食建议中的 1 个关键动作']
    return data


def enrich_course(item, data, user):
    tags = data.get('tag_list') or []
    gtext = goal_text(user)
    data['coach_name'] = 'FitLife AI 教练组'
    data['duration_text'] = f"建议每次 20~35 分钟，适合 {gtext} 阶段连续练习"
    data['lesson_points'] = [
        f'第 1 讲：理解 {item.title} 的训练目标与动作结构',
        '第 2 讲：掌握每次训练的节奏安排与热身要点',
        '第 3 讲：结合饮食建议完成一周执行闭环',
    ]
    data['full_content'] = (
        f"{item.title} 以 {item.level} 难度展开，围绕 {', '.join(tags) if tags else '训练基础'} 做连续训练设计。"
        f"本课程更适合 {gtext} 用户，用较低理解成本快速进入系统训练。"
        '课程会强调动作质量、呼吸节奏、完成顺序与恢复建议。'
    )
    return data


def enrich_article(item, data, user):
    gtext = goal_text(user)
    data['author'] = 'FitLife 内容编辑部'
    data['headline'] = f"{item.title}｜适合 {gtext} 用户阅读"
    data['article_blocks'] = [
        item.summary or '本文围绕饮食、训练和行为反馈之间的关系进行说明。',
        f'对于 {gtext} 用户，更重要的不是一次练很猛，而是建立可以连续执行的节奏。',
        '在系统中，知识内容不仅用于阅读，也会转化为用户兴趣和推荐增强的信号。',
    ]
    data['takeaways'] = ['先保证连续执行，再追求高强度。', '训练和饮食建议需要成套理解。', '互动行为会帮助系统理解你的真实偏好。']
    return data


def enrich_post(item, data):
    data['topic_label'] = '训练反馈'
    data['comments_preview'] = [
        {'nickname': '轻食打卡组', 'text': '这种记录方式很适合后续复盘。'},
        {'nickname': '晨跑研究社', 'text': '如果能配合计划执行，效果会更稳定。'},
    ]
    return data


def build_personalized_pick(user, context):
    if not user:
        return {'title': '本周精选', 'keywords': ['减脂', '轻食', '快走'], 'reasons': ['当前尚无足够行为数据，先以目标和基础偏好做内容推荐。']}
    profile = getattr(user, 'profile', None)
    keywords = []
    if profile:
        keywords.extend([x.strip() for x in str(profile.exercise_preference or '').replace('，', ',').split(',') if x.strip()])
        keywords.extend([x.strip() for x in str(profile.diet_preference or '').replace('，', ',').split(',') if x.strip()])
    if context['joined_ids']:
        keywords.append('挑战报名')
    if context['course_favorite_ids']:
        keywords.append('课程收藏')
    if context['article_favorite_ids']:
        keywords.append('知识阅读')
    if context['post_liked_ids']:
        keywords.append('社区互动')
    dedup = []
    for kw in keywords:
        if kw and kw not in dedup:
            dedup.append(kw)
    reasons = [
        '先依据目标、训练偏好和饮食偏好生成内容推荐。',
        '当发现页互动增多后，会把报名、收藏、点赞作为增强信号。',
    ]
    if context['joined_ids'] or context['course_favorite_ids'] or context['article_favorite_ids'] or context['post_liked_ids']:
        reasons.append('你已经产生行为数据，后续推荐会逐渐向“内容推荐 + 协同过滤增强”过渡。')
    return {'title': '为你精选', 'keywords': dedup[:6] if dedup else ['减脂', '轻食', '快走'], 'reasons': reasons}


class DiscoverHomeView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        user = get_user_by_id(request.query_params.get('user_id'))
        context = build_user_context(user)

        challenges_qs = Challenge.objects.filter(is_active=True).prefetch_related('joins')[:6]
        courses_qs = TopicCourse.objects.filter(is_active=True).prefetch_related('favorites')[:6]
        articles_qs = KnowledgeArticle.objects.filter(is_active=True).prefetch_related('favorites')[:6]
        feeds_qs = CommunityPost.objects.filter(is_active=True).prefetch_related('likes')[:6]

        raw_challenges = ChallengeSerializer(challenges_qs, many=True, context=context).data
        raw_topics = TopicCourseSerializer(courses_qs, many=True, context=context).data
        raw_articles = KnowledgeArticleSerializer(articles_qs, many=True, context=context).data
        raw_feeds = CommunityPostSerializer(feeds_qs, many=True, context=context).data

        challenges = [enrich_challenge(item, data, user) for item, data in zip(challenges_qs, raw_challenges)]
        topics = [enrich_course(item, data, user) for item, data in zip(courses_qs, raw_topics)]
        articles = [enrich_article(item, data, user) for item, data in zip(articles_qs, raw_articles)]
        feeds = [enrich_post(item, data) for item, data in zip(feeds_qs, raw_feeds)]

        payload = {
            'theme': {'title': '发现', 'desc': '去掉搜索，强化运营位、内容详情和模块互动，让发现页更像真正的内容型应用。'},
            'banners': BANNERS,
            'channels': CHANNELS,
            'editor_pick': build_personalized_pick(user, context),
            'challenges': challenges,
            'topics': topics,
            'articles': articles,
            'feeds': feeds,
        }
        return api_success(payload, message='发现页内容获取成功')


class ChallengeToggleJoinView(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request):
        user = get_user_by_id(request.data.get('user_id'))
        challenge_id = request.data.get('challenge_id')
        if not user or not challenge_id:
            return api_error('缺少 user_id 或 challenge_id', status_code=400)
        try:
            challenge = Challenge.objects.get(id=challenge_id)
        except Challenge.DoesNotExist:
            return api_error('挑战不存在', status_code=404)

        obj = ChallengeJoin.objects.filter(user=user, challenge=challenge).first()
        if obj:
            obj.delete()
            active = False
            message = '已取消报名'
        else:
            ChallengeJoin.objects.create(user=user, challenge=challenge)
            active = True
            message = '报名成功'

        total = challenge.participant_count + challenge.joins.count()
        return api_success({'active': active, 'count': total, 'people_text': f'{total:,}'}, message=message)


class TopicCourseToggleFavoriteView(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request):
        user = get_user_by_id(request.data.get('user_id'))
        course_id = request.data.get('course_id')
        if not user or not course_id:
            return api_error('缺少 user_id 或 course_id', status_code=400)
        try:
            course = TopicCourse.objects.get(id=course_id)
        except TopicCourse.DoesNotExist:
            return api_error('课程不存在', status_code=404)

        obj = TopicCourseFavorite.objects.filter(user=user, course=course).first()
        if obj:
            obj.delete()
            active = False
            message = '已取消收藏'
        else:
            TopicCourseFavorite.objects.create(user=user, course=course)
            active = True
            message = '收藏成功'
        return api_success({'active': active}, message=message)


class KnowledgeArticleToggleFavoriteView(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request):
        user = get_user_by_id(request.data.get('user_id'))
        article_id = request.data.get('article_id')
        if not user or not article_id:
            return api_error('缺少 user_id 或 article_id', status_code=400)
        try:
            article = KnowledgeArticle.objects.get(id=article_id)
        except KnowledgeArticle.DoesNotExist:
            return api_error('文章不存在', status_code=404)

        obj = KnowledgeArticleFavorite.objects.filter(user=user, article=article).first()
        if obj:
            obj.delete()
            active = False
            message = '已取消收藏'
        else:
            KnowledgeArticleFavorite.objects.create(user=user, article=article)
            active = True
            message = '收藏成功'
        return api_success({'active': active}, message=message)


class CommunityPostToggleLikeView(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request):
        user = get_user_by_id(request.data.get('user_id'))
        post_id = request.data.get('post_id')
        if not user or not post_id:
            return api_error('缺少 user_id 或 post_id', status_code=400)
        try:
            post = CommunityPost.objects.get(id=post_id)
        except CommunityPost.DoesNotExist:
            return api_error('动态不存在', status_code=404)

        obj = CommunityPostLike.objects.filter(user=user, post=post).first()
        if obj:
            obj.delete()
            active = False
            message = '已取消点赞'
        else:
            CommunityPostLike.objects.create(user=user, post=post)
            active = True
            message = '点赞成功'
        total = post.like_count + post.likes.count()
        return api_success({'active': active, 'count': total}, message=message)
