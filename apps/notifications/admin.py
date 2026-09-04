from django.contrib import admin
from .models import Reminder, Notification

class ReminderAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'task', 'status', 'created_at', 'sent_at')
    list_filter = ('status', 'created_at', 'sent_at')
    search_fields = ('sender__email', 'receiver__email', 'task__title')
    readonly_fields = ('created_at', 'updated_at')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__email', 'title', 'message')
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(Reminder, ReminderAdmin)
admin.site.register(Notification, NotificationAdmin)
