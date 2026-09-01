from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Task(models.Model):
    TASK_TYPES = [
        ('group', 'Group Task'),
        ('personal', 'Personal Task'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=10, choices=TASK_TYPES, default='personal')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    assigned_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tasks'
        indexes = [
            models.Index(fields=['type', 'assigned_date']),
            models.Index(fields=['created_by']),
        ]
        ordering = ['-assigned_date']
    
    def __str__(self):
        return f"{self.title} ({self.type})"

class TaskStatus(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('not_done', 'Not Done'),
        ('skipped', 'Skipped'),
    ]
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='statuses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_statuses')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'task_statuses'
        unique_together = ['task', 'user']
        indexes = [
            models.Index(fields=['task', 'user']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.task.title}: {self.status}"
    
    def mark_done(self):
        self.status = 'done'
        self.completed_at = timezone.now()
        self.save()
    
    def mark_not_done(self):
        self.status = 'not_done'
        self.completed_at = None
        self.save()
