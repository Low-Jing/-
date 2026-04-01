# 健康体重管理健身系统后端起步版

这是一个适合本科毕业设计入门的 Django + DRF 后端起步工程。

## 1. 建议软件
- Python 3.12
- VS Code
- MySQL 8（后续切换）
- Postman（接口测试，可选）

## 2. 创建虚拟环境并安装依赖（Windows PowerShell）
```powershell
python -m venv .venv
.\.venv\Scriptsctivate
pip install -r requirements.txt
```

## 3. 初始化数据库
默认使用 SQLite，先保证项目能跑起来。
```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data
python manage.py runserver
```

浏览器打开：
- 后台管理：http://127.0.0.1:8000/admin/
- API 根路径：http://127.0.0.1:8000/api/

## 4. 当前已实现接口
- POST `/api/users/register/` 用户注册
- GET `/api/users/profiles/` 用户档案列表
- GET/POST `/api/health/records/` 健康记录
- GET `/api/plans/exercises/` 动作库
- GET `/api/plans/foods/` 食谱库
- POST `/api/plans/recommend/` 生成推荐计划
- GET/POST `/api/plans/checkins/` 打卡记录

## 5. 切换到 MySQL
先安装 MySQL 并创建数据库 `fitness_system`。
然后把 `fitness_backend/settings.py` 中 DATABASES 的 SQLite 配置替换为注释中的 MySQL 配置即可。
