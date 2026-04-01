from django.core.management.base import BaseCommand
from apps.plans.models import Exercise, Food


class Command(BaseCommand):
    help = '初始化动作库和食谱库测试数据'

    def handle(self, *args, **options):
        exercise_data = [
            {'title': '跑步', 'category': '有氧', 'fit_goal': 'lose_weight', 'duration_minutes': 30, 'calories': 280, 'difficulty': '中等', 'description': '适合减脂用户'},
            {'title': '快走', 'category': '有氧', 'fit_goal': 'lose_weight', 'duration_minutes': 40, 'calories': 220, 'difficulty': '简单', 'description': '适合初学者'},
            {'title': '哑铃训练', 'category': '力量', 'fit_goal': 'gain_muscle', 'duration_minutes': 35, 'calories': 180, 'difficulty': '中等', 'description': '适合增肌塑形'},
            {'title': '深蹲训练', 'category': '力量', 'fit_goal': 'gain_muscle', 'duration_minutes': 25, 'calories': 160, 'difficulty': '中等', 'description': '提升下肢力量'},
            {'title': '瑜伽拉伸', 'category': '柔韧', 'fit_goal': 'maintain', 'duration_minutes': 20, 'calories': 90, 'difficulty': '简单', 'description': '适合日常健康维持'},
        ]

        food_data = [
            {'name': '鸡胸肉沙拉', 'fit_goal': 'lose_weight', 'calories': 320, 'protein': 32, 'preference_tag': '清淡', 'description': '高蛋白低脂'},
            {'name': '全麦三明治', 'fit_goal': 'lose_weight', 'calories': 300, 'protein': 18, 'preference_tag': '便捷', 'description': '适合上班族'},
            {'name': '牛肉饭', 'fit_goal': 'gain_muscle', 'calories': 520, 'protein': 35, 'preference_tag': '高蛋白', 'description': '适合增肌'},
            {'name': '三文鱼意面', 'fit_goal': 'gain_muscle', 'calories': 560, 'protein': 34, 'preference_tag': '高蛋白', 'description': '高质量蛋白来源'},
            {'name': '蔬菜豆腐汤', 'fit_goal': 'maintain', 'calories': 260, 'protein': 16, 'preference_tag': '清淡', 'description': '日常维持健康'},
        ]

        for item in exercise_data:
            Exercise.objects.get_or_create(title=item['title'], defaults=item)

        for item in food_data:
            Food.objects.get_or_create(name=item['name'], defaults=item)

        self.stdout.write(self.style.SUCCESS('测试数据初始化完成'))
