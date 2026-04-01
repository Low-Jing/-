from django.contrib.auth.models import User
from django.db import models


class Challenge(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    tag = models.CharField(max_length=30, default='挑战')
    participant_count = models.PositiveIntegerField(default=0)
    days = models.PositiveIntegerField(default=7)
    theme_color = models.CharField(max_length=120, default='linear-gradient(135deg,#1d4ed8 0%,#06b6d4 100%)')
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', '-id']

    def __str__(self):
        return self.title


class TopicCourse(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    level = models.CharField(max_length=20, default='入门')
    tags = models.CharField(max_length=120, blank=True, help_text='多个标签用中文逗号分隔')
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', '-id']

    def __str__(self):
        return self.title


class KnowledgeArticle(models.Model):
    title = models.CharField(max_length=120)
    summary = models.TextField(blank=True)
    category = models.CharField(max_length=30, default='知识')
    read_minutes = models.PositiveIntegerField(default=5)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', '-id']

    def __str__(self):
        return self.title


class CommunityPost(models.Model):
    nickname = models.CharField(max_length=50)
    content = models.TextField()
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    time_text = models.CharField(max_length=30, default='今天')
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', '-id']

    def __str__(self):
        return f'{self.nickname}-{self.content[:10]}'


class ChallengeJoin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discover_challenge_joins')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='joins')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'challenge'], name='unique_user_challenge_join')
        ]
        ordering = ['-id']


class TopicCourseFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discover_course_favorites')
    course = models.ForeignKey(TopicCourse, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'course'], name='unique_user_course_favorite')
        ]
        ordering = ['-id']


class KnowledgeArticleFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discover_article_favorites')
    article = models.ForeignKey(KnowledgeArticle, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'article'], name='unique_user_article_favorite')
        ]
        ordering = ['-id']


class CommunityPostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discover_post_likes')
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_user_post_like')
        ]
        ordering = ['-id']
