from django.core.management.base import BaseCommand
from apps.discover.models import Challenge, TopicCourse, KnowledgeArticle, CommunityPost


class Command(BaseCommand):
    help = '初始化发现页内容数据'

    def handle(self, *args, **options):
        Challenge.objects.all().delete()
        TopicCourse.objects.all().delete()
        KnowledgeArticle.objects.all().delete()
        CommunityPost.objects.all().delete()

        Challenge.objects.bulk_create([
            Challenge(title='7天燃脂快走挑战', description='每日 30 分钟快走或慢跑，配合饮食建议形成更完整闭环。', tag='热门', participant_count=1268, days=7, theme_color='linear-gradient(135deg,#1d4ed8 0%,#06b6d4 100%)', sort_order=1),
            Challenge(title='14天高蛋白饮食打卡', description='帮助用户建立高蛋白、低油轻食的饮食习惯。', tag='饮食', participant_count=936, days=14, theme_color='linear-gradient(135deg,#059669 0%,#14b8a6 100%)', sort_order=2),
            Challenge(title='办公室体态修复季', description='围绕肩颈放松、核心激活和下背稳定设计轻训练。', tag='体态', participant_count=603, days=21, theme_color='linear-gradient(135deg,#7c3aed 0%,#ec4899 100%)', sort_order=3),
        ])

        TopicCourse.objects.bulk_create([
            TopicCourse(title='新手减脂启动课', description='把热量缺口、基础有氧和轻力量结合起来，适合冷启动用户。', level='入门', tags='减脂，跑步，饮食', sort_order=1),
            TopicCourse(title='增肌训练拆解计划', description='围绕上肢、下肢和核心进行分化训练，更利于展示内容丰富度。', level='进阶', tags='增肌，力量，蛋白质', sort_order=2),
            TopicCourse(title='女性健康塑形专题', description='围绕塑形、恢复和周期训练做差异化内容。', level='精选', tags='塑形，恢复，周期', sort_order=3),
        ])

        KnowledgeArticle.objects.bulk_create([
            KnowledgeArticle(title='为什么冷启动更适合内容推荐', summary='因为早期用户少、交互稀疏，内容标签比行为相似度更稳定。', category='推荐', read_minutes=4, sort_order=1),
            KnowledgeArticle(title='如何把反馈数据接入协同过滤', summary='可把打卡、点赞、收藏和复练次数转成用户-项目交互矩阵。', category='算法', read_minutes=6, sort_order=2),
            KnowledgeArticle(title='如何让运动类毕设更像产品', summary='关键是持续使用链路：推荐→执行→打卡→反馈→再推荐。', category='产品', read_minutes=5, sort_order=3),
        ])

        CommunityPost.objects.bulk_create([
            CommunityPost(nickname='晨跑研究社', content='今天完成 5km 慢跑，计划页推荐的跑步强度很适合我。', like_count=82, comment_count=14, time_text='10 分钟前', sort_order=1),
            CommunityPost(nickname='轻食打卡组', content='用了系统推荐的鸡胸肉藜麦沙拉，口味清淡也比较容易坚持。', like_count=67, comment_count=8, time_text='1 小时前', sort_order=2),
            CommunityPost(nickname='居家训练营', content='HIIT 20 分钟打卡成功，希望后面能接入收藏动作功能。', like_count=49, comment_count=12, time_text='今天', sort_order=3),
        ])

        self.stdout.write(self.style.SUCCESS('发现页内容初始化完成'))
