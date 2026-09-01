from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.tasks.models import Task

User = get_user_model()

class Reminder(models.Model):
    REMINDER_TYPES = [
        ('email', 'Email'),
        ('push', 'Push Notification'),
        ('sms', 'SMS'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_reminders')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reminders')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='reminders')
    message = models.TextField()
    reminder_type = models.CharField(max_length=10, choices=REMINDER_TYPES, default='email')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reminders'
        indexes = [
            models.Index(fields=['sender', 'receiver']),
            models.Index(fields=['task']),
            models.Index(fields=['status']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.email} -> {self.receiver.email}: {self.task.title}"
    
    def mark_sent(self):
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    def mark_failed(self):
        self.status = 'failed'
        self.save()

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('task_assigned', 'Task Assigned'),
        ('task_completed', 'Task Completed'),
        ('reminder', 'Reminder'),
        ('system', 'System'),
        ('group_update', 'Group Update'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    related_task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications'
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email}: {self.title}"
    
    def mark_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
    
    def mark_unread(self):
        self.is_read = False
        self.read_at = None
        self.save()
