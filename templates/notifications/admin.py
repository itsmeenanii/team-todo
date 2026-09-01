from django.contrib import admin
from .models import Reminder, Notification

class ReminderAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'task', 'status', 'created_at', 'sent_at')
    list_filter = ('status', 'created_at', 'sent_at')
    search_fields = ('sender__email', 'receiver__email', 'task__title')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Reminder Information', {
            'fields': ('sender', 'receiver', 'task', 'message', 'reminder_type')
        }),
        ('Status', {
            'fields': ('status', 'sent_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__email', 'title', 'message')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Notification Information', {
            'fields': ('user', 'title', 'message', 'notification_type', 'related_task')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(Reminder, ReminderAdmin)
admin.site.register(Notification, NotificationAdmin)
