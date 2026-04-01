from django.urls import path
from .views import (
    DiscoverHomeView,
    UserInteractionSummaryView,
    ChallengeToggleJoinView,
    TopicCourseToggleFavoriteView,
    KnowledgeArticleToggleFavoriteView,
    CommunityPostToggleLikeView,
)

urlpatterns = [
    path('home/', DiscoverHomeView.as_view(), name='discover-home'),
    path('user-summary/', UserInteractionSummaryView.as_view(), name='discover-user-summary'),
    path('challenge/toggle-join/', ChallengeToggleJoinView.as_view(), name='discover-challenge-toggle-join'),
    path('course/toggle-favorite/', TopicCourseToggleFavoriteView.as_view(), name='discover-course-toggle-favorite'),
    path('article/toggle-favorite/', KnowledgeArticleToggleFavoriteView.as_view(), name='discover-article-toggle-favorite'),
    path('post/toggle-like/', CommunityPostToggleLikeView.as_view(), name='discover-post-toggle-like'),
]
