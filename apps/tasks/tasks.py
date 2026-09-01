from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from .models import Task, TaskStatus

User = get_user_model()

@shared_task
def generate_daily_group_tasks():
    today = timezone.now().date()
    
    if Task.objects.filter(type='group', assigned_date=today).exists():
        return "Tasks already generated for today"
    
    default_tasks = [
        "Morning Stand-up Meeting",
        "Daily Progress Update",
        "Review Team Tasks",
        "Complete Daily Goals",
        "End of Day Summary"
    ]
    
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
def cleanup_old_tasks():
    cutoff_date = timezone.now().date() - timedelta(days=30)
    old_tasks = Task.objects.filter(
        type='group',
        assigned_date__lt=cutoff_date,
        is_active=True
    )
    
    count = old_tasks.count()
    old_tasks.update(is_active=False)
    
    return f"Archived {count} old tasks"
