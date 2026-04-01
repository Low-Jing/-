from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('discover', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChallengeJoin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('challenge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='joins', to='discover.challenge')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discover_challenge_joins', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-id']},
        ),
        migrations.CreateModel(
            name='TopicCourseFavorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='discover.topiccourse')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discover_course_favorites', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-id']},
        ),
        migrations.CreateModel(
            name='KnowledgeArticleFavorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='discover.knowledgearticle')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discover_article_favorites', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-id']},
        ),
        migrations.CreateModel(
            name='CommunityPostLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='discover.communitypost')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discover_post_likes', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-id']},
        ),
        migrations.AddConstraint(
            model_name='challengejoin',
            constraint=models.UniqueConstraint(fields=('user', 'challenge'), name='unique_user_challenge_join'),
        ),
        migrations.AddConstraint(
            model_name='topiccoursefavorite',
            constraint=models.UniqueConstraint(fields=('user', 'course'), name='unique_user_course_favorite'),
        ),
        migrations.AddConstraint(
            model_name='knowledgearticlefavorite',
            constraint=models.UniqueConstraint(fields=('user', 'article'), name='unique_user_article_favorite'),
        ),
        migrations.AddConstraint(
            model_name='communitypostlike',
            constraint=models.UniqueConstraint(fields=('user', 'post'), name='unique_user_post_like'),
        ),
    ]
