# errands/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps


@receiver(post_save, sender='errands.Task')  # 用字符串表示模型路径
def create_notification(sender, instance, **kwargs):
    Notification = apps.get_model('errands', 'Notification')  # 延迟加载 Notification

    # 任务被接单
    if instance.status == "in_progress" and instance.assigned_to:
        Notification.objects.create(
            user=instance.created_by,
            message=f"你的任务“{instance.title}”已被{instance.assigned_to.username}接取。"
        )

    # 任务完成
    if instance.status == "completed":
        Notification.objects.create(
            user=instance.created_by,
            message=f"你的任务“{instance.title}”已完成！"
        )
        if instance.assigned_to:
            Notification.objects.create(
                user=instance.assigned_to,
                message=f"你接取的任务“{instance.title}”已被标记为完成。"
            )

    # 任务取消
    if instance.status == "cancelled":
        if instance.assigned_to:  # 仅在任务已被接取时发送通知
            Notification.objects.create(
                user=instance.assigned_to,
                message=f"你接取的任务“{instance.title}”已被取消。"
            )
        # 如果需要，可以在任务未被接取时发送其他通知
        # 例如通知创建者任务已取消（如果有其他逻辑需要）
        # else:
        #     Notification.objects.create(
        #         user=instance.created_by,
        #         message=f"你的任务“{instance.title}”已被取消。"
        #     )
