from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.tasks.models import TaskStatus
from .services import send_task_completion_notification, send_notification

User = get_user_model()

@receiver(post_save, sender=TaskStatus)
def task_status_changed(sender, instance, created, **kwargs):
    if not created and instance.status in ['done', 'not_done']:
        send_task_completion_notification(
            task=instance.task,
            user=instance.user,
            status=instance.status
        )

@receiver(post_save, sender=User)
def user_joined_notification(sender, instance, created, **kwargs):
    if created and instance.is_active:
        admins = User.objects.filter(role='admin', is_active=True)
        for admin in admins:
            send_notification(
                user=admin,
                title="New Member Joined",
                message=f"{instance.get_full_name()} has joined the group!",
                notification_type='group_update'
            )
