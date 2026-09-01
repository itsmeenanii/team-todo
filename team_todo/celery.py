import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collaborative_todo.settings')

# Check if we're running on Vercel
IS_VERCEL = os.environ.get('VERCEL', False)

# Only initialize Celery if not on Vercel
if not IS_VERCEL:
    app = Celery('collaborative_todo')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks()

    app.conf.beat_schedule = {
        'generate-daily-group-tasks': {
            'task': 'apps.tasks.tasks.generate_daily_group_tasks',
            'schedule': crontab(hour=9, minute=0),
        },
        'send-daily-reminders': {
            'task': 'apps.notifications.tasks.send_daily_reminders',
            'schedule': crontab(hour=18, minute=0),
        },
        'cleanup-old-notifications': {
            'task': 'apps.notifications.tasks.cleanup_old_notifications',
            'schedule': crontab(hour=0, minute=0),
        },
    }
else:
    # Dummy Celery app for Vercel
    app = Celery('collaborative_todo')
    app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )
