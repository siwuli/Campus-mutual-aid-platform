# Campus-mutual-aid-platform
大三时的期末项目，做的是一个基于 Django + Bootstrap 的校园跑腿、悬赏和管理平台，旨在帮助学生快速发布需求、接取任务，并提供后台管理功能进行用户和任务的维护与数据分析。

## 功能概述
### 前台功能：
-注册/登录：支持自定义用户模型，具有学号/工号、电话等信息。
-发布悬赏：填写标题、描述、酬劳、类型与状态等信息并发布。
-接取悬赏：学生可浏览并接取待接单的任务，完成后获取酬劳。
-评价系统：双方可对任务完成情况进行评分与评价。
-消息通知：任务状态改变或收到评价后，系统自动发送通知。
### 后台管理（管理员权限）：
-仪表盘：显示用户数、任务数、已完成任务等概览信息。
-用户管理：查看、搜索、编辑、删除用户。
-任务管理：查看、搜索/过滤、编辑、删除任务。
-数据分析：任务状态分布图、用户接单数量图，查看用户/任务/评分等统计数据。

## 技术栈
-后端：Django 3.x/4.x + Django REST Framework（可选）
-数据库：SQLite（开发环境），可轻松切换至 MySQL/PostgreSQL
-前端：Bootstrap 5 + jQuery/JavaScript + Chart.js（后台数据可视化）

## 迁移数据库并创建超级用户：
```
python manage.py makemigrations
```
```
python manage.py migrate
```
```
python manage.py createsuperuser
```

## 运行开发服务器：
```
python manage.py runserver
```
打开浏览器访问 http://127.0.0.1:8000/ 即可查看前台页面，访问 http://127.0.0.1:8000/backend/ 进入后台管理页面（需管理员账号登录）
