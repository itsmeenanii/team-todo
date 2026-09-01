from django.contrib import admin
from .models import Task, TaskStatus

class TaskStatusInline(admin.TabularInline):
    model = TaskStatus
    extra = 0
    fields = ('user', 'status', 'completed_at', 'notes')
    readonly_fields = ('created_at', 'updated_at')

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'created_by', 'assigned_date', 'is_active', 'created_at')
    list_filter = ('type', 'is_active', 'assigned_date', 'created_at')
    search_fields = ('title', 'description', 'created_by__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [TaskStatusInline]
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description', 'type', 'created_by', 'assigned_date')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class TaskStatusAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'status', 'completed_at', 'created_at')
    list_filter = ('status', 'created_at', 'completed_at')
    search_fields = ('task__title', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)
    fieldsets = (
        ('Task Status', {
            'fields': ('task', 'user', 'status', 'completed_at', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(Task, TaskAdmin)
admin.site.register(TaskStatus, TaskStatusAdmin)
