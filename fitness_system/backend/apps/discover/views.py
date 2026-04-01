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


class DiscoverHomeView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        user = get_user_by_id(request.query_params.get('user_id'))

        challenges = Challenge.objects.filter(is_active=True).prefetch_related('joins')[:6]
        courses = TopicCourse.objects.filter(is_active=True).prefetch_related('favorites')[:6]
        articles = KnowledgeArticle.objects.filter(is_active=True).prefetch_related('favorites')[:6]
        feeds = CommunityPost.objects.filter(is_active=True).prefetch_related('likes')[:6]

        joined_ids = set()
        course_favorite_ids = set()
        article_favorite_ids = set()
        post_liked_ids = set()

        if user:
            joined_ids = set(ChallengeJoin.objects.filter(user=user).values_list('challenge_id', flat=True))
            course_favorite_ids = set(TopicCourseFavorite.objects.filter(user=user).values_list('course_id', flat=True))
            article_favorite_ids = set(KnowledgeArticleFavorite.objects.filter(user=user).values_list('article_id', flat=True))
            post_liked_ids = set(CommunityPostLike.objects.filter(user=user).values_list('post_id', flat=True))

        context = {
            'joined_ids': joined_ids,
            'course_favorite_ids': course_favorite_ids,
            'article_favorite_ids': article_favorite_ids,
            'post_liked_ids': post_liked_ids,
        }

        return Response({
            'theme': {
                'title': '春季轻断食与快走周',
                'desc': '把挑战、课程、营养知识和社区互动放到一个页面，让系统更像完整产品。'
            },
            'channels': CHANNELS,
            'challenges': ChallengeSerializer(challenges, many=True, context=context).data,
            'topics': TopicCourseSerializer(courses, many=True, context=context).data,
            'articles': KnowledgeArticleSerializer(articles, many=True, context=context).data,
            'feeds': CommunityPostSerializer(feeds, many=True, context=context).data,
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
            recent_actions.append({'type': 'challenge', 'title': item.challenge.title, 'text': '已报名挑战'})
        for item in course_qs[:2]:
            recent_actions.append({'type': 'course', 'title': item.course.title, 'text': '已收藏课程'})
        for item in article_qs[:2]:
            recent_actions.append({'type': 'article', 'title': item.article.title, 'text': '已收藏文章'})
        for item in liked_qs[:2]:
            recent_actions.append({'type': 'post', 'title': item.post.nickname, 'text': '已点赞动态'})

        return Response({
            'joined_challenges_count': joined_qs.count(),
            'favorite_courses_count': course_qs.count(),
            'favorite_articles_count': article_qs.count(),
            'liked_posts_count': liked_qs.count(),
            'interaction_total': joined_qs.count() + course_qs.count() + article_qs.count() + liked_qs.count(),
            'recent_actions': recent_actions[:6],
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
