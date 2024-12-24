# backend/urls.py

from django.urls import path
from . import views

app_name = 'backend'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # 后台主页
    path('users/', views.user_list, name='user_list'),  # 用户管理
    path('users/edit/<int:user_id>/', views.user_edit, name='user_edit'),  # 编辑用户
    path('users/delete/<int:user_id>/', views.user_delete, name='user_delete'),  # 删除用户
    path('tasks/', views.task_list, name='task_list'),  # 任务管理
    path('tasks/edit/<int:task_id>/', views.task_edit, name='task_edit'),  # 编辑任务
    path('tasks/delete/<int:task_id>/', views.task_delete, name='task_delete'),  # 删除任务
    path('analytics/', views.analytics, name='analytics'),  # 数据分析
]
