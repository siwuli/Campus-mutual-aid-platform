from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps

class User(AbstractUser):
    # 其他自定义字段
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', null=True, blank=True)

    def __str__(self):
        return self.username

# Create your models here.

# errands/models.py

# errands/models.py

from django.db import models
from django.conf import settings

class Task(models.Model):
    TASK_TYPE_CHOICES = [
        ('express', '快递'),
        ('takeaway', '外卖'),
        ('purchase', '代购'),
        ('other', '其他'),
    ]

    STATUS_CHOICES = [
        ('pending', '待接取'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    reward = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='tasks_created'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_assigned'
    )
    type = models.CharField(
        max_length=20,
        choices=TASK_TYPE_CHOICES,
        default='other'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Review(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='reviews')
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    reviewed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1-5 分
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('task', 'reviewed_by')  # 确保每个用户只能对每个任务评价一次

    def __str__(self):
        return f"{self.reviewed_by} reviewed {self.reviewed_user} for '{self.task.title}'"

class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()  # 通知内容
    is_read = models.BooleanField(default=False)  # 是否已读
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()  # 通知内容
    is_read = models.BooleanField(default=False)  # 是否已读
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

