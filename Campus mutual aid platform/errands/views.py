from django.shortcuts import render
from rest_framework import generics
from .models import Task
from .serializers import TaskSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task, Review
from .models import Notification
from .serializers import NotificationSerializer
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserUpdateForm, ReviewForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Avg
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models import Q  # 用于复杂查询
from django.db.models import Exists, OuterRef
from django.utils import timezone
from .models import Review, Notification

# Create your views here.

class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]  # 需要用户登录

    def perform_create(self, serializer):
        # 自动将当前登录用户设置为 created_by
        serializer.save(created_by=self.request.user)

class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class TakeTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
            if task.assigned_to is None:  # 检查任务是否已被接单
                task.assigned_to = request.user
                task.status = "in_progress"
                task.save()
                return Response({"message": "Task successfully taken"}, status=status.HTTP_200_OK)
            return Response({"error": "Task already assigned"}, status=status.HTTP_400_BAD_REQUEST)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

#实现状态更新视图
class TaskStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)

            # 仅允许任务发布者或接单者更新状态
            if request.user == task.created_by or request.user == task.assigned_to:
                status_value = request.data.get("status")  # 避免变量名冲突
                if status_value in ["completed", "cancelled"]:
                    task.status = status_value
                    task.save()
                    return Response(
                        {"message": f"Task status updated to {status_value}"},
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {"error": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )
        except Task.DoesNotExist:
            return Response(
                {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
            )

#添加任务过滤功能
class TaskListView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'reward']

#创建视图用于提交评价，并确保任务已经完成：
class TaskReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
            if task.status != "completed":
                return Response({"error": "Task must be completed before reviewing"}, status=status.HTTP_400_BAD_REQUEST)

            # 检查用户是否有权限评价
            if request.user != task.created_by and request.user != task.assigned_to:
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

            # 确保一条任务只能有一次评价
            if hasattr(task, 'review'):
                return Response({"error": "Task already reviewed"}, status=status.HTTP_400_BAD_REQUEST)

            # 创建评价
            review = Review.objects.create(
                task=task,
                reviewed_by=request.user,
                reviewed_user=task.assigned_to if request.user == task.created_by else task.created_by,
                rating=request.data.get('rating'),
                comment=request.data.get('comment', '')
            )
            return Response({"message": "Review submitted successfully"}, status=status.HTTP_201_CREATED)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 返回当前用户的通知，按时间倒序排列
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


def login_view(request):
    """
    处理登录逻辑：
    - GET 请求时，返回登录页面
    - POST 请求时，根据表单的username,password验证用户
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)  # 登录成功，写入 session
            return redirect('index')  # 跳转到首页(或任务列表等), 'index'是下方示例首页的url别名
        else:
            # 登录失败，给出提示
            messages.error(request, '登录失败，用户名或密码错误。')
    # 无论是否失败，最终都要返回登录页面
    return render(request, 'errands/login.html')


@login_required
def index_view(request):
    """
    示例首页视图，只能在登录状态下访问
    """
    return render(request, 'errands/main.html')


def logout_view(request):
    """
    退出登录
    """
    logout(request)
    messages.success(request, '您已成功退出登录。')
    return redirect('login_page')


User = get_user_model()

def register_view(request):
    """
    处理用户注册逻辑：
    - GET 请求时：渲染 register.html
    - POST 请求时：验证表单并创建用户
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        student_id = request.POST.get('student_id', '').strip()
        phone = request.POST.get('phone', '').strip()

        # 1. 基础校验：是否填写必需信息
        if not username or not password or not password_confirm:
            messages.error(request, '用户名和密码不能为空')
            return render(request, 'errands/register.html')

        # 2. 检查两次密码是否一致
        if password != password_confirm:
            messages.error(request, '两次输入的密码不一致')
            return render(request, 'errands/register.html')

        # 3. 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在，请换个名字')
            return render(request, 'errands/register.html')

        # 4. 如果你的模型里 student_id 必须唯一，也要检查
        if student_id and User.objects.filter(student_id=student_id).exists():
            messages.error(request, '该学号/工号已被占用')
            return render(request, 'errands/register.html')

        # 5. 创建用户
        user = User(
            username=username,
            student_id=student_id or None,
            phone=phone or None,
        )
        user.password = make_password(password)  # 手动加密密码
        user.save()

        # 注册成功，给出提示并跳转到登录页
        messages.success(request, '注册成功，请登录！')
        return redirect('login_page')  # 在urls里配置 name='login_page'

    # 若是 GET 请求，或注册失败再次渲染：
    return render(request, 'errands/register.html')

@login_required
def main_page(request):
    query = request.GET.get('q', '')  # 获取搜索关键词

    # 标注当前用户是否已评价任务
    my_published_tasks = Task.objects.filter(created_by=request.user).annotate(
        has_reviewed=Exists(
            Review.objects.filter(task=OuterRef('pk'), reviewed_by=request.user)
        )
    )
    my_taken_tasks = Task.objects.filter(assigned_to=request.user).annotate(
        has_reviewed=Exists(
            Review.objects.filter(task=OuterRef('pk'), reviewed_by=request.user)
        )
    )

    if query:
        my_published_tasks = my_published_tasks.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
        my_taken_tasks = my_taken_tasks.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    return render(request, 'errands/main.html', {
        'my_published_tasks': my_published_tasks,
        'my_taken_tasks': my_taken_tasks,
        'query': query,  # 将搜索关键词返回模板
    })


@login_required
def take_tasks_view(request):
    # 如果是 POST, 并且是“发布悬赏”操作
    if request.method == 'POST' and request.POST.get('action') == 'create_task':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        reward_str = request.POST.get('reward', '0').strip()
        task_type = request.POST.get('task_type', 'other')

        if not title or not description or not reward_str:
            messages.error(request, "标题、描述和酬劳不能为空！")
        else:
            try:
                reward_value = float(reward_str)
            except ValueError:
                reward_value = 0.0

            Task.objects.create(
                title=title,
                description=description,
                reward=reward_value,
                status='pending',
                created_by=request.user,
                created_at=timezone.now(),
                type=task_type  # 在这里记录类型
            )
            messages.success(request, f"成功发布悬赏：{title}")

    query = request.GET.get('q', '')  # 获取搜索关键词
    # ---- 处理筛选（GET）----
    time_filter = request.GET.get('time_filter', '')
    reward_filter = request.GET.get('reward_filter', '')
    type_filter = request.GET.get('type_filter', '')

    queryset = Task.objects.filter(status='pending')

    # 搜索过滤：按标题或描述模糊匹配
    if query:
        queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))

    # 类型筛选
    if type_filter:
        queryset = queryset.filter(type=type_filter)

    # 酬劳筛选
    if reward_filter == 'low_to_high':
        queryset = queryset.order_by('reward')
    elif reward_filter == 'high_to_low':
        queryset = queryset.order_by('-reward')

    # 时间筛选
    if time_filter == 'newest':
        queryset = queryset.order_by('-created_at')
    elif time_filter == 'oldest':
        queryset = queryset.order_by('created_at')

    return render(request, 'errands/take_tasks.html', {
        'tasks': queryset,
        'query': query,  # 将搜索关键词返回模板
    })


@login_required
def ajax_take_task_view(request, task_id):
    """
    接取悬赏，返回JSON:
    { "status": "ok" } or {"error": "..."}
    """
    if request.method == 'POST':
        try:
            task = Task.objects.get(pk=task_id)
            if task.status != 'pending':
                return JsonResponse({"error": "任务已被接取或不在待接单状态"}, status=400)
            task.assigned_to = request.user
            task.status = 'in_progress'
            task.save()
            return JsonResponse({"status": "ok"}, status=200)
        except Task.DoesNotExist:
            return JsonResponse({"error": "任务不存在"}, status=404)
    return JsonResponse({"error": "Invalid method"}, status=405)


@login_required
def profile_view(request):
    """
    个人主页视图：显示和更新个人信息，查看评价和消息通知。
    """
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '个人信息更新成功！')
            return redirect('profile')
        else:
            messages.error(request, '更新失败，请检查表单内容。')
    else:
        form = UserUpdateForm(instance=request.user)

    # 获取用户的评价和消息通知
    my_reviews = Review.objects.filter(reviewed_user=request.user)
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # 计算平均评分
    average_rating = my_reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    average_rating = round(average_rating, 2)

    return render(request, 'errands/profile.html', {
        'form': form,
        'my_reviews': my_reviews,
        'notifications': notifications,
        'average_rating': average_rating,
    })


@login_required
def update_task_status(request, task_id):
    """
    更新任务状态视图：完成任务或取消任务。
    """
    if request.method == 'PATCH':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': '无效的JSON'}, status=400)

        new_status = data.get('status')
        if new_status not in ['completed', 'cancelled']:
            return JsonResponse({'error': '无效的状态'}, status=400)

        task = get_object_or_404(Task, id=task_id)

        # 权限检查
        if new_status == 'completed':
            if task.assigned_to != request.user:
                return JsonResponse({'error': '你没有权限完成这个任务'}, status=403)
        elif new_status == 'cancelled':
            if task.created_by != request.user:
                return JsonResponse({'error': '你没有权限取消这个任务'}, status=403)

        task.status = new_status
        task.save()
        return JsonResponse({'message': '任务状态已更新'})
    else:
        return JsonResponse({'error': '无效的请求方法'}, status=405)

@login_required
@require_POST
def submit_review(request, task_id):
    """
    提交评价视图：用户对已完成的任务进行评分和评论。
    """
    task = get_object_or_404(Task, id=task_id)

    # 权限检查：只能对已完成的任务进行评价
    if task.status != 'completed':
        return JsonResponse({'error': '只有完成的任务才能进行评价'}, status=400)

    # 确认当前用户是任务的相关方
    if task.created_by != request.user and task.assigned_to != request.user:
        return JsonResponse({'error': '你没有权限评价这个任务'}, status=403)

    # 确认用户尚未评价过此任务
    existing_review = Review.objects.filter(task=task, reviewed_by=request.user).first()
    if existing_review:
        return JsonResponse({'error': '你已经评价过这个任务'}, status=400)

    try:
        data = json.loads(request.body)
        rating = data.get('rating')
        comment = data.get('comment')

        if not rating or not comment:
            return JsonResponse({'error': '评分和评论不能为空'}, status=400)

        # 验证评分范围
        rating = int(rating)
        if rating < 1 or rating > 5:
            return JsonResponse({'error': '评分必须在1到5之间'}, status=400)

        # 确定被评价的用户
        if task.created_by == request.user:
            reviewed_user = task.assigned_to
        else:
            reviewed_user = task.created_by

        # 确保被评价的用户存在
        if not reviewed_user:
            return JsonResponse({'error': '被评价的用户不存在'}, status=400)

        # 创建评价
        review = Review.objects.create(
            task=task,
            reviewed_by=request.user,
            reviewed_user=reviewed_user,
            rating=rating,
            comment=comment
        )

        # 创建通知给被评价方
        Notification.objects.create(
            user=review.reviewed_user,
            message=f"你被用户“{review.reviewed_by.username}”评价了任务“{task.title}”：评分 {review.rating} / 5，评论：“{review.comment}”。"
        )

        return JsonResponse({'message': '评价已提交'})
    except (ValueError, TypeError):
        return JsonResponse({'error': '无效的数据'}, status=400)

# errands/views.py

from django.shortcuts import render

def home(request):
    return render(request, 'errands/index.html')
