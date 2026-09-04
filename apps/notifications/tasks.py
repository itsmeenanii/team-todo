from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from .models import Reminder
from .services import send_reminder

User = get_user_model()

@shared_task
def send_daily_reminders():
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    from apps.tasks.models import TaskStatus
    
    incomplete_tasks = TaskStatus.objects.filter(
        task__type='group',
        task__assigned_date=yesterday,
        status__in=['pending', 'not_done']
    ).select_related('task', 'user')
    
    reminder_count = 0
    for task_status in incomplete_tasks:
        # Check if reminder already sent for this task
        existing_reminder = Reminder.objects.filter(
            task=task_status.task,
            receiver=task_status.user,
            created_at__date=today
        ).exists()
        
        if not existing_reminder:
            # Get admin users as senders
            admins = User.objects.filter(role='admin', is_active=True)
            if admins.exists():
                reminder = Reminder.objects.create(
                    sender=admins.first(),
                    receiver=task_status.user,
                    task=task_status.task,
                    message=f"Daily reminder: Please complete your task: {task_status.task.title}",
                    reminder_type='email'
                )
                send_reminder(reminder)
                reminder_count += 1
    
    return f"Sent {reminder_count} daily reminders"
