from django.core.management.base import BaseCommand
from apps.plans.models import Exercise, Food


EXERCISES = [
    {'title': '燃脂跑步', 'category': '有氧', 'fit_goal': 'lose_weight', 'duration_minutes': 30, 'calories': 280, 'difficulty': '中等', 'description': '适合减脂阶段的基础有氧训练。'},
    {'title': '快走爬坡', 'category': '有氧', 'fit_goal': 'lose_weight', 'duration_minutes': 35, 'calories': 240, 'difficulty': '低', 'description': '适合新手和体重管理初期。'},
    {'title': '自重 HIIT 循环', 'category': 'HIIT', 'fit_goal': 'lose_weight', 'duration_minutes': 20, 'calories': 230, 'difficulty': '高', 'description': '适合时间较短但想提升燃脂效率的用户。'},
    {'title': '上肢力量入门', 'category': '力量', 'fit_goal': 'gain_muscle', 'duration_minutes': 25, 'calories': 180, 'difficulty': '中等', 'description': '适合增肌初期用户。'},
    {'title': '下肢抗阻训练', 'category': '力量', 'fit_goal': 'gain_muscle', 'duration_minutes': 35, 'calories': 220, 'difficulty': '中等', 'description': '通过深蹲、弓步等动作提升下肢力量。'},
    {'title': '核心稳定训练', 'category': '核心', 'fit_goal': 'maintain', 'duration_minutes': 20, 'calories': 120, 'difficulty': '低', 'description': '适合体态改善与日常健康保持。'},
    {'title': '拉伸放松瑜伽', 'category': '瑜伽', 'fit_goal': 'maintain', 'duration_minutes': 25, 'calories': 90, 'difficulty': '低', 'description': '改善柔韧性与恢复效率。'},
    {'title': '晚间舒缓普拉提', 'category': '普拉提', 'fit_goal': 'maintain', 'duration_minutes': 25, 'calories': 100, 'difficulty': '低', 'description': '适合上班族和居家训练。'},
]

FOODS = [
    {'name': '鸡胸肉藜麦沙拉', 'fit_goal': 'lose_weight', 'calories': 320, 'protein': 32, 'preference_tag': '高蛋白', 'description': '清淡低油，适合减脂期。'},
    {'name': '牛肉全麦能量碗', 'fit_goal': 'gain_muscle', 'calories': 430, 'protein': 35, 'preference_tag': '增肌', 'description': '适合训练后补充优质蛋白。'},
    {'name': '酸奶水果坚果杯', 'fit_goal': 'maintain', 'calories': 260, 'protein': 18, 'preference_tag': '轻食', 'description': '适合作为早餐或加餐。'},
    {'name': '清蒸鱼配杂粮饭', 'fit_goal': 'lose_weight', 'calories': 360, 'protein': 30, 'preference_tag': '清淡', 'description': '低油高蛋白。'},
    {'name': '番茄牛腩饭', 'fit_goal': 'gain_muscle', 'calories': 480, 'protein': 34, 'preference_tag': '高蛋白', 'description': '适合增肌用户。'},
    {'name': '蔬菜鸡蛋三明治', 'fit_goal': 'maintain', 'calories': 290, 'protein': 16, 'preference_tag': '早餐', 'description': '方便快捷，适合通勤场景。'},
]


class Command(BaseCommand):
    help = '初始化更丰富的动作库和饮食库演示数据'

    def handle(self, *args, **options):
        for item in EXERCISES:
            Exercise.objects.update_or_create(title=item['title'], defaults=item)
        for item in FOODS:
            Food.objects.update_or_create(name=item['name'], defaults=item)
        self.stdout.write(self.style.SUCCESS('丰富演示数据初始化完成'))
