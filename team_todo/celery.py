import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'team_todo.settings')

app = Celery('team_todo')
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
    'cleanup-old-tasks': {
        'task': 'apps.tasks.tasks.cleanup_old_tasks',
        'schedule': crontab(hour=0, minute=0),
    },
}
