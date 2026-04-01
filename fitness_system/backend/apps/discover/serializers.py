from rest_framework import serializers
from .models import Challenge, TopicCourse, KnowledgeArticle, CommunityPost


class ChallengeSerializer(serializers.ModelSerializer):
    people_text = serializers.SerializerMethodField()
    joined = serializers.SerializerMethodField()
    total_participants = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = [
            'id', 'title', 'description', 'tag', 'participant_count', 'total_participants',
            'people_text', 'days', 'theme_color', 'joined'
        ]

    def get_total_participants(self, obj):
        return obj.participant_count + obj.joins.count()

    def get_people_text(self, obj):
        return f'{self.get_total_participants(obj):,}'

    def get_joined(self, obj):
        joined_ids = self.context.get('joined_ids', set())
        return obj.id in joined_ids


class TopicCourseSerializer(serializers.ModelSerializer):
    tag_list = serializers.SerializerMethodField()
    favorited = serializers.SerializerMethodField()

    class Meta:
        model = TopicCourse
        fields = ['id', 'title', 'description', 'level', 'tags', 'tag_list', 'favorited']

    def get_tag_list(self, obj):
        if not obj.tags:
            return []
        return [item.strip() for item in obj.tags.replace('、', '，').split('，') if item.strip()]

    def get_favorited(self, obj):
        favorite_ids = self.context.get('course_favorite_ids', set())
        return obj.id in favorite_ids


class KnowledgeArticleSerializer(serializers.ModelSerializer):
    favorited = serializers.SerializerMethodField()

    class Meta:
        model = KnowledgeArticle
        fields = ['id', 'title', 'summary', 'category', 'read_minutes', 'favorited']

    def get_favorited(self, obj):
        favorite_ids = self.context.get('article_favorite_ids', set())
        return obj.id in favorite_ids


class CommunityPostSerializer(serializers.ModelSerializer):
    liked = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()

    class Meta:
        model = CommunityPost
        fields = ['id', 'nickname', 'content', 'like_count', 'total_likes', 'liked', 'comment_count', 'time_text']

    def get_total_likes(self, obj):
        return obj.like_count + obj.likes.count()

    def get_liked(self, obj):
        liked_ids = self.context.get('post_liked_ids', set())
        return obj.id in liked_ids
