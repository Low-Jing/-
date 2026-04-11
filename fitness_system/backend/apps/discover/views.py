from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
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
    {
        'image_key': 'banner1',
        'title': '春季轻断食与快走周',
        'subtitle': '挑战、课程、知识与社区内容整合在一个页面',
        'badge': '内容运营位',
    },
    {
        'image_key': 'banner2',
        'title': '一周燃脂训练专栏',
        'subtitle': '围绕跑步、快走、HIIT 与轻食方案做连续推荐',
        'badge': '训练专题',
    },
    {
        'image_key': 'banner3',
        'title': '轻食与高蛋白组合',
        'subtitle': '更贴近减脂塑形用户的饮食内容入口',
        'badge': '饮食专题',
    },
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
        return {
            'joined_ids': set(),
            'course_favorite_ids': set(),
            'article_favorite_ids': set(),
            'post_liked_ids': set(),
        }
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
    mapping = {
        'lose_weight': '减脂塑形',
        'gain_muscle': '增肌提升',
        'keep_fit': '健康保持',
    }
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
    data['task_list'] = [
        '完成当天训练计划',
        '记录体重变化与主观感受',
        '完成饮食建议中的 1 个关键动作',
    ]
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
        f"{item.title} 以 {item.level} 难度展开，围绕 {', '.join(tags) if tags else '训练基础'} 做连续训练设计。\n"
        f"本课程更适合 {gtext} 用户，用较低理解成本快速进入系统训练。\n"
        "课程会强调动作质量、呼吸节奏、完成顺序与恢复建议。"
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
    data['takeaways'] = [
        '先保证连续执行，再追求高强度。',
        '训练和饮食建议需要成套理解。',
        '互动行为会帮助系统理解你的真实偏好。',
    ]
    return data


def enrich_post(item, data):
    data['topic_label'] = '训练反馈'
    data['comments_preview'] = [
        {'nickname': '轻食打卡组', 'text': '这种记录方式很适合后续复盘。'},
        {'nickname': '晨跑研究社', 'text': '如果能配合计划执行，效果会更稳定。'},
    ]
    return data


def build_personalized_pick(user, context, challenges, courses, articles):
    if not user:
        return {
            'title': '本周精选',
            'keywords': ['减脂', '轻食', '快走'],
            'reasons': ['当前尚无足够行为数据，先以目标和基础偏好做内容推荐。']
        }
    profile = getattr(user, 'profile', None)
    keywords = []
    if profile:
        keywords.extend([x for x in str(profile.exercise_preference or '').replace('，', ',').split(',') if x])
        keywords.extend([x for x in str(profile.diet_preference or '').replace('，', ',').split(',') if x])
    if context['joined_ids']:
        keywords.append('挑战报名')
    if context['course_favorite_ids']:
        keywords.append('课程收藏')
    if context['article_favorite_ids']:
        keywords.append('知识阅读')
    if context['post_liked_ids']:
        keywords.append('社区互动')
    dedup = []
    seen = set()
    for kw in keywords:
        kw = kw.strip()
        if kw and kw not in seen:
            seen.add(kw)
            dedup.append(kw)
    reasons = [
        '先依据目标、训练偏好和饮食偏好生成内容推荐。',
        '当发现页互动增多后，会把报名、收藏、点赞作为增强信号。',
    ]
    if context['joined_ids'] or context['course_favorite_ids'] or context['article_favorite_ids'] or context['post_liked_ids']:
        reasons.append('你已经产生行为数据，后续推荐会逐渐向“内容推荐 + 协同过滤增强”过渡。')
    return {
        'title': '为你精选',
        'keywords': dedup[:6] if dedup else ['减脂', '轻食', '快走'],
        'reasons': reasons,
    }


class DiscoverHomeView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        user = get_user_by_id(request.query_params.get('user_id'))
        context = build_user_context(user)

        challenges_qs = Challenge.objects.filter(is_active=True).prefetch_related('joins')[:6]
        courses_qs = TopicCourse.objects.filter(is_active=True).prefetch_related('favorites')[:6]
        articles_qs = KnowledgeArticle.objects.filter(is_active=True).prefetch_related('favorites')[:6]
        feeds_qs = CommunityPost.objects.filter(is_active=True).prefetch_related('likes')[:6]

        challenges = []
        for item, data in zip(challenges_qs, ChallengeSerializer(challenges_qs, many=True, context=context).data):
            challenges.append(enrich_challenge(item, data, user))

        topics = []
        for item, data in zip(courses_qs, TopicCourseSerializer(courses_qs, many=True, context=context).data):
            topics.append(enrich_course(item, data, user))

        articles = []
        for item, data in zip(articles_qs, KnowledgeArticleSerializer(articles_qs, many=True, context=context).data):
            articles.append(enrich_article(item, data, user))

        feeds = []
        for item, data in zip(feeds_qs, CommunityPostSerializer(feeds_qs, many=True, context=context).data):
            feeds.append(enrich_post(item, data))

        return Response({
            'theme': {
                'title': '发现',
                'desc': '去掉搜索，强化运营位、内容详情和模块互动，让发现页更像真正的内容型应用。'
            },
            'banners': BANNERS,
            'channels': CHANNELS,
            'editor_pick': build_personalized_pick(user, context, challenges, topics, articles),
            'challenges': challenges,
            'topics': topics,
            'articles': articles,
            'feeds': feeds,
        })


class UserInteractionSummaryView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        user = get_user_by_id(request.query_params.get('user_id'))
        if not user:
            return Response({'message': '用户不存在'}, status=status.HTTP_400_BAD_REQUEST)

        joined_qs = ChallengeJoin.objects.filter(user=user).select_related('challenge').order_by('-id')
        course_qs = TopicCourseFavorite.objects.filter(user=user).select_related('course').order_by('-id')
        article_qs = KnowledgeArticleFavorite.objects.filter(user=user).select_related('article').order_by('-id')
        liked_qs = CommunityPostLike.objects.filter(user=user).select_related('post').order_by('-id')

        recent_actions = []
        for item in joined_qs[:2]:
            recent_actions.append({'action': '已报名挑战', 'target': item.challenge.title})
        for item in course_qs[:2]:
            recent_actions.append({'action': '已收藏课程', 'target': item.course.title})
        for item in article_qs[:2]:
            recent_actions.append({'action': '已收藏文章', 'target': item.article.title})
        for item in liked_qs[:2]:
            recent_actions.append({'action': '已点赞动态', 'target': item.post.nickname})

        interaction_total = joined_qs.count() + course_qs.count() + article_qs.count() + liked_qs.count()
        stage = '内容推荐' if interaction_total < 4 else '内容推荐 + 协同过滤增强'
        behavior_keywords = []
        for item in joined_qs[:3]:
            behavior_keywords.append(item.challenge.tag)
        for item in course_qs[:3]:
            behavior_keywords.extend([x.strip() for x in item.course.tags.replace('、', '，').split('，') if x.strip()][:2])
        for item in article_qs[:3]:
            behavior_keywords.append(item.article.category)
        dedup = []
        seen = set()
        for kw in behavior_keywords:
            if kw not in seen:
                seen.add(kw)
                dedup.append(kw)

        return Response({
            'challenge_count': joined_qs.count(),
            'course_favorite_count': course_qs.count(),
            'article_favorite_count': article_qs.count(),
            'feed_like_count': liked_qs.count(),
            'interaction_total': interaction_total,
            'recent_actions': recent_actions[:6],
            'stage': stage,
            'behavior_keywords': dedup[:8],
        })


class ChallengeToggleJoinView(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request):
        user = get_user_by_id(request.data.get('user_id'))
        challenge_id = request.data.get('challenge_id')
        if not user or not challenge_id:
            return Response({'message': '缺少 user_id 或 challenge_id'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            challenge = Challenge.objects.get(id=challenge_id)
        except Challenge.DoesNotExist:
            return Response({'message': '挑战不存在'}, status=status.HTTP_404_NOT_FOUND)

        obj = ChallengeJoin.objects.filter(user=user, challenge=challenge).first()
        if obj:
            obj.delete()
            active = False
        else:
            ChallengeJoin.objects.create(user=user, challenge=challenge)
            active = True

        total = challenge.participant_count + challenge.joins.count()
        return Response({'active': active, 'count': total, 'people_text': f'{total:,}'})


class TopicCourseToggleFavoriteView(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request):
        user = get_user_by_id(request.data.get('user_id'))
        course_id = request.data.get('course_id')
        if not user or not course_id:
            return Response({'message': '缺少 user_id 或 course_id'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            course = TopicCourse.objects.get(id=course_id)
        except TopicCourse.DoesNotExist:
            return Response({'message': '课程不存在'}, status=status.HTTP_404_NOT_FOUND)

        obj = TopicCourseFavorite.objects.filter(user=user, course=course).first()
        if obj:
            obj.delete()
            active = False
        else:
            TopicCourseFavorite.objects.create(user=user, course=course)
            active = True
        return Response({'active': active})


class KnowledgeArticleToggleFavoriteView(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request):
        user = get_user_by_id(request.data.get('user_id'))
        article_id = request.data.get('article_id')
        if not user or not article_id:
            return Response({'message': '缺少 user_id 或 article_id'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            article = KnowledgeArticle.objects.get(id=article_id)
        except KnowledgeArticle.DoesNotExist:
            return Response({'message': '文章不存在'}, status=status.HTTP_404_NOT_FOUND)

        obj = KnowledgeArticleFavorite.objects.filter(user=user, article=article).first()
        if obj:
            obj.delete()
            active = False
        else:
            KnowledgeArticleFavorite.objects.create(user=user, article=article)
            active = True
        return Response({'active': active})


class CommunityPostToggleLikeView(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request):
        user = get_user_by_id(request.data.get('user_id'))
        post_id = request.data.get('post_id')
        if not user or not post_id:
            return Response({'message': '缺少 user_id 或 post_id'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            post = CommunityPost.objects.get(id=post_id)
        except CommunityPost.DoesNotExist:
            return Response({'message': '动态不存在'}, status=status.HTTP_404_NOT_FOUND)

        obj = CommunityPostLike.objects.filter(user=user, post=post).first()
        if obj:
            obj.delete()
            active = False
        else:
            CommunityPostLike.objects.create(user=user, post=post)
            active = True
        total = post.like_count + post.likes.count()
        return Response({'active': active, 'count': total})
