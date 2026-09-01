import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collaborative_todo.settings')

app = Celery('collaborative_todo')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'generate-daily-group-tasks': {
        'task': 'apps.tasks.tasks.generate_daily_group_tasks',
        'schedule': crontab(hour=9, minute=0),  # Run at 9 AM daily
    },
    'send-daily-reminders': {
        'task': 'apps.notifications.tasks.send_daily_reminders',
        'schedule': crontab(hour=18, minute=0),  # Run at 6 PM daily
    },
    'cleanup-old-notifications': {
        'task': 'apps.notifications.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=0, minute=0),  # Run at midnight daily
    },
}
