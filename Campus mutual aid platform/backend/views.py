# backend/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from errands.models import Task, Review, Notification
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import models
from django.db.models import Count, Avg
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db.models import Q

User = get_user_model() # 获取自定义用户模型

#确保只有管理员用户可以访问后台管理界面。可以使用 user_passes_test 装饰器。
def admin_required(view_func):
    """
    装饰器：确保用户是管理员（is_staff=True）。
    如果未登录，重定向到登录页面；
    如果已登录但不是管理员，返回403错误。
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login_page')  # 未登录，重定向到登录页面
        if not request.user.is_staff:
            raise PermissionDenied  # 已登录但非管理员，返回403错误
        return view_func(request, *args, **kwargs)
    return _wrapped_view

#创建后台主页视图
@login_required
@admin_required
def dashboard(request):
    total_users = User.objects.count()
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status='completed').count()
    average_reward = Task.objects.aggregate(avg_reward=Avg('reward'))['avg_reward'] or 0

    context = {
        'total_users': total_users,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'average_reward': average_reward,
    }
    return render(request, 'backend/dashboard.html', context)

#用户列表视图
@login_required
@admin_required
def user_list(request):
    search_query = request.GET.get('search', '')
    if search_query:
        users = User.objects.filter(username__icontains=search_query) | User.objects.filter(email__icontains=search_query)
    else:
        users = User.objects.all()

    paginator = Paginator(users, 10)  # 每页显示10个用户
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'backend/user_list.html', {'page_obj': page_obj, 'search_query': search_query})

#编辑用户视图
@login_required
@admin_required
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        is_staff = request.POST.get('is_staff') == 'on'
        is_active = request.POST.get('is_active') == 'on'

        user.username = username
        user.email = email
        user.is_staff = is_staff
        user.is_active = is_active
        user.save()

        messages.success(request, '用户信息已更新。')
        return redirect('backend:user_list')

    return render(request, 'backend/user_edit.html', {'user': user})

#删除用户视图
@login_required
@admin_required
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, '用户已删除。')
        return redirect('backend:user_list')
    return render(request, 'backend/user_delete_confirm.html', {'user': user})

#任务列表视图
@login_required
@admin_required
def task_list(request):
    # 获取搜索和过滤参数
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()

    # 基础查询集
    tasks = Task.objects.all()

    # 如果有搜索关键词，则在任务的标题和描述中进行模糊搜索
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    # 如果有状态过滤，则进一步筛选
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    # 分页
    paginator = Paginator(tasks, 10)  # 每页显示10个任务
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 为模板提供状态选项（如果需要在前端生成 <select> ）
    STATUS_CHOICES = [
        ('pending', '待接取'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'STATUS_CHOICES': STATUS_CHOICES,
    }
    return render(request, 'backend/task_list.html', context)

#编辑任务视图
@login_required
@admin_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    users = User.objects.filter(is_staff=False, is_active=True)  # 可分配的用户

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        reward = request.POST.get('reward')
        status = request.POST.get('status')
        assigned_to_id = request.POST.get('assigned_to')

        task.title = title
        task.description = description
        task.reward = reward
        task.status = status
        if assigned_to_id:
            task.assigned_to = User.objects.get(id=assigned_to_id)
        else:
            task.assigned_to = None
        task.save()

        messages.success(request, '任务信息已更新。')
        return redirect('backend:task_list')

    return render(request, 'backend/task_edit.html', {'task': task, 'users': users})

#删除任务视图
@login_required
@admin_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.delete()
        messages.success(request, '任务已删除。')
        return redirect('backend:task_list')
    return render(request, 'backend/task_delete_confirm.html', {'task': task})

#创建数据分析视图
@login_required
@admin_required
def analytics(request):
    # 用户统计
    user_stats = User.objects.aggregate(total_users=Count('id'), active_users=Count('id', filter=models.Q(is_active=True)))

    # 任务统计
    task_stats = Task.objects.aggregate(
        total_tasks=Count('id'),
        completed_tasks=Count('id', filter=models.Q(status='completed')),
        pending_tasks=Count('id', filter=models.Q(status='pending')),
        in_progress_tasks=Count('id', filter=models.Q(status='in_progress')),
        cancelled_tasks=Count('id', filter=models.Q(status='cancelled')),
        average_reward=Avg('reward')
    )

    # 评分统计
    rating_stats = Review.objects.aggregate(
        average_rating=Avg('rating'),
        total_reviews=Count('id')
    )

    # 数据可视化数据
    tasks_per_status = Task.objects.values('status').annotate(count=Count('id'))
    users_per_task = Task.objects.values('assigned_to__username').annotate(count=Count('id')).order_by('-count')[:5]

    context = {
        'user_stats': user_stats,
        'task_stats': task_stats,
        'rating_stats': rating_stats,
        'tasks_per_status': list(tasks_per_status),
        'users_per_task': list(users_per_task),
    }
    return render(request, 'backend/analytics.html', context)