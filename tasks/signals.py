from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Task, TaskStatus

User = get_user_model()

@receiver(post_save, sender=Task)
def create_task_statuses(sender, instance, created, **kwargs):
    """Create TaskStatus for all users when a group task is created"""
    if created and instance.type == 'group':
        # Get all active users
        users = User.objects.filter(is_active=True)
        for user in users:
            TaskStatus.objects.get_or_create(
                task=instance,
                user=user,
                defaults={'status': 'pending'}
            )

@receiver(pre_delete, sender=Task)
def cleanup_task_statuses(sender, instance, **kwargs):
    """Delete all related task statuses when a task is deleted"""
    TaskStatus.objects.filter(task=instance).delete()
