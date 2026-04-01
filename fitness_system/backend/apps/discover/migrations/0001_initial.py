from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('tag', models.CharField(default='挑战', max_length=30)),
                ('participant_count', models.PositiveIntegerField(default=0)),
                ('days', models.PositiveIntegerField(default=7)),
                ('theme_color', models.CharField(default='linear-gradient(135deg,#1d4ed8 0%,#06b6d4 100%)', max_length=120)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['sort_order', '-id']},
        ),
        migrations.CreateModel(
            name='CommunityPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.CharField(max_length=50)),
                ('content', models.TextField()),
                ('like_count', models.PositiveIntegerField(default=0)),
                ('comment_count', models.PositiveIntegerField(default=0)),
                ('time_text', models.CharField(default='今天', max_length=30)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['sort_order', '-id']},
        ),
        migrations.CreateModel(
            name='KnowledgeArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('summary', models.TextField(blank=True)),
                ('category', models.CharField(default='知识', max_length=30)),
                ('read_minutes', models.PositiveIntegerField(default=5)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['sort_order', '-id']},
        ),
        migrations.CreateModel(
            name='TopicCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('level', models.CharField(default='入门', max_length=20)),
                ('tags', models.CharField(blank=True, help_text='多个标签用中文逗号分隔', max_length=120)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['sort_order', '-id']},
        ),
    ]
