from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from .models import Task, TaskStatus

User = get_user_model()

@shared_task
def generate_daily_group_tasks():
    """Generate daily group tasks for all members"""
    today = timezone.now().date()
    
    # Check if tasks already generated for today
    if Task.objects.filter(type='group', assigned_date=today).exists():
        return "Tasks already generated for today"
    
    # Default daily tasks (can be customized)
    default_tasks = [
        "Morning Stand-up Meeting",
        "Daily Progress Update",
        "Review Team Tasks",
        "Complete Daily Goals",
        "End of Day Summary"
    ]
    
    # Create tasks
    admin_users = User.objects.filter(role='admin', is_active=True)
    if not admin_users.exists():
        return "No admin user found to create tasks"
    
    admin_user = admin_users.first()
    
    created_count = 0
    for task_title in default_tasks:
        task = Task.objects.create(
            title=task_title,
            description=f"Daily {task_title.lower()} for all team members",
            type='group',
            created_by=admin_user,
            assigned_date=today
        )
        
        # Create statuses for all active users
        users = User.objects.filter(is_active=True)
        for user in users:
            TaskStatus.objects.create(
                task=task,
                user=user,
                status='pending'
            )
        created_count += 1
    
    return f"Created {created_count} daily group tasks for {today}"

@shared_task
def check_task_completion_reminders():
    """Check for incomplete tasks and send reminders"""
    today = timezone.now().date()
    
    # Get incomplete tasks from yesterday
    yesterday = today - timedelta(days=1)
    incomplete_tasks = TaskStatus.objects.filter(
        task__type='group',
        task__assigned_date=yesterday,
        status__in=['pending', 'not_done']
    ).select_related('task', 'user')
    
    reminder_count = 0
    for task_status in incomplete_tasks:
        # Send reminder (will be handled by notifications app)
        from apps.notifications.services import send_task_reminder
        send_task_reminder(
            task_status.user,
            task_status.task,
            task_status
        )
        reminder_count += 1
    
    return f"Sent {reminder_count} reminders for incomplete tasks"

@shared_task
def cleanup_old_tasks():
    """Archive or delete old tasks"""
    # Archive tasks older than 30 days
    cutoff_date = timezone.now().date() - timedelta(days=30)
    old_tasks = Task.objects.filter(
        type='group',
        assigned_date__lt=cutoff_date,
        is_active=True
    )
    
    count = old_tasks.count()
    old_tasks.update(is_active=False)
    
    return f"Archived {count} old tasks"
