from django.contrib import admin
from .models import Challenge, TopicCourse, KnowledgeArticle, CommunityPost


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'tag', 'participant_count', 'days', 'sort_order', 'is_active')
    list_filter = ('tag', 'is_active')
    search_fields = ('title', 'description')


@admin.register(TopicCourse)
class TopicCourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'tags', 'sort_order', 'is_active')
    list_filter = ('level', 'is_active')
    search_fields = ('title', 'description', 'tags')


@admin.register(KnowledgeArticle)
class KnowledgeArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'read_minutes', 'sort_order', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'summary')


@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'like_count', 'comment_count', 'time_text', 'sort_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('nickname', 'content')
