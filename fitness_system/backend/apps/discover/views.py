from django.contrib.auth.models import User
from django.db.models import Q
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
    {'icon': '🔥', 'text': '挑战赛'},
    {'icon': '🎬', 'text': '课程'},
    {'icon': '🥗', 'text': '饮食'},
    {'icon': '📚', 'text': '知识'},
    {'icon': '🏃', 'text': '跑步'},
    {'icon': '🧘', 'text': '拉伸'},
    {'icon': '👥', 'text': '社区'},
    {'icon': '⭐', 'text': '精选'},
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


def tokenize(text):
    if not text:
        return []
    cleaned = str(text)
    for sep in ['，', ',', '、', ' ', '/', '|', '-', '：', ':', '；', ';']:
        cleaned = cleaned.replace(sep, ' ')
    return [item.strip().lower() for item in cleaned.split() if item.strip()]


def build_interest_keywords(user, context):
    keywords = []
    if not user:
        return keywords

    profile = getattr(user, 'profile', None)
    if profile:
        keywords.extend(tokenize(profile.exercise_preference))
        keywords.extend(tokenize(profile.diet_preference))
        keywords.extend(tokenize(profile.goal_type))
        keywords.extend(tokenize(profile.available_time))

    joined = Challenge.objects.filter(id__in=context['joined_ids'])
    courses = TopicCourse.objects.filter(id__in=context['course_favorite_ids'])
    articles = KnowledgeArticle.objects.filter(id__in=context['article_favorite_ids'])

    for item in joined:
        keywords.extend(tokenize(item.title))
        keywords.extend(tokenize(item.tag))
    for item in courses:
        keywords.extend(tokenize(item.title))
        keywords.extend(tokenize(item.tags))
        keywords.extend(tokenize(item.level))
    for item in articles:
        keywords.extend(tokenize(item.title))
        keywords.extend(tokenize(item.category))

    seen = set()
    result = []
    for word in keywords:
        if word and word not in seen:
            seen.add(word)
            result.append(word)
    return result[:12]


def score_text(text, keywords):
    lower_text = str(text or '').lower()
    score = 0
    for kw in keywords:
        if kw and kw in lower_text:
            score += 1
    return score


def score_challenge(item, keywords, context):
    score = score_text(item.title, keywords) + score_text(item.description, keywords) + score_text(item.tag, keywords)
    if item.id in context['joined_ids']:
        score += 4
    return score


def score_course(item, keywords, context):
    score = score_text(item.title, keywords) + score_text(item.description, keywords) + score_text(item.tags, keywords) + score_text(item.level, keywords)
    if item.id in context['course_favorite_ids']:
        score += 4
    return score


def score_article(item, keywords, context):
    score = score_text(item.title, keywords) + score_text(item.summary, keywords) + score_text(item.category, keywords)
    if item.id in context['article_favorite_ids']:
        score += 4
    return score


def score_post(item, keywords, context):
    score = score_text(item.nickname, keywords) + score_text(item.content, keywords)
    if item.id in context['post_liked_ids']:
        score += 4
    return score


def build_banner_list():
    return [
        {
            'title': '春季轻断食与快走周',
            'subtitle': '挑战、课程、营养知识与社区互动整合到一个页面',
            'badge': '运营主题',
        },
        {
            'title': '减脂塑形精选内容',
            'subtitle': '围绕跑步、快走、轻食和拉伸，构建连续使用闭环',
            'badge': '内容推荐',
        },
        {
            'title': '行为数据正在积累',
            'subtitle': '报名、收藏、点赞等行为将用于后期协同过滤增强',
            'badge': '算法增强',
        },
    ]


class DiscoverHomeView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        user = get_user_by_id(request.query_params.get('user_id'))
        context = build_user_context(user)

        challenges = Challenge.objects.filter(is_active=True).prefetch_related('joins')[:6]
        courses = TopicCourse.objects.filter(is_active=True).prefetch_related('favorites')[:6]
        articles = KnowledgeArticle.objects.filter(is_active=True).prefetch_related('favorites')[:6]
        feeds = CommunityPost.objects.filter(is_active=True).prefetch_related('likes')[:6]

        return Response({
            'theme': {
                'title': '春季轻断食与快走周',
                'desc': '把挑战、课程、营养知识和社区互动放到一个页面，让系统更像完整产品。'
            },
            'banners': build_banner_list(),
            'channels': CHANNELS,
            'challenges': ChallengeSerializer(challenges, many=True, context=context).data,
            'topics': TopicCourseSerializer(courses, many=True, context=context).data,
            'articles': KnowledgeArticleSerializer(articles, many=True, context=context).data,
            'feeds': CommunityPostSerializer(feeds, many=True, context=context).data,
        })


class DiscoverSearchView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        user = get_user_by_id(request.query_params.get('user_id'))
        context = build_user_context(user)
        q = (request.query_params.get('q') or '').strip()
        tab = (request.query_params.get('tab') or 'all').strip()

        challenge_qs = Challenge.objects.filter(is_active=True)
        course_qs = TopicCourse.objects.filter(is_active=True)
        article_qs = KnowledgeArticle.objects.filter(is_active=True)
        post_qs = CommunityPost.objects.filter(is_active=True)

        if q:
            challenge_qs = challenge_qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(tag__icontains=q))
            course_qs = course_qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(tags__icontains=q) | Q(level__icontains=q))
            article_qs = article_qs.filter(Q(title__icontains=q) | Q(summary__icontains=q) | Q(category__icontains=q))
            post_qs = post_qs.filter(Q(nickname__icontains=q) | Q(content__icontains=q))

        data = {
            'query': q,
            'tab': tab,
            'challenges': ChallengeSerializer(challenge_qs[:8], many=True, context=context).data,
            'topics': TopicCourseSerializer(course_qs[:8], many=True, context=context).data,
            'articles': KnowledgeArticleSerializer(article_qs[:8], many=True, context=context).data,
            'feeds': CommunityPostSerializer(post_qs[:8], many=True, context=context).data,
        }

        if tab == 'challenge':
            data['topics'] = []
            data['articles'] = []
            data['feeds'] = []
        elif tab == 'course':
            data['challenges'] = []
            data['articles'] = []
            data['feeds'] = []
        elif tab == 'article':
            data['challenges'] = []
            data['topics'] = []
            data['feeds'] = []
        elif tab == 'community':
            data['challenges'] = []
            data['topics'] = []
            data['articles'] = []

        return Response(data)


class DiscoverRecommendView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        user = get_user_by_id(request.query_params.get('user_id'))
        context = build_user_context(user)
        keywords = build_interest_keywords(user, context)

        challenge_list = list(Challenge.objects.filter(is_active=True).prefetch_related('joins'))
        course_list = list(TopicCourse.objects.filter(is_active=True).prefetch_related('favorites'))
        article_list = list(KnowledgeArticle.objects.filter(is_active=True).prefetch_related('favorites'))
        post_list = list(CommunityPost.objects.filter(is_active=True).prefetch_related('likes'))

        challenge_list.sort(key=lambda item: (score_challenge(item, keywords, context), item.participant_count), reverse=True)
        course_list.sort(key=lambda item: (score_course(item, keywords, context), item.id), reverse=True)
        article_list.sort(key=lambda item: (score_article(item, keywords, context), item.read_minutes), reverse=True)
        post_list.sort(key=lambda item: (score_post(item, keywords, context), item.like_count), reverse=True)

        reasons = []
        if keywords:
            reasons.append('已根据你的偏好与互动行为提取关键词：' + '、'.join(keywords[:6]))
        else:
            reasons.append('当前仍以默认优质内容与基础内容推荐为主。')
        if context['joined_ids'] or context['course_favorite_ids'] or context['article_favorite_ids'] or context['post_liked_ids']:
            reasons.append('系统检测到你已产生发现页互动行为，后续可用于协同过滤增强。')
        else:
            reasons.append('继续参与挑战、收藏课程和点赞动态，可提升后续推荐个性化程度。')

        return Response({
            'stage': '内容推荐 + 行为增强准备',
            'keywords': keywords,
            'reasons': reasons,
            'challenge_recommendations': ChallengeSerializer(challenge_list[:4], many=True, context=context).data,
            'course_recommendations': TopicCourseSerializer(course_list[:4], many=True, context=context).data,
            'article_recommendations': KnowledgeArticleSerializer(article_list[:4], many=True, context=context).data,
            'community_recommendations': CommunityPostSerializer(post_list[:4], many=True, context=context).data,
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
            message = '已取消报名'
        else:
            ChallengeJoin.objects.create(user=user, challenge=challenge)
            active = True
            message = '报名成功'

        total = challenge.participant_count + challenge.joins.count()
        return Response({'active': active, 'count': total, 'people_text': f'{total:,}', 'message': message})


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
            message = '已取消收藏'
        else:
            TopicCourseFavorite.objects.create(user=user, course=course)
            active = True
            message = '已收藏课程'
        return Response({'active': active, 'message': message})


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
            message = '已取消收藏'
        else:
            KnowledgeArticleFavorite.objects.create(user=user, article=article)
            active = True
            message = '已收藏文章'
        return Response({'active': active, 'message': message})


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
            message = '已取消点赞'
        else:
            CommunityPostLike.objects.create(user=user, post=post)
            active = True
            message = '已点赞'

        total = post.like_count + post.likes.count()
        return Response({'active': active, 'count': total, 'message': message})
