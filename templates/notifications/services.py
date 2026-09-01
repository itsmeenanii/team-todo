import logging
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from firebase_admin import messaging, credentials, initialize_app
import firebase_admin
import os
from twilio.rest import Client

logger = logging.getLogger(__name__)

# Initialize Firebase (only once)
try:
    if not firebase_admin._apps:
        if settings.FIREBASE_CREDENTIALS:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
            initialize_app(cred)
except Exception as e:
    logger.error(f"Failed to initialize Firebase: {e}")

def send_reminder(reminder):
    """Send a reminder via the specified channel"""
    try:
        if reminder.reminder_type == 'email':
            send_email_reminder(reminder)
        elif reminder.reminder_type == 'push':
            send_push_reminder(reminder)
        elif reminder.reminder_type == 'sms':
            send_sms_reminder(reminder)
        else:
            logger.error(f"Unknown reminder type: {reminder.reminder_type}")
            return False
        
        reminder.mark_sent()
        return True
    except Exception as e:
        logger.error(f"Failed to send reminder {reminder.id}: {e}")
        reminder.mark_failed()
        return False

def send_email_reminder(reminder):
    """Send email reminder"""
    subject = f"Reminder: Complete your task - {reminder.task.title}"
    message = render_to_string('notifications/reminder_email.html', {
        'receiver_name': reminder.receiver.get_full_name(),
        'task_title': reminder.task.title,
        'task_description': reminder.task.description,
        'sender_name': reminder.sender.get_full_name(),
        'message': reminder.message,
        'task_url': f"{settings.BASE_URL}/tasks/{reminder.task.id}/",
    })
    
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[reminder.receiver.email],
    )
    email.content_subtype = "html"
    email.send()

def send_push_reminder(reminder):
    """Send push notification via FCM"""
    if not reminder.receiver.fcm_token:
        logger.warning(f"No FCM token for user {reminder.receiver.id}")
        return
    
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title="Task Reminder",
                body=f"{reminder.sender.get_full_name()} reminded you: {reminder.task.title}",
            ),
            data={
                'task_id': str(reminder.task.id),
                'reminder_id': str(reminder.id),
                'type': 'task_reminder',
            },
            token=reminder.receiver.fcm_token,
        )
        response = messaging.send(message)
        logger.info(f"Push notification sent: {response}")
    except Exception as e:
        logger.error(f"Failed to send push notification: {e}")
        raise

def send_sms_reminder(reminder):
    """Send SMS reminder via Twilio"""
    if not reminder.receiver.mobile:
        logger.warning(f"No mobile number for user {reminder.receiver.id}")
        return
    
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Reminder: {reminder.sender.get_full_name()} reminded you to complete: {reminder.task.title}. {reminder.message}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=reminder.receiver.mobile
        )
        logger.info(f"SMS sent: {message.sid}")
    except Exception as e:
        logger.error(f"Failed to send SMS: {e}")
        raise

def send_notification(user, title, message, notification_type='system', related_task=None):
    """Create and send a notification to a user"""
    from .models import Notification
    
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        related_task=related_task
    )
    
    # Also send push notification if user has FCM token
    if hasattr(user, 'fcm_token') and user.fcm_token:
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=message[:200],  # Truncate long messages
                ),
                data={
                    'notification_id': str(notification.id),
                    'type': notification_type,
                },
                token=user.fcm_token,
            )
            messaging.send(message)
        except Exception as e:
            logger.error(f"Failed to send push notification for notification {notification.id}: {e}")
    
    return notification

def send_task_completion_notification(task, user, status):
    """Send notification when a task is completed"""
    if status == 'done':
        title = "Task Completed"
        message = f"{user.get_full_name()} completed: {task.title}"
    else:
        title = "Task Marked as Not Done"
        message = f"{user.get_full_name()} marked as not done: {task.title}"
    
    # Notify task creator
    if task.created_by != user:
        send_notification(
            user=task.created_by,
            title=title,
            message=message,
            notification_type='task_completed',
            related_task=task
        )
    
    # If group task, notify all members
    if task.type == 'group':
        from django.contrib.auth import get_user_model
        User = get_user_model()
        members = User.objects.filter(is_active=True).exclude(id=user.id)
        for member in members:
            send_notification(
                user=member,
                title=f"Task Update: {task.title}",
                message=f"{user.get_full_name()} updated task status to: {status}",
                notification_type='task_completed',
                related_task=task
            )

def send_welcome_email(user, password=None):
    """Send welcome email to new user"""
    subject = "Welcome to Collaborative Todo Application"
    message = render_to_string('notifications/welcome_email.html', {
        'user_name': user.get_full_name(),
        'email': user.email,
        'password': password if password else 'your password (set during registration)',
        'login_url': f"{settings.BASE_URL}/login/",
    })
    
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.content_subtype = "html"
    email.send()
